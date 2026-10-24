"""Job storage and execution (FR-03).

Each job lives in `<data_dir>/jobs/<id>/`:
    job.json            job metadata (status, progress, settings)
    input/<file>        uploaded video
    output/tracks.json  result written by the processor
    output/crops/track_<id>/*.jpg, output/clips/track_<id>.mp4   (written by the extractor)

ADR-0002 allows an in-process worker for the prototype: jobs run one at a time in a
background thread behind the `JobManager` interface, which can later be replaced by
a Redis/RQ worker without changing the API.
"""
from __future__ import annotations

import json
import shutil
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import cv2

from .schemas import TERMINAL, AnalysisSettings, Job, JobStatus, JobSummary

ProgressFn = Callable[[float], None]
StopFn = Callable[[], bool]
# processor(video_path, output_dir, settings_dict, progress, should_stop) -> result dict
Processor = Callable[[Path, Path, dict, ProgressFn, StopFn], dict]


class JobCancelled(Exception):
    """Raised by a processor that noticed `should_stop()`."""


def video_metadata(path: Path) -> dict:
    """Open a video and read one frame. Raises ValueError if it cannot be decoded."""
    cap = cv2.VideoCapture(str(path))
    try:
        ok, frame = cap.read() if cap.isOpened() else (False, None)
        if not ok or frame is None:
            raise ValueError("The file is not a readable video.")
        return {
            "fps": float(cap.get(cv2.CAP_PROP_FPS) or 0.0),
            "frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0),
            "width": int(frame.shape[1]),
            "height": int(frame.shape[0]),
        }
    finally:
        cap.release()


def stub_processor(video: Path, out_dir: Path, settings: dict, progress: ProgressFn, should_stop: StopFn) -> dict:
    """Fake analysis: reports progress and returns no tracks. Used until the pipeline is wired."""
    meta = video_metadata(video)
    for step in range(1, 6):
        if should_stop():
            raise JobCancelled()
        time.sleep(0.02)
        progress(step / 5)
    return {**meta, "tracks": []}


def pipeline_processor(video: Path, out_dir: Path, settings: dict, progress: ProgressFn, should_stop: StopFn) -> dict:
    """Real analysis: detector + tracker + motion filter + extractor (DIP-15, DIP-16)."""
    try:
        from src.vision.pipeline import run_pipeline
    except ImportError as exc:  # pragma: no cover - depends on which tasks are merged
        raise RuntimeError("Pipeline is not installed yet (src/vision/pipeline.py, DIP-16).") from exc
    return run_pipeline(video, out_dir, settings, progress=progress, should_stop=should_stop)


PROCESSORS: dict[str, Processor] = {"stub": stub_processor, "pipeline": pipeline_processor}


def _now() -> datetime:
    return datetime.now(timezone.utc)


class JobManager:
    def __init__(self, data_dir: Path, processor: Processor | str = "stub", workers: int = 1) -> None:
        self.root = Path(data_dir) / "jobs"
        self.root.mkdir(parents=True, exist_ok=True)
        self.processor = PROCESSORS[processor] if isinstance(processor, str) else processor
        self._jobs: dict[str, Job] = {}
        self._stop: dict[str, threading.Event] = {}
        self._lock = threading.RLock()
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="job")
        self._load()

    # ---- persistence -------------------------------------------------------
    def job_dir(self, job_id: str) -> Path:
        return self.root / job_id

    def output_dir(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "output"

    def _save(self, job: Job) -> None:
        path = self.job_dir(job.id) / "job.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(job.model_dump_json(indent=2))
        tmp.replace(path)

    def _load(self) -> None:
        for path in sorted(self.root.glob("*/job.json")):
            try:
                job = Job.model_validate_json(path.read_text())
            except ValueError:
                continue
            if job.status not in TERMINAL:  # the server stopped while the job was waiting/running
                job = job.model_copy(update={"status": JobStatus.failed, "error": "Interrupted by server restart.", "updated_at": _now()})
                self._save(job)
            self._jobs[job.id] = job

    def _update(self, job_id: str, **changes) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            if "progress" in changes:  # FR-03: progress never decreases
                changes["progress"] = max(job.progress, min(float(changes["progress"]), 1.0))
            job = job.model_copy(update={**changes, "updated_at": _now()})
            self._jobs[job_id] = job
            self._save(job)
            return job

    # ---- public API --------------------------------------------------------
    def create(self, upload: Path, filename: str, settings: AnalysisSettings) -> Job:
        job_id = uuid.uuid4().hex[:12]
        input_dir = self.job_dir(job_id) / "input"
        input_dir.mkdir(parents=True)
        video = input_dir / filename
        shutil.move(str(upload), video)
        now = _now()
        job = Job(id=job_id, status=JobStatus.queued, filename=filename, size_bytes=video.stat().st_size,
                  created_at=now, updated_at=now, settings=settings)
        with self._lock:
            self._jobs[job_id] = job
            self._stop[job_id] = threading.Event()
            self._save(job)
        self._pool.submit(self._run, job_id)
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self) -> list[Job]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    def video_path(self, job_id: str) -> Path:
        job = self._jobs[job_id]
        return self.job_dir(job_id) / "input" / job.filename

    def cancel(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            if job.status in TERMINAL:
                return job
            self._stop.setdefault(job_id, threading.Event()).set()
            if job.status == JobStatus.queued:
                return self._update(job_id, status=JobStatus.cancelled)
            return job  # running: the worker marks it cancelled when the processor stops

    def delete(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.status == JobStatus.running:
                raise RuntimeError("The job is running. Cancel it first.")
            self._jobs.pop(job_id)
            self._stop.pop(job_id, None)
        shutil.rmtree(self.job_dir(job_id), ignore_errors=True)

    def wait(self, job_id: str, timeout: float = 30.0) -> Job:
        """Block until the job reaches a final state (used by tests and scripts)."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.get(job_id)
            if job is None or job.status in TERMINAL:
                return job
            time.sleep(0.02)
        raise TimeoutError(job_id)

    def shutdown(self) -> None:
        for event in self._stop.values():
            event.set()
        self._pool.shutdown(wait=True, cancel_futures=True)

    # ---- worker ------------------------------------------------------------
    def _run(self, job_id: str) -> None:
        stop = self._stop[job_id]
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None or job.status != JobStatus.queued:
                return
            job = self._update(job_id, status=JobStatus.running)
        out_dir = self.output_dir(job_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = self.processor(
                self.video_path(job_id), out_dir, job.settings.model_dump(),
                lambda p: self._update(job_id, progress=p), stop.is_set,
            )
            if stop.is_set():
                raise JobCancelled()
            (out_dir / "tracks.json").write_text(json.dumps(result, indent=2))
            tracks = result.get("tracks", [])
            summary = JobSummary(frames=int(result.get("frames", 0)), fps=float(result.get("fps", 0.0)),
                                 tracks_total=len(tracks), tracks_moving=sum(1 for t in tracks if t.get("moving")))
            self._update(job_id, status=JobStatus.done, progress=1.0, summary=summary)
        except JobCancelled:
            self._update(job_id, status=JobStatus.cancelled)
        except Exception as exc:  # NFR-05: a failing job ends in "failed" with a reason; the service keeps running
            self._update(job_id, status=JobStatus.failed, error=f"{type(exc).__name__}: {exc}")
