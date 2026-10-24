"""FR-06..FR-08 acceptance tests: motion filter, crops, clips (DIP-16)."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.vision.extractor import crop_box, extract, pick_indices
from src.vision.motion_filter import classify_tracks, window_displacement
from src.vision.pipeline import run_pipeline

W, H, FPS, N = 320, 240, 10, 60
MOVING_START, MOVING_END = 20, 49  # the moving square is visible on these frames


def moving_box(i: int) -> list[int]:
    return [10 + (i - MOVING_START) * 6, 100, 30, 30]


STATIC_BOX = [250, 30, 30, 30]


@pytest.fixture(scope="module")
def video(tmp_path_factory) -> Path:
    """Static background, a static grey square on all frames, a white square moving on frames 20..49."""
    path = tmp_path_factory.mktemp("v") / "scene.avi"
    rng = np.random.default_rng(1)
    bg = rng.integers(60, 100, size=(H, W, 3), dtype=np.uint8)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H))
    for i in range(N):
        frame = bg.copy()
        x, y, w, h = STATIC_BOX
        cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1), (160, 160, 160), -1)
        if MOVING_START <= i <= MOVING_END:
            x, y, w, h = moving_box(i)
            cv2.rectangle(frame, (x, y), (x + w - 1, y + h - 1), (255, 255, 255), -1)
        writer.write(frame)
    writer.release()
    return path


def gt_tracks() -> list[dict]:
    moving_frames = list(range(MOVING_START, MOVING_END + 1))
    return [
        {"id": 1, "class": "person", "first_frame": MOVING_START, "last_frame": MOVING_END,
         "frames": moving_frames, "boxes": [moving_box(i) for i in moving_frames]},
        {"id": 2, "class": "car", "first_frame": 0, "last_frame": N - 1,
         "frames": list(range(N)), "boxes": [STATIC_BOX] * N},
    ]


def frame_count(path: Path) -> int:
    cap = cv2.VideoCapture(str(path))
    n = 0
    while cap.read()[0]:
        n += 1
    cap.release()
    return n


# ---- FR-06 -------------------------------------------------------------------

def test_fr06_moving_object_marked_moving_static_not():
    moving, static = classify_tracks(gt_tracks(), min_displacement_px=25, window_frames=15)
    assert moving["moving"] is True and moving["displacement_px"] == pytest.approx(90, abs=1)
    assert static["moving"] is False and static["displacement_px"] == 0


def test_fr06_threshold_is_configurable():
    # 6 px/frame: 90 px inside a 15-frame window, 174 px over the whole 30-frame track
    moving, _ = classify_tracks(gt_tracks(), min_displacement_px=150, window_frames=15)
    assert moving["moving"] is False
    moving, _ = classify_tracks(gt_tracks(), min_displacement_px=150, window_frames=60)
    assert moving["moving"] is True
    assert moving["displacement_px"] == pytest.approx(174, abs=1)


def test_fr06_slow_drift_is_not_moving():
    frames = list(range(100))
    boxes = [[i, 0, 10, 10] for i in frames]  # 1 px per frame
    assert window_displacement(frames, boxes, 15) == pytest.approx(15)
    assert not classify_tracks([{"frames": frames, "boxes": boxes}], 25, 15)[0]["moving"]


def test_fr06_invalid_parameters():
    with pytest.raises(ValueError):
        classify_tracks(gt_tracks(), min_displacement_px=0)
    with pytest.raises(ValueError):
        window_displacement([0, 1], [[0, 0, 1, 1]], 15)


# ---- FR-07 -------------------------------------------------------------------

def test_pick_indices():
    assert pick_indices(30, 5) == [0, 7, 14, 22, 29]
    assert pick_indices(3, 5) == [0, 1, 2]
    assert pick_indices(10, 1) == [5]
    assert pick_indices(0, 5) == []


def test_crop_box_is_clamped():
    frame = np.zeros((100, 100, 3), np.uint8)
    assert crop_box(frame, [90, 90, 30, 30]).shape[:2] == (13, 13)  # 10% margin, clamped at 100
    assert crop_box(frame, [200, 200, 10, 10]) is None


@pytest.mark.parametrize("max_crops", [1, 3, 5])
def test_fr07_each_moving_track_has_1_to_n_readable_crops(video, tmp_path, max_crops):
    tracks = classify_tracks(gt_tracks(), 25, 15)
    out = extract(video, tracks, tmp_path, max_crops_per_track=max_crops, save_clips=False)
    moving, static = out
    assert 1 <= len(moving["crops"]) <= max_crops
    assert static["crops"] == [], "stationary tracks get no crops"
    for rel in moving["crops"]:
        img = cv2.imread(str(tmp_path / rel))
        assert img is not None, rel
        # the crop shows the object: the white square dominates the centre of the crop
        h, w = img.shape[:2]
        assert img[h // 2, w // 2].mean() > 200
    assert all(rel.startswith("crops/track_1/") for rel in moving["crops"])


# ---- FR-08 -------------------------------------------------------------------

@pytest.mark.parametrize("padding_s", [0.0, 0.5, 1.0])
def test_fr08_clip_plays_and_starts_within_padding(video, tmp_path, padding_s):
    tracks = classify_tracks(gt_tracks(), 25, 15)
    moving = extract(video, tracks, tmp_path, clip_padding_seconds=padding_s, save_crops=False)[0]
    pad = round(padding_s * FPS)
    assert abs(moving["clip_start_frame"] - (MOVING_START - pad)) <= 1
    assert abs(moving["clip_end_frame"] - min(MOVING_END + pad, N - 1)) <= 1
    clip = tmp_path / moving["clip"]
    assert clip.is_file()
    expected = moving["clip_end_frame"] - moving["clip_start_frame"] + 1
    assert abs(frame_count(clip) - expected) <= 1, "clip must contain the padded range"


def test_fr08_padding_is_clamped_to_video(video, tmp_path):
    track = {"id": 9, "moving": True, "first_frame": 0, "last_frame": N - 1,
             "frames": list(range(N)), "boxes": [STATIC_BOX] * N}
    out = extract(video, [track], tmp_path, clip_padding_seconds=5, save_crops=False)[0]
    assert (out["clip_start_frame"], out["clip_end_frame"]) == (0, N - 1)
    assert abs(frame_count(tmp_path / out["clip"]) - N) <= 1


def test_extraction_can_be_switched_off(video, tmp_path):
    out = extract(video, classify_tracks(gt_tracks()), tmp_path, save_crops=False, save_clips=False)
    assert out[0]["crops"] == [] and out[0]["clip"] is None
    assert not (tmp_path / "crops").exists() and not (tmp_path / "clips").exists()


def test_missing_video_raises(tmp_path):
    with pytest.raises(ValueError):
        extract(tmp_path / "nope.mp4", [], tmp_path)


# ---- whole pipeline with baseline B0 (no ML dependencies) ------------------------

def test_pipeline_with_baseline_produces_artefacts_and_report(video, tmp_path):
    out_dir = tmp_path / "job42" / "output"
    seen = []
    settings = {"backend": "mog2", "motion": {"min_displacement_px": 25, "window_frames": 15},
                "extraction": {"max_crops_per_track": 3, "clip_padding_seconds": 0.5}}
    result = run_pipeline(video, out_dir, settings, progress=seen.append)
    moving = [t for t in result["tracks"] if t["moving"]]
    assert moving, "the moving square must be found"
    for t in moving:
        assert 1 <= len(t["crops"]) <= 3 and t["clip"]
        assert (out_dir / t["clip"]).is_file()
    report = json.loads((out_dir / "report.json").read_text())
    assert report["job_id"] == "job42" and len(report["tracks"]) == len(result["tracks"])
    assert (out_dir / "report.csv").read_text().startswith("job_id,track_id")
    assert seen[-1] == pytest.approx(1.0) and seen == sorted(seen)


def test_pipeline_rejects_unknown_backend(video, tmp_path):
    with pytest.raises(ValueError):
        run_pipeline(video, tmp_path, {"backend": "magic"})
