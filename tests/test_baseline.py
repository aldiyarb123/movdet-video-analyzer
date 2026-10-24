"""Tests for the MOG2 baseline using deterministic synthetic videos."""
from pathlib import Path

import cv2
import numpy as np
import pytest

import json

from baseline_mog2 import (
    CentroidTracker,
    Track,
    is_moving,
    main,
    run,
    track_displacement,
    window_displacement,
)
from benchmark_baseline import benchmark

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


def make_track(step_px: float, n: int) -> Track:
    t = Track(id=1)
    for i in range(n):
        t.add(i, (round(i * step_px), 50, 20, 20))
    return t


def test_window_criterion_ignores_slow_drift():
    # 1 px per frame for 100 frames: 99 px overall, but only ~15 px inside a 15-frame window.
    slow = make_track(1.0, 100)
    assert is_moving(slow, 25, window_frames=None)
    assert window_displacement(slow, 15) == pytest.approx(15, abs=1)
    assert not is_moving(slow, 25, window_frames=15)


def test_window_criterion_accepts_fast_motion():
    fast = make_track(4.0, 20)
    assert window_displacement(fast, 15) == pytest.approx(60, abs=1)
    assert is_moving(fast, 25, window_frames=15)


def test_window_handles_gaps_in_track():
    t = Track(id=1)
    t.add(0, (0, 0, 10, 10))
    t.add(40, (100, 0, 10, 10))  # far apart in time: outside a 15-frame window
    assert window_displacement(t, 15) == 0.0
    assert window_displacement(t, 50) == pytest.approx(100)


def test_window_must_be_positive():
    with pytest.raises(ValueError):
        window_displacement(make_track(1, 5), 0)


def test_run_reports_params_and_progress(tmp_path):
    video = tmp_path / "moving.avi"
    make_video(video, n_frames=60, moving=True)
    seen = []
    result = run(video, window_frames=15, progress=seen.append)
    assert result["params"]["window_frames"] == 15
    assert (result["width"], result["height"]) == (W, H)
    assert seen[-1] == 1.0 and seen == sorted(seen), "progress must not decrease"
    for t in result["tracks"]:
        assert {"id", "class", "boxes", "frames", "moving", "window_displacement_px"} <= t.keys()
        assert len(t["boxes"]) == len(t["frames"])


def test_run_can_be_stopped(tmp_path):
    video = tmp_path / "moving.avi"
    make_video(video, n_frames=60, moving=True)
    calls = {"n": 0}

    def stop() -> bool:
        calls["n"] += 1
        return calls["n"] > 10

    assert run(video, should_stop=stop)["frames"] == 10


def test_resize_height(tmp_path):
    video = tmp_path / "moving.avi"
    make_video(video, n_frames=40, moving=True)
    result = run(video, resize_height=120)
    assert (result["width"], result["height"]) == (160, 120)


def test_undecodable_file_raises(tmp_path):
    bad = tmp_path / "bad.mp4"
    bad.write_bytes(b"not a video")
    with pytest.raises(ValueError):
        run(bad)


def test_cli_writes_json(tmp_path):
    video = tmp_path / "moving.avi"
    out = tmp_path / "out" / "tracks.json"
    make_video(video, n_frames=90, moving=True)
    main([str(video), "--out", str(out), "--window-frames", "15"])
    data = json.loads(out.read_text())
    assert data["frames"] == 90
    assert any(t["moving"] for t in data["tracks"])


def test_benchmark_reports_speed(tmp_path):
    video = tmp_path / "moving.avi"
    make_video(video, n_frames=60, moving=True)
    b = benchmark(video, repeat=1)
    assert b["frames"] == 60 and b["processing_fps"] > 0
    assert b["machine"]["cpu_count"]
