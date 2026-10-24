"""Classical baseline (B0): MOG2 background subtraction + centroid tracking.

This is the comparison method for the evaluation (docs/09-verification-plan.md).
It has no class labels and no appearance model, by design.

Usage:
    python src/vision/baseline_mog2.py video.mp4 --out out/tracks.json --window-frames 15
    python src/vision/benchmark_baseline.py video.mp4 --out docs/evidence/dip-12
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

Box = tuple[int, int, int, int]  # x, y, w, h


@dataclass
class Track:
    id: int
    frames: list[int] = field(default_factory=list)
    boxes: list[Box] = field(default_factory=list)
    missed: int = 0

    @property
    def last_center(self) -> tuple[float, float]:
        x, y, w, h = self.boxes[-1]
        return x + w / 2, y + h / 2

    def add(self, frame_idx: int, box: Box) -> None:
        self.frames.append(frame_idx)
        self.boxes.append(box)
        self.missed = 0


def box_center(box: Box) -> tuple[float, float]:
    x, y, w, h = box
    return x + w / 2, y + h / 2


def track_displacement(track: Track) -> float:
    """Straight-line distance between first and last center, in pixels."""
    if len(track.boxes) < 2:
        return 0.0
    (x0, y0), (x1, y1) = box_center(track.boxes[0]), box_center(track.boxes[-1])
    return math.hypot(x1 - x0, y1 - y0)


def window_displacement(track: Track, window_frames: int) -> float:
    """Largest center displacement between two observations at most `window_frames` apart.

    This is the ADR-0003 criterion: an object is moving if, inside some window of
    `window_frames` frames, its center travels at least the threshold. A track that is
    shorter than the window is measured from its first to its last observation.
    """
    if window_frames < 1:
        raise ValueError("window_frames must be >= 1")
    if len(track.boxes) < 2:
        return 0.0
    centers = [box_center(b) for b in track.boxes]
    best = 0.0
    j = 0
    for i, start in enumerate(track.frames):
        j = max(j, i)
        while j + 1 < len(track.frames) and track.frames[j + 1] - start <= window_frames:
            j += 1
        (x0, y0), (x1, y1) = centers[i], centers[j]
        best = max(best, math.hypot(x1 - x0, y1 - y0))
    return best


def is_moving(
    track: Track, min_displacement_px: float = 25.0, window_frames: int | None = None
) -> bool:
    """Motion criterion (ADR-0003).

    With `window_frames=None` the whole track is used (first vs last center); otherwise
    the displacement must happen within `window_frames` frames, so slow drift is ignored.
    """
    if window_frames is None:
        return track_displacement(track) >= min_displacement_px
    return window_displacement(track, window_frames) >= min_displacement_px


class CentroidTracker:
    """Greedy nearest-centroid tracker (the baseline's weak tracker)."""

    def __init__(self, max_distance: float = 60.0, max_missed: int = 15) -> None:
        self.max_distance = max_distance
        self.max_missed = max_missed
        self.active: list[Track] = []
        self.finished: list[Track] = []
        self._next_id = 1

    def update(self, frame_idx: int, boxes: list[Box]) -> None:
        unmatched = set(range(len(boxes)))
        pairs = []
        for t_i, track in enumerate(self.active):
            tx, ty = track.last_center
            for b_i, box in enumerate(boxes):
                bx, by = box_center(box)
                dist = math.hypot(bx - tx, by - ty)
                if dist <= self.max_distance:
                    pairs.append((dist, t_i, b_i))
        pairs.sort()
        used_tracks: set[int] = set()
        for _, t_i, b_i in pairs:
            if t_i in used_tracks or b_i not in unmatched:
                continue
            self.active[t_i].add(frame_idx, boxes[b_i])
            used_tracks.add(t_i)
            unmatched.discard(b_i)

        still_active = []
        for t_i, track in enumerate(self.active):
            if t_i not in used_tracks:
                track.missed += 1
            if track.missed > self.max_missed:
                self.finished.append(track)
            else:
                still_active.append(track)
        self.active = still_active

        for b_i in sorted(unmatched):
            track = Track(id=self._next_id)
            self._next_id += 1
            track.add(frame_idx, boxes[b_i])
            self.active.append(track)

    def all_tracks(self) -> list[Track]:
        return sorted(self.finished + self.active, key=lambda t: t.id)


def detect_boxes(mask: np.ndarray, min_area: int = 400) -> list[Box]:
    """Turn a foreground mask into bounding boxes."""
    _, binary = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)  # drop shadow pixels (127)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    binary = cv2.dilate(binary, kernel, iterations=2)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        if cv2.contourArea(contour) >= min_area:
            x, y, w, h = cv2.boundingRect(contour)
            boxes.append((x, y, w, h))
    return boxes


