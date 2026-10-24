"""Motion filter (FR-06, ADR-0003): mark each track as moving or stationary.

A track is *moving* if its box centre travels at least `min_displacement_px` between two
observations that are at most `window_frames` frames apart. Works on any track in the
common format (`frames` + `boxes` as [x, y, w, h]) from YOLO tracking or baseline B0.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Sequence


def centre(box: Sequence[float]) -> tuple[float, float]:
    x, y, w, h = box[:4]
    return x + w / 2, y + h / 2


def window_displacement(frames: Sequence[int], boxes: Sequence[Sequence[float]], window_frames: int) -> float:
    """Largest centre displacement between two observations at most `window_frames` apart."""
    if window_frames < 1:
        raise ValueError("window_frames must be >= 1")
    if len(frames) != len(boxes):
        raise ValueError("frames and boxes must have the same length")
    if len(frames) < 2:
        return 0.0
    centres = [centre(b) for b in boxes]
    best, j = 0.0, 0
    for i, start in enumerate(frames):
        j = max(j, i)
        while j + 1 < len(frames) and frames[j + 1] - start <= window_frames:
            j += 1
        (x0, y0), (x1, y1) = centres[i], centres[j]
        best = max(best, math.hypot(x1 - x0, y1 - y0))
    return best


def total_displacement(boxes: Sequence[Sequence[float]]) -> float:
    if len(boxes) < 2:
        return 0.0
    (x0, y0), (x1, y1) = centre(boxes[0]), centre(boxes[-1])
    return math.hypot(x1 - x0, y1 - y0)


def classify_tracks(
    tracks: Iterable[dict[str, Any]], min_displacement_px: float = 25.0, window_frames: int = 15
) -> list[dict[str, Any]]:
    """Return copies of the tracks with `moving`, `displacement_px` and `total_displacement_px` set."""
    if min_displacement_px <= 0:
        raise ValueError("min_displacement_px must be > 0")
    out = []
    for t in tracks:
        disp = window_displacement(t["frames"], t["boxes"], window_frames)
        out.append({
            **t,
            "displacement_px": round(disp, 2),
            "total_displacement_px": round(total_displacement(t["boxes"]), 2),
            "moving": disp >= min_displacement_px,
        })
    return out
