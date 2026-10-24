"""Full analysis pipeline: detect + track -> motion filter -> extractor -> report.

Called by the API worker (`MOVDET_PROCESSOR=pipeline`, src/backend/jobs.py) and usable
from the command line:
    python -m src.vision.pipeline video.mp4 --out out/job1 [--backend mog2]

`settings` uses the API format (src/backend/schemas.py):
    {"classes": [...], "confidence": 0.35, "tracker": "bytetrack", "backend": "yolo",
     "motion": {"min_displacement_px": 25, "window_frames": 15},
     "extraction": {"max_crops_per_track": 5, "clip_padding_seconds": 1.0,
                    "save_crops": true, "save_clips": true}}   # extraction is optional
"""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from typing import Any, Callable

from src.reporting.export import TrackReport, export_csv_report, export_json_report
from src.vision.extractor import extract
from src.vision.motion_filter import classify_tracks

DETECT_SHARE = 0.8  # share of the progress bar used by detection + tracking


def _scaled(progress: Callable[[float], None] | None, lo: float, hi: float):
    if progress is None:
        return None
    return lambda p: progress(lo + (hi - lo) * p)


def detect_and_track(video: Path, settings: dict, progress=None, should_stop=None) -> dict[str, Any]:
    backend = settings.get("backend", "yolo")
    if backend == "mog2":
        from src.vision.baseline_mog2 import run

        kwargs = {"progress": progress, "should_stop": should_stop}
        accepted = inspect.signature(run).parameters
        result = run(video, **{k: v for k, v in kwargs.items() if k in accepted and v is not None})
        for t in result["tracks"]:
            t.setdefault("class", "object")
        return result
    if backend == "yolo":
        from src.vision.detector_tracker import track_video

        return track_video(
            video, model=settings.get("model", "yolo11n.pt"), tracker=settings.get("tracker", "bytetrack"),
            confidence=settings.get("confidence", 0.35), classes=settings.get("classes"),
            progress=progress, should_stop=should_stop,
        )
    raise ValueError(f"Unknown backend: {backend}")


def run_pipeline(
    video: str | Path,
    out_dir: str | Path,
    settings: dict | None = None,
    progress: Callable[[float], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    video, out_dir = Path(video), Path(out_dir)
    settings = settings or {}
    motion = settings.get("motion", {})
    extraction = settings.get("extraction", {})
    out_dir.mkdir(parents=True, exist_ok=True)

    result = detect_and_track(video, settings, _scaled(progress, 0.0, DETECT_SHARE), should_stop)
    if should_stop is not None and should_stop():
        return result
    tracks = classify_tracks(result["tracks"], motion.get("min_displacement_px", 25.0), motion.get("window_frames", 15))
    tracks = extract(
        video, tracks, out_dir,
        max_crops_per_track=extraction.get("max_crops_per_track", 5),
        clip_padding_seconds=extraction.get("clip_padding_seconds", 1.0),
        save_crops=extraction.get("save_crops", True),
        save_clips=extraction.get("save_clips", True),
        progress=_scaled(progress, DETECT_SHARE, 1.0), should_stop=should_stop,
    )
    result = {**result, "tracks": tracks, "settings": settings}

    job_id = job_id or out_dir.parent.name or "job"
    fps = result.get("fps") or 1.0
    reports = [TrackReport(track_id=str(t["id"]), class_name=t.get("class", "object"),
                           first_time_s=round(t["first_frame"] / fps, 3), last_time_s=round(t["last_frame"] / fps, 3),
                           moving=bool(t["moving"])) for t in tracks]
    export_json_report(out_dir / "report.json", job_id, reports)
    export_csv_report(out_dir / "report.csv", job_id, reports)
    return result


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Run the full MotionScope pipeline on one video")
    ap.add_argument("video")
    ap.add_argument("--out", default="out/pipeline")
    ap.add_argument("--backend", choices=["yolo", "mog2"], default="yolo")
    ap.add_argument("--classes", nargs="*", default=None)
    ap.add_argument("--tracker", choices=["bytetrack", "botsort"], default="bytetrack")
    ap.add_argument("--min-displacement", type=float, default=25.0)
    ap.add_argument("--window-frames", type=int, default=15)
    args = ap.parse_args(argv)
    settings = {"backend": args.backend, "classes": args.classes, "tracker": args.tracker,
                "motion": {"min_displacement_px": args.min_displacement, "window_frames": args.window_frames}}
    result = run_pipeline(args.video, args.out, settings, job_id=Path(args.out).name)
    (Path(args.out) / "tracks.json").write_text(json.dumps(result, indent=2))
    moving = [t for t in result["tracks"] if t["moving"]]
    print(f"{result['frames']} frames, {len(result['tracks'])} tracks, {len(moving)} moving, "
          f"{sum(len(t['crops']) for t in moving)} crops, {sum(1 for t in moving if t['clip'])} clips -> {args.out}")


if __name__ == "__main__":
    main()
