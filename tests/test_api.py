"""API tests for the backend skeleton (DIP-14). Acceptance: POST /api/jobs works with the stub."""
from __future__ import annotations

import csv
import io
import json
import time
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.backend.app import create_app, safe_filename
from src.backend.config import Settings
from src.backend.jobs import JobCancelled, JobManager
from src.backend.schemas import AnalysisSettings, JobStatus


@pytest.fixture(scope="module")
def video_bytes(tmp_path_factory) -> bytes:
    path = tmp_path_factory.mktemp("v") / "clip.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (64, 48))
    for i in range(20):
        frame = np.full((48, 64, 3), 80, np.uint8)
        cv2.rectangle(frame, (i * 2, 10), (i * 2 + 10, 20), (255, 255, 255), -1)
        writer.write(frame)
    writer.release()
    return path.read_bytes()


@pytest.fixture()
def client(tmp_path):
    app = create_app(Settings(data_dir=tmp_path, max_upload_mb=1, processor="stub"))
    with TestClient(app) as c:
        yield c


def upload(client, data: bytes, name="clip.avi", settings: dict | None = None, content_type="video/x-msvideo"):
    form = {"settings": json.dumps(settings)} if settings is not None else {}
    return client.post("/api/jobs", files={"video": (name, data, content_type)}, data=form)


def wait_done(client, job_id: str, timeout=10.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = client.get(f"/api/jobs/{job_id}").json()
        if job["status"] in ("done", "failed", "cancelled"):
            return job
        time.sleep(0.02)
    raise TimeoutError


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "processor": "stub"}


def test_create_job_with_stub_runs_to_done(client, video_bytes):
    r = upload(client, video_bytes, settings={"classes": ["person"], "confidence": 0.5})
    assert r.status_code == 201, r.text
    job = r.json()
    assert job["status"] in ("queued", "running", "done") and len(job["id"]) == 12
    assert job["settings"]["classes"] == ["person"] and job["settings"]["confidence"] == 0.5
    done = wait_done(client, job["id"])
    assert done["status"] == "done" and done["progress"] == 1.0
    assert done["summary"] == {"frames": 20, "fps": 10.0, "tracks_total": 0, "tracks_moving": 0}
    assert [j["id"] for j in client.get("/api/jobs").json()["jobs"]] == [job["id"]]


def test_defaults_applied_when_settings_omitted(client, video_bytes):
    job = upload(client, video_bytes).json()
    assert job["settings"] == AnalysisSettings().model_dump()
    assert job["settings"]["tracker"] == "bytetrack" and job["settings"]["motion"]["window_frames"] == 15


@pytest.mark.parametrize("settings, field", [
    ({"confidence": 1.5}, "confidence"),
    ({"tracker": "deepsort"}, "tracker"),
    ({"motion": {"min_displacement_px": -1}}, "motion.min_displacement_px"),
    ({"classes": []}, "classes"),
    ({"unknown": 1}, "unknown"),
])
def test_out_of_range_settings_rejected(client, video_bytes, settings, field):
    r = upload(client, video_bytes, settings=settings)
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str) and field in r.json()["detail"]


def test_settings_must_be_json(client, video_bytes):
    r = client.post("/api/jobs", files={"video": ("a.avi", video_bytes, "video/x-msvideo")}, data={"settings": "{oops"})
    assert r.status_code == 422 and "JSON" in r.json()["detail"]


@pytest.mark.parametrize("name, content_type, code", [
    ("notes.txt", "text/plain", 415),
    ("clip.avi", "text/plain", 415),
    ("clip.exe", "application/octet-stream", 415),
])
def test_unsupported_type_rejected(client, video_bytes, name, content_type, code):
    assert upload(client, video_bytes, name=name, content_type=content_type).status_code == code


def test_fake_video_rejected(client):
    r = upload(client, b"this is not a video", name="fake.mp4", content_type="video/mp4")
    assert r.status_code == 422 and "not a readable video" in r.json()["detail"]


def test_empty_file_rejected(client):
    assert upload(client, b"", name="empty.mp4", content_type="video/mp4").status_code == 400


def test_too_large_file_rejected(client):
    r = upload(client, b"0" * (1024 * 1024 + 1), name="big.mp4", content_type="video/mp4")
    assert r.status_code == 413 and "1 MB" in r.json()["detail"]
    assert not list((client.app.state.settings.data_dir / "tmp").iterdir()), "temp file must be removed"


def test_filename_is_sanitised():
    assert safe_filename("../../etc/pass wd.MP4") == "pass_wd.mp4"
    assert safe_filename("Видео 1.avi") == "1.avi"
    assert safe_filename("....mov") == "video.mov"


def test_unknown_job_is_404(client):
    assert client.get("/api/jobs/nope").status_code == 404
    assert client.get("/api/jobs/nope/tracks").status_code == 404


def test_results_exports_and_delete(client, video_bytes):
    job_id = upload(client, video_bytes).json()["id"]
    wait_done(client, job_id)
    tracks = client.get(f"/api/jobs/{job_id}/tracks").json()
    assert tracks["frames"] == 20 and tracks["tracks"] == [] and tracks["width"] == 64
    report = client.get(f"/api/jobs/{job_id}/report.json").json()
    assert report == {"schema_version": "1.0", "job_id": job_id, "tracks": []}
    r = client.get(f"/api/jobs/{job_id}/report.csv")
    assert r.status_code == 200 and r.text.startswith("job_id,track_id")
    assert client.get(f"/api/jobs/{job_id}/video").content == video_bytes
    assert client.get(f"/api/jobs/{job_id}/tracks/1/crop").status_code == 404
    assert client.delete(f"/api/jobs/{job_id}").status_code == 204
    assert client.get(f"/api/jobs/{job_id}").status_code == 404