def run(
    video_path: str | Path,
    history: int = 500,
    var_threshold: float = 16.0,
    detect_shadows: bool = True,
    min_area: int = 400,
    max_distance: float = 60.0,
    min_displacement_px: float = 25.0,
    window_frames: int | None = 15,
    max_missed: int = 15,
    resize_height: int | None = None,
    progress: Callable[[float], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> dict:
    """Run baseline B0 on a video file and return tracks as a JSON-ready dict.

    `resize_height` scales frames (keeping aspect ratio) before processing; boxes are
    reported in the processed resolution. `progress` receives a value in [0, 1].
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=history, varThreshold=var_threshold, detectShadows=detect_shadows
    )
    tracker = CentroidTracker(max_distance=max_distance, max_missed=max_missed)
    frame_idx = 0
    width = height = 0
    while True:
        if should_stop is not None and should_stop():
            break
        ok, frame = cap.read()
        if not ok:
            break
        if resize_height and frame.shape[0] != resize_height:
            scale = resize_height / frame.shape[0]
            frame = cv2.resize(frame, (round(frame.shape[1] * scale), resize_height))
        height, width = frame.shape[:2]
        mask = subtractor.apply(frame)
        tracker.update(frame_idx, detect_boxes(mask, min_area))
        frame_idx += 1
        if progress is not None and total and frame_idx % 25 == 0:
            progress(min(frame_idx / total, 1.0))
    cap.release()
    if frame_idx == 0:
        raise ValueError(f"No frames could be decoded from: {video_path}")
    if progress is not None:
        progress(1.0)

    tracks = []
    for t in tracker.all_tracks():
        tracks.append(
            {
                "id": t.id,
                "first_frame": t.frames[0],
                "last_frame": t.frames[-1],
                "n_detections": len(t.frames),
                "class": "object",
                "displacement_px": round(track_displacement(t), 2),
                "window_displacement_px": round(
                    window_displacement(t, window_frames) if window_frames else track_displacement(t), 2
                ),
                "moving": is_moving(t, min_displacement_px, window_frames),
                "boxes": [list(b) for b in t.boxes],
                "frames": t.frames,
            }
        )
    return {
        "video": str(video_path),
        "method": "baseline-b0-mog2",
        "fps": fps,
        "frames": frame_idx,
        "width": width,
        "height": height,
        "params": {
            "history": history,
            "var_threshold": var_threshold,
            "detect_shadows": detect_shadows,
            "min_area": min_area,
            "max_distance": max_distance,
            "max_missed": max_missed,
            "min_displacement_px": min_displacement_px,
            "window_frames": window_frames,
        },
        "tracks": tracks,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="MOG2 baseline for moving-object analysis")
    parser.add_argument("video")
    parser.add_argument("--out", default="out/tracks.json")
    parser.add_argument("--min-area", type=int, default=400)
    parser.add_argument("--min-displacement", type=float, default=25.0)
    parser.add_argument("--window-frames", type=int, default=15, help="0 = whole track")
    parser.add_argument("--history", type=int, default=500)
    parser.add_argument("--var-threshold", type=float, default=16.0)
    parser.add_argument("--max-distance", type=float, default=60.0)
    parser.add_argument("--resize-height", type=int, default=None)
    args = parser.parse_args(argv)

    result = run(
        args.video,
        history=args.history,
        var_threshold=args.var_threshold,
        min_area=args.min_area,
        max_distance=args.max_distance,
        min_displacement_px=args.min_displacement,
        window_frames=args.window_frames or None,
        resize_height=args.resize_height,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    moving = sum(1 for t in result["tracks"] if t["moving"])
    print(f"{result['frames']} frames, {len(result['tracks'])} tracks, {moving} moving -> {out}")


if __name__ == "__main__":
    main()
