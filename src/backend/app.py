"""FastAPI application: jobs, results and exports (FR-01..03, FR-11, NFR-08).

Run from the repository root:
    uvicorn src.backend.app:app --reload          # stub analysis (default)
    MOVDET_PROCESSOR=pipeline uvicorn src.backend.app:app
"""
from __future__ import annotations

import asyncio
import json
import re
import tempfile
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import ValidationError

from src.reporting.export import TrackReport, build_report, export_csv_report

from .config import ALLOWED_CONTENT_TYPES, ALLOWED_EXTENSIONS, Settings
from .jobs import JobManager, video_metadata
from .schemas import TERMINAL, AnalysisSettings, Health, Job, JobList, JobStatus, TracksResponse

CHUNK = 1024 * 1024


def safe_filename(name: str) -> str:
    """NFR-08: keep only the base name and safe characters."""
    name = unicodedata.normalize("NFKD", Path(name or "").name).encode("ascii", "ignore").decode()
    stem, ext = Path(name).stem, Path(name).suffix.lower()
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")[:80] or "video"
    return f"{stem}{ext}"


def parse_settings(raw: str | None) -> AnalysisSettings:
    if not raw:
        return AnalysisSettings()
    try:
        return AnalysisSettings.model_validate(json.loads(raw))
    except json.JSONDecodeError:
        raise HTTPException(422, "Settings must be valid JSON.")
    except ValidationError as exc:
        problems = "; ".join(f"{'.'.join(map(str, e['loc'])) or 'settings'}: {e['msg']}" for e in exc.errors())
        raise HTTPException(422, f"Invalid settings: {problems}")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    manager = JobManager(settings.data_dir, settings.processor)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        manager.shutdown()

    app = FastAPI(
        title="MotionScope API",
        version="0.1.0",
        description="Upload a video, run moving-object analysis as a job, read tracks and exports.",
        lifespan=lifespan,
    )
    app.state.manager = manager
    app.state.settings = settings

    def get_job(job_id: str) -> Job:
        job = manager.get(job_id)
        if job is None:
            raise HTTPException(404, "Job not found.")
        return job

    def read_result(job_id: str) -> dict:
        job = get_job(job_id)
        if job.status != JobStatus.done:
            raise HTTPException(409, f"Results are not ready: job is {job.status.value}.")
        return json.loads((manager.output_dir(job_id) / "tracks.json").read_text())

    @app.get("/api/health", response_model=Health, tags=["system"])
    def health() -> Health:
        return Health(processor=settings.processor)

    @app.post("/api/jobs", response_model=Job, status_code=201, tags=["jobs"],
              responses={413: {"description": "File too large"}, 415: {"description": "Unsupported file type"},
                         422: {"description": "Invalid settings or unreadable video"}})
    async def create_job(video: UploadFile = File(...), settings_json: str | None = Form(None, alias="settings")) -> Job:
        """FR-01, FR-02: upload a video with settings; returns the queued job."""
        filename = safe_filename(video.filename or "")
        if Path(filename).suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(415, f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}.")
        content_type = (video.content_type or "").lower()
        if content_type and not content_type.startswith(ALLOWED_CONTENT_TYPES):
            raise HTTPException(415, f"Unsupported content type: {content_type}.")
        analysis = parse_settings(settings_json)

        tmp_dir = settings.data_dir / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=tmp_dir, suffix=Path(filename).suffix, delete=False) as tmp:
            tmp_path = Path(tmp.name)
            size = 0
            try:
                while chunk := await video.read(CHUNK):
                    size += len(chunk)
                    if size > settings.max_upload_bytes:
                        raise HTTPException(413, f"File is larger than {settings.max_upload_mb} MB.")
                    tmp.write(chunk)
            except HTTPException:
                tmp.close()
                tmp_path.unlink(missing_ok=True)
                raise
        if size == 0:
            tmp_path.unlink(missing_ok=True)
            raise HTTPException(400, "The file is empty.")
        try:
            await asyncio.to_thread(video_metadata, tmp_path)
        except ValueError as exc:
            tmp_path.unlink(missing_ok=True)
            raise HTTPException(422, str(exc))
        return manager.create(tmp_path, filename, analysis)

    @app.get("/api/jobs", response_model=JobList, tags=["jobs"])
    def list_jobs() -> JobList:
        """History, newest first."""
        return JobList(jobs=manager.list())

    @app.get("/api/jobs/{job_id}", response_model=Job, tags=["jobs"])
    def job_status(job_id: str) -> Job:
        """FR-03: status and progress (0..1)."""
        return get_job(job_id)

    @app.get("/api/jobs/{job_id}/events", tags=["jobs"], response_class=StreamingResponse)
    async def job_events(job_id: str, request: Request) -> StreamingResponse:
        """FR-03: Server-Sent Events with the job on every change, until it finishes."""
        get_job(job_id)

        async def stream():
            last = None
            while not await request.is_disconnected():
                job = manager.get(job_id)
                if job is None:
                    break
                data = job.model_dump_json()
                if data != last:
                    yield f"event: job\ndata: {data}\n\n"
                    last = data
                if job.status in TERMINAL:
                    break
                await asyncio.sleep(0.5)

        return StreamingResponse(stream(), media_type="text/event-stream")

    @app.post("/api/jobs/{job_id}/cancel", response_model=Job, tags=["jobs"])
    def cancel_job(job_id: str) -> Job:
        get_job(job_id)
        return manager.cancel(job_id)

    @app.delete("/api/jobs/{job_id}", status_code=204, tags=["jobs"])
    def delete_job(job_id: str) -> None:
        get_job(job_id)
        try:
            manager.delete(job_id)
        except RuntimeError as exc:
            raise HTTPException(409, str(exc))

    @app.get("/api/jobs/{job_id}/video", tags=["results"], response_class=FileResponse)
    def job_video(job_id: str) -> FileResponse:
        get_job(job_id)
        return FileResponse(manager.video_path(job_id))

    @app.get("/api/jobs/{job_id}/tracks", response_model=TracksResponse, response_model_by_alias=True, tags=["results"])
    def job_tracks(job_id: str, moving_only: bool = False) -> TracksResponse:
        """Tracks with boxes per frame ([frame, x, y, w, h]) for the overlay (FR-09)."""
        result = read_result(job_id)
        tracks = []
        for t in result.get("tracks", []):
            if moving_only and not t.get("moving"):
                continue
            tracks.append({
                "id": t["id"], "class": t.get("class", "object"),
                "first_frame": t["first_frame"], "last_frame": t["last_frame"],
                "moving": t.get("moving"), "displacement_px": t.get("displacement_px"),
                "boxes": [[f, *map(int, b)] for f, b in zip(t["frames"], t["boxes"])],
            })
        return TracksResponse(job_id=job_id, fps=result.get("fps", 0.0), frames=result.get("frames", 0),
                              width=result.get("width", 0), height=result.get("height", 0), tracks=tracks)

    def report_tracks(job_id: str) -> list[TrackReport]:
        result = read_result(job_id)
        fps = result.get("fps") or 1.0
        return [TrackReport(track_id=str(t["id"]), class_name=t.get("class", "object"),
                            first_time_s=round(t["first_frame"] / fps, 3), last_time_s=round(t["last_frame"] / fps, 3),
                            moving=bool(t.get("moving"))) for t in result.get("tracks", [])]

    @app.get("/api/jobs/{job_id}/report.json", tags=["results"])
    def report_json(job_id: str) -> dict:
        """FR-11: report in the schema docs/schemas/export-report.schema.json."""
        return build_report(job_id, report_tracks(job_id))

    @app.get("/api/jobs/{job_id}/report.csv", tags=["results"], response_class=FileResponse)
    def report_csv(job_id: str) -> FileResponse:
        path = manager.output_dir(job_id) / "report.csv"
        export_csv_report(path, job_id, report_tracks(job_id))
        return FileResponse(path, media_type="text/csv", filename=f"motionscope-{job_id}.csv")

    @app.get("/api/jobs/{job_id}/tracks/{track_id}/crop", tags=["results"], response_class=FileResponse)
    def track_crop(job_id: str, track_id: int, index: int = 0) -> FileResponse:
        """FR-07: one of the saved crops of a moving track."""
        read_result(job_id)
        crops = sorted((manager.output_dir(job_id) / "crops" / f"track_{track_id}").glob("*.jpg"))
        if not 0 <= index < len(crops):
            raise HTTPException(404, "No crop for this track.")
        return FileResponse(crops[index], media_type="image/jpeg")

    @app.get("/api/jobs/{job_id}/tracks/{track_id}/clip", tags=["results"], response_class=FileResponse)
    def track_clip(job_id: str, track_id: int) -> FileResponse:
        """FR-08: the saved clip of a moving track."""
        read_result(job_id)
        clip = manager.output_dir(job_id) / "clips" / f"track_{track_id}.mp4"
        if not clip.is_file():
            raise HTTPException(404, "No clip for this track.")
        return FileResponse(clip, media_type="video/mp4")

    return app


app = create_app()