def test_events_stream_ends_with_final_state(client, video_bytes):
    job_id = upload(client, video_bytes).json()["id"]
    with client.stream("GET", f"/api/jobs/{job_id}/events") as r:
        assert r.headers["content-type"].startswith("text/event-stream")
        events = [json.loads(line[6:]) for line in r.iter_lines() if line.startswith("data: ")]
    assert events[-1]["status"] == "done"
    progress = [e["progress"] for e in events]
    assert progress == sorted(progress)


# ---- JobManager with fake processors -------------------------------------------------

def fake_result(n_tracks=2):
    return {"fps": 10.0, "frames": 30, "width": 64, "height": 48, "tracks": [
        {"id": i, "class": "person", "first_frame": 0, "last_frame": 9, "moving": i == 1,
         "displacement_px": 40.0, "frames": list(range(10)), "boxes": [[i, 1, 5, 5]] * 10}
        for i in range(1, n_tracks + 1)]}


def make_upload(tmp_path: Path, video_bytes: bytes) -> Path:
    p = tmp_path / f"up-{time.monotonic_ns()}.avi"
    p.write_bytes(video_bytes)
    return p


def test_tracks_endpoint_formats_boxes(tmp_path, video_bytes):
    app = create_app(Settings(data_dir=tmp_path, processor="stub"))
    app.state.manager.processor = lambda v, o, s, progress, stop: fake_result()
    with TestClient(app) as c:
        job_id = upload(c, video_bytes).json()["id"]
        assert wait_done(c, job_id)["summary"]["tracks_moving"] == 1
        body = c.get(f"/api/jobs/{job_id}/tracks").json()
        assert body["tracks"][0]["class"] == "person"
        assert body["tracks"][0]["boxes"][3] == [3, 1, 1, 5, 5]
        assert [t["id"] for t in c.get(f"/api/jobs/{job_id}/tracks?moving_only=true").json()["tracks"]] == [1]
        report = c.get(f"/api/jobs/{job_id}/report.json").json()
        assert report["tracks"][0] == {"track_id": "1", "class": "person", "first_time_s": 0.0, "last_time_s": 0.9, "moving": True}
        rows = list(csv.DictReader(io.StringIO(c.get(f"/api/jobs/{job_id}/report.csv").text)))
        assert len(rows) == 2


def test_failure_is_reported_and_service_keeps_running(tmp_path, video_bytes):
    def boom(*_):
        raise RuntimeError("decoder crashed")

    m = JobManager(tmp_path, boom)
    job = m.wait(m.create(make_upload(tmp_path, video_bytes), "a.avi", AnalysisSettings()).id)
    assert job.status == JobStatus.failed and "decoder crashed" in job.error
    m.processor = lambda *_: fake_result()
    assert m.wait(m.create(make_upload(tmp_path, video_bytes), "b.avi", AnalysisSettings()).id).status == JobStatus.done
    m.shutdown()


def test_cancel_running_job(tmp_path, video_bytes):
    def slow(video, out, settings, progress, should_stop):
        for i in range(500):
            if should_stop():
                raise JobCancelled()
            progress(i / 500)
            time.sleep(0.01)
        return fake_result()

    m = JobManager(tmp_path, slow)
    job = m.create(make_upload(tmp_path, video_bytes), "a.avi", AnalysisSettings())
    while m.get(job.id).status == JobStatus.queued:
        time.sleep(0.01)
    m.cancel(job.id)
    assert m.wait(job.id).status == JobStatus.cancelled
    m.shutdown()


def test_progress_never_decreases(tmp_path, video_bytes):
    def jumpy(video, out, settings, progress, should_stop):
        for p in (0.5, 0.2, 0.7, 0.1):
            progress(p)
        assert m.get(job_ids[0]).progress == 0.7
        return fake_result()

    m = JobManager(tmp_path, jumpy)
    job_ids = []
    job_ids.append(m.create(make_upload(tmp_path, video_bytes), "a.avi", AnalysisSettings()).id)
    assert m.wait(job_ids[0]).status == JobStatus.done
    m.shutdown()


def test_jobs_survive_restart_and_interrupted_jobs_fail(tmp_path, video_bytes):
    m = JobManager(tmp_path, lambda *_: fake_result())
    done_id = m.create(make_upload(tmp_path, video_bytes), "a.avi", AnalysisSettings()).id
    m.wait(done_id)
    m.shutdown()
    # simulate a job left "running" by a crash
    stuck = tmp_path / "jobs" / "stuck000000"
    stuck.mkdir()
    data = json.loads((tmp_path / "jobs" / done_id / "job.json").read_text())
    data.update(id="stuck000000", status="running")
    (stuck / "job.json").write_text(json.dumps(data))

    m2 = JobManager(tmp_path, "stub")
    assert m2.get(done_id).status == JobStatus.done
    assert m2.get("stuck000000").status == JobStatus.failed
    m2.shutdown()
