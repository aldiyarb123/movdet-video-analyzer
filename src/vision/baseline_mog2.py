"""Classical baseline (B0): MOG2 background subtraction + centroid tracking.

This is the comparison method for the evaluation (docs/09-verification-plan.md).
It has no class labels and no appearance model, by design.

Usage:
    python src/vision/baseline_mog2.py video.mp4 --out out/tracks.json
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

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


def is_moving(track: Track, min_displacement_px: float = 25.0) -> bool:
    """Motion criterion: the track travelled at least `min_displacement_px`."""
    return track_displacement(track) >= min_displacement_px


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
) -> dict:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=history, varThreshold=var_threshold, detectShadows=detect_shadows
    )
    tracker = CentroidTracker(max_distance=max_distance)
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        mask = subtractor.apply(frame)
        tracker.update(frame_idx, detect_boxes(mask, min_area))
        frame_idx += 1
    cap.release()

    tracks = []
    for t in tracker.all_tracks():
        tracks.append(
            {
                "id": t.id,
                "first_frame": t.frames[0],
                "last_frame": t.frames[-1],
                "n_detections": len(t.frames),
                "displacement_px": round(track_displacement(t), 2),
                "moving": is_moving(t, min_displacement_px),
                "boxes": [list(b) for b in t.boxes],
                "frames": t.frames,
            }
        )
    return {"video": str(video_path), "fps": fps, "frames": frame_idx, "tracks": tracks}


def main() -> None:
    parser = argparse.ArgumentParser(description="MOG2 baseline for moving-object analysis")
    parser.add_argument("video")
    parser.add_argument("--out", default="out/tracks.json")
    parser.add_argument("--min-area", type=int, default=400)
    parser.add_argument("--min-displacement", type=float, default=25.0)
    args = parser.parse_args()

    result = run(args.video, min_area=args.min_area, min_displacement_px=args.min_displacement)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    moving = sum(1 for t in result["tracks"] if t["moving"])
    print(f"{result['frames']} frames, {len(result['tracks'])} tracks, {moving} moving -> {out}")


if __name__ == "__main__":
    main()
