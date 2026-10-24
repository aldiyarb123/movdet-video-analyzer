"""Tests for the detector + tracker integration (DIP-15).

The aggregation logic is tested without a model. The end-to-end test runs only when
Ultralytics is installed (`pip install -r requirements-ml.txt`).
"""
from __future__ import annotations

import os

import cv2
import numpy as np
import pytest

from src.vision.detector_tracker import TRACKERS, TrackAccumulator, class_ids, summarize, track_video

NAMES = {0: "person", 1: "bicycle", 2: "car"}


def test_accumulator_builds_tracks_in_baseline_format():
    acc = TrackAccumulator()
    acc.add(0, [1, 2], [[10, 20, 30, 60], [100, 100, 150, 130]], ["person", "car"], [0.9, 0.8])
    acc.add(1, [1], [[12.4, 20, 32.6, 60]], ["person"], [0.85])
    acc.add(3, [1], [[16, 20, 36, 60]], ["person"], [0.7])
    tracks = acc.tracks()
    assert [t["id"] for t in tracks] == [1, 2]
    person = tracks[0]
    assert person["frames"] == [0, 1, 3] and person["first_frame"] == 0 and person["last_frame"] == 3
    assert person["boxes"][0] == [10, 20, 20, 40]  # xyxy -> x, y, w, h
    assert person["boxes"][1] == [12, 20, 20, 40]
    assert len(person["boxes"]) == len(person["frames"]) == len(person["confidences"]) == person["n_detections"]


def test_class_is_majority_vote():
    acc = TrackAccumulator()
    for f, name in enumerate(["car", "truck", "car", "car"]):
        acc.add(f, [5], [[0, 0, 10, 10]], [name], [0.5])
    assert acc.tracks()[0]["class"] == "car"


def test_short_tracks_dropped_and_duplicates_ignored():
    acc = TrackAccumulator()
    acc.add(0, [1, 1], [[0, 0, 5, 5], [50, 50, 60, 60]], ["person", "person"], [0.9, 0.9])
    acc.add(0, [2], [[0, 0, 5, 5]], ["person"], [0.9])
    acc.add(1, [1], [[1, 0, 6, 5]], ["person"], [0.9])
    assert acc.tracks()[0]["n_detections"] == 2  # same frame counted once
    assert [t["id"] for t in acc.tracks(min_detections=2)] == [1]


def test_class_ids_mapping():
    assert class_ids(NAMES, None) is None
    assert class_ids(NAMES, ["Car", "person", "car"]) == [0, 2]
    with pytest.raises(ValueError, match="dragon"):
        class_ids(NAMES, ["dragon"])


def test_summary():
    acc = TrackAccumulator()
    for f in range(4):
        acc.add(f, [1, 2], [[0, 0, 5, 5], [9, 9, 20, 20]], ["person", "car"], [0.9, 0.9])
    result = {"video": "/x/v.avi", "method": "yolo+bytetrack", "frames": 4, "width": 64, "height": 48,
              "params": {}, "tracks": acc.tracks()}
    s = summarize(result)
    assert s["tracks"] == 2 and s["tracks_by_class"] == {"person": 1, "car": 1} and s["resolution"] == "64x48"


def test_supported_trackers():
    assert set(TRACKERS) == {"bytetrack", "botsort"}


def _model_available() -> bool:
    try:
        import ultralytics  # noqa: F401
    except ImportError:
        return False
    return os.path.exists("yolo11n.pt") or os.environ.get("MOVDET_ALLOW_DOWNLOAD") == "1"


@pytest.mark.skipif(not _model_available(), reason="needs ultralytics and yolo11n.pt (see requirements-ml.txt)")
def test_track_video_end_to_end(tmp_path):
    path = tmp_path / "v.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 120))
    for i in range(15):
        frame = np.full((120, 160, 3), 90, np.uint8)
        cv2.rectangle(frame, (10 + 3 * i, 40), (40 + 3 * i, 70), (240, 240, 240), -1)
        writer.write(frame)
    writer.release()
    seen = []
    result = track_video(path, tracker="bytetrack", min_detections=1, progress=seen.append)
    assert result["frames"] == 15 and (result["width"], result["height"]) == (160, 120)
    assert seen[-1] == 1.0
    for t in result["tracks"]:
        assert len(t["frames"]) == len(t["boxes"])
    with pytest.raises(ValueError):
        track_video(tmp_path / "missing.mp4")
