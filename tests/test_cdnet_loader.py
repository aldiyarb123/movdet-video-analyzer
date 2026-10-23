from pathlib import Path

import cv2
import numpy as np
import pytest

from src.data.cdnet_loader import load_cdnet_sequence, read_frame


def make_cdnet_subset(root: Path) -> Path:
    sequence_dir = root / "baseline" / "highway"
    input_dir = sequence_dir / "input"
    ground_truth_dir = sequence_dir / "groundtruth"

    input_dir.mkdir(parents=True)
    ground_truth_dir.mkdir()

    for index in (1, 2):
        image = np.full((12, 16, 3), index * 50, dtype=np.uint8)
        ground_truth = np.full((12, 16), 255, dtype=np.uint8)

        assert cv2.imwrite(str(input_dir / f"in{index:06d}.jpg"), image)
        assert cv2.imwrite(str(ground_truth_dir / f"gt{index:06d}.png"), ground_truth)

    (sequence_dir / "temporalROI.txt").write_text("1 2\n", encoding="utf-8")
    return root


def test_cdnet_subset_loads_images_and_ground_truth(tmp_path):
    dataset_root = make_cdnet_subset(tmp_path / "cdnet2014" / "dataset")

    sequence = load_cdnet_sequence(dataset_root, "baseline", "highway")

    assert sequence.category == "baseline"
    assert sequence.name == "highway"
    assert sequence.temporal_roi == (1, 2)
    assert [frame.index for frame in sequence.frames] == [1, 2]

    image, ground_truth = read_frame(sequence.frames[0])

    assert image.shape == (12, 16, 3)
    assert ground_truth is not None
    assert ground_truth.shape == (12, 16)


def test_loader_rejects_missing_sequence(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_cdnet_sequence(tmp_path, "baseline", "missing")