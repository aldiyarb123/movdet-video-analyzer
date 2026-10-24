"""Detector + tracker integration (DIP-15, ADR-0001): YOLO via Ultralytics with ByteTrack or BoT-SORT.

Produces tracks in the same format as baseline B0 (`baseline_mog2.run`), so the motion
filter, extractor, API and evaluation treat both methods the same way:

    {"video", "method", "fps", "frames", "width", "height", "params",
     "tracks": [{"id", "class", "first_frame", "last_frame", "n_detections",
                 "frames": [...], "boxes": [[x, y, w, h], ...], "confidences": [...]}]}

Install the model dependencies first: `pip install -r requirements-ml.txt`.
Weights (`yolo11n.pt` by default) are downloaded by Ultralytics on first use; after that
analysis runs offline (NFR-03).

Usage (from the repository root):
    python src/vision/detector_tracker.py video.mp4 --out out/tracks.json
    python src/vision/detector_tracker.py video.mp4 --classes person car --tracker botsort
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import cv2

TRACKERS = {"bytetrack": "bytetrack.yaml", "botsort": "botsort.yaml"}
DEFAULT_MODEL = "yolo11n.pt"


@dataclass
class _Acc:
    frames: list[int] = field(default_factory=list)
    boxes: list[list[int]] = field(default_factory=list)
    confidences: list[float] = field(default_factory=list)
    classes: Counter = field(default_factory=Counter)


class TrackAccumulator:
    """Collects per-frame tracker output into whole tracks (pure Python, testable without a model)."""

    def __init__(self) -> None:
        self._tracks: dict[int, _Acc] = {}

    def add(self, frame_idx: int, ids: Sequence[int], xyxy: Sequence[Sequence[float]],
            class_names: Sequence[str], confidences: Sequence[float]) -> None:
        for tid, (x1, y1, x2, y2), name, conf in zip(ids, xyxy, class_names, confidences):
            acc = self._tracks.setdefault(int(tid), _Acc())
            if acc.frames and acc.frames[-1] == frame_idx:
                continue  # one box per track per frame
            acc.frames.append(frame_idx)
            acc.boxes.append([round(x1), round(y1), max(1, round(x2 - x1)), max(1, round(y2 - y1))])
            acc.confidences.append(round(float(conf), 3))
            acc.classes[name] += 1

    def tracks(self, min_detections: int = 1) -> list[dict[str, Any]]:
        out = []
        for tid in sorted(self._tracks):
            acc = self._tracks[tid]
            if len(acc.frames) < min_detections:
                continue
            out.append({
                "id": tid,
                "class": acc.classes.most_common(1)[0][0],  # majority vote over the track
                "first_frame": acc.frames[0],
                "last_frame": acc.frames[-1],
                "n_detections": len(acc.frames),
                "frames": acc.frames,
                "boxes": acc.boxes,
                "confidences": acc.confidences,
            })
        return out


def class_ids(names: dict[int, str], wanted: Iterable[str] | None) -> list[int] | None:
    """Map class names (e.g. "person") to model class indices; unknown names raise ValueError."""
    if not wanted:
        return None
    lookup = {v.lower(): k for k, v in names.items()}
    unknown = [w for w in wanted if w.lower() not in lookup]
    if unknown:
        raise ValueError(f"Unknown classes for this model: {', '.join(unknown)}")
    return sorted({lookup[w.lower()] for w in wanted})


def track_video(
    video_path: str | Path,
    model: str = DEFAULT_MODEL,
    tracker: str = "bytetrack",
    confidence: float = 0.35,
    classes: Sequence[str] | None = None,
    min_detections: int = 3,
    device: str | None = None,
    progress: Callable[[float], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Detect and track objects in a video file. Tracks shorter than `min_detections` are dropped."""
    from ultralytics import YOLO  # imported here so the rest of the project works without ML deps

    if tracker not in TRACKERS:
        raise ValueError(f"tracker must be one of {sorted(TRACKERS)}")
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    cap.release()

    yolo = YOLO(model)
    ids_filter = class_ids(yolo.names, classes)
    acc = TrackAccumulator()
    frame_idx = width = height = 0
    started = time.perf_counter()
    results = yolo.track(
        source=str(video_path), stream=True, persist=True, tracker=TRACKERS[tracker],
        conf=confidence, classes=ids_filter, device=device, verbose=False,
    )
    for r in results:
        if should_stop is not None and should_stop():
            break
        height, width = r.orig_shape
        b = r.boxes
        if b is not None and b.id is not None and len(b):
            acc.add(frame_idx, b.id.int().tolist(), b.xyxy.tolist(),
                    [r.names[int(c)] for c in b.cls.tolist()], b.conf.tolist())
        frame_idx += 1
        if progress is not None and total and frame_idx % 10 == 0:
            progress(min(frame_idx / total, 1.0))
    elapsed = time.perf_counter() - started
    if frame_idx == 0:
        raise ValueError(f"No frames could be decoded from: {video_path}")
    if progress is not None:
        progress(1.0)
    return {
        "video": str(video_path),
        "method": f"yolo+{tracker}",
        "fps": fps,
        "frames": frame_idx,
        "width": int(width),
        "height": int(height),
        "processing_fps": round(frame_idx / elapsed, 2) if elapsed else None,
        "params": {"model": Path(model).name, "tracker": tracker, "confidence": confidence,
                   "classes": list(classes) if classes else None, "min_detections": min_detections},
        "tracks": acc.tracks(min_detections),
    }


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    tracks = result["tracks"]
    lengths = sorted(t["n_detections"] for t in tracks)
    return {
        "video": Path(result["video"]).name,
        "method": result["method"],
        "frames": result["frames"],
        "resolution": f"{result['width']}x{result['height']}",
        "processing_fps": result.get("processing_fps"),
        "tracks": len(tracks),
        "tracks_by_class": dict(Counter(t["class"] for t in tracks)),
        "median_track_length_frames": lengths[len(lengths) // 2] if lengths else 0,
        "params": result["params"],
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="YOLO + ByteTrack/BoT-SORT tracking of a video file")
    ap.add_argument("video")
    ap.add_argument("--out", default="out/tracks.json")
    ap.add_argument("--summary", default=None, help="also write a short summary JSON here")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--tracker", choices=sorted(TRACKERS), default="bytetrack")
    ap.add_argument("--confidence", type=float, default=0.35)
    ap.add_argument("--classes", nargs="*", default=None)
    ap.add_argument("--device", default=None, help="e.g. cpu, 0, mps")
    args = ap.parse_args(argv)

    result = track_video(args.video, args.model, args.tracker, args.confidence, args.classes, device=args.device)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    summary = summarize(result)
    if args.summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary).write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
