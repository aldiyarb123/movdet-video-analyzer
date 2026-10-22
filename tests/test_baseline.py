"""Tests for the MOG2 baseline using deterministic synthetic videos."""
from pathlib import Path

import cv2
import numpy as np
import pytest

from baseline_mog2 import CentroidTracker, Track, is_moving, run, track_displacement

W, H = 320, 240


def make_video(path: Path, n_frames: int, moving: bool, warmup: int = 30) -> None:
    """Static textured background; optionally one square moving left to right."""
    rng = np.random.default_rng(0)
    background = rng.integers(60, 100, size=(H, W, 3), dtype=np.uint8)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 25, (W, H))
    assert writer.isOpened()
    for i in range(n_frames):
        frame = background.copy()
        if moving and i >= warmup:
            x = 10 + (i - warmup) * 4
            cv2.rectangle(frame, (x, 100), (x + 30, 130), (255, 255, 255), -1)
        writer.write(frame)
    writer.release()


def test_displacement_and_criterion():
    t = Track(id=1)
    t.add(0, (0, 0, 10, 10))
    t.add(1, (30, 40, 10, 10))
    assert track_displacement(t) == pytest.approx(50.0)
    assert is_moving(t, min_displacement_px=25)
    assert not is_moving(t, min_displacement_px=60)


def test_single_detection_is_not_moving():
    t = Track(id=1)
    t.add(0, (5, 5, 10, 10))
    assert track_displacement(t) == 0.0
    assert not is_moving(t)


def test_tracker_keeps_identity_for_close_boxes():
    tracker = CentroidTracker(max_distance=30)
    tracker.update(0, [(10, 10, 20, 20)])
    tracker.update(1, [(14, 10, 20, 20)])
    tracker.update(2, [(18, 10, 20, 20)])
    tracks = tracker.all_tracks()
    assert len(tracks) == 1
    assert tracks[0].frames == [0, 1, 2]


def test_tracker_creates_new_track_for_far_box():
    tracker = CentroidTracker(max_distance=30)
    tracker.update(0, [(10, 10, 20, 20)])
    tracker.update(1, [(200, 200, 20, 20)])
    assert len(tracker.all_tracks()) == 2


def test_tracker_drops_lost_track():
    tracker = CentroidTracker(max_distance=30, max_missed=2)
    tracker.update(0, [(10, 10, 20, 20)])
    for i in range(1, 5):
        tracker.update(i, [])
    assert len(tracker.finished) == 1 and not tracker.active


def test_moving_square_is_found(tmp_path):
    video = tmp_path / "moving.avi"
    make_video(video, n_frames=90, moving=True)
    result = run(video)
    moving = [t for t in result["tracks"] if t["moving"]]
    assert moving, "expected at least one moving track"
    assert max(t["displacement_px"] for t in moving) > 100


def test_static_scene_has_no_moving_tracks(tmp_path):
    video = tmp_path / "static.avi"
    make_video(video, n_frames=60, moving=False)
    result = run(video)
    assert not [t for t in result["tracks"] if t["moving"]]


def test_missing_file_raises(tmp_path):
    with pytest.raises(ValueError):
        run(tmp_path / "nope.mp4")
