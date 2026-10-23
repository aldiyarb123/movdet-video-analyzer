"""Loader for a local CDnet 2014 subset.

Expected local layout:
data/cdnet2014/dataset/<category>/<sequence>/
├── input/
│   └── in000001.jpg
├── groundtruth/
│   └── gt000001.png
└── temporalROI.txt
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

_INPUT_PATTERN = re.compile(r"^in(?P<index>\d+)\.(jpg|jpeg|png)$", re.IGNORECASE)
_GT_EXTENSIONS = (".png", ".bmp")


@dataclass(frozen=True)
class CDnetFrame:
    """One CDnet input frame and its optional ground-truth mask."""

    index: int
    image_path: Path
    ground_truth_path: Path | None


@dataclass(frozen=True)
class CDnetSequence:
    """Metadata and file paths for one CDnet sequence."""

    dataset_root: Path
    category: str
    name: str
    frames: tuple[CDnetFrame, ...]
    temporal_roi: tuple[int, int] | None

    @property
    def path(self) -> Path:
        return self.dataset_root / self.category / self.name


def _frame_index(path: Path) -> int:
    match = _INPUT_PATTERN.match(path.name)
    if match is None:
        raise ValueError(f"Not a CDnet input frame: {path.name}")
    return int(match.group("index"))


def _ground_truth_path(ground_truth_dir: Path, index: int) -> Path | None:
    stem = f"gt{index:06d}"
    for extension in _GT_EXTENSIONS:
        candidate = ground_truth_dir / f"{stem}{extension}"
        if candidate.is_file():
            return candidate
    return None


def _read_temporal_roi(path: Path) -> tuple[int, int] | None:
    if not path.is_file():
        return None

    values = path.read_text(encoding="utf-8").split()
    if len(values) < 2:
        raise ValueError(f"Invalid temporal ROI file: {path}")

    start, end = int(values[0]), int(values[1])
    if start > end:
        raise ValueError(f"Invalid temporal ROI range in {path}")

    return start, end


def load_cdnet_sequence(
    dataset_root: str | Path,
    category: str,
    sequence: str,
    require_ground_truth: bool = True,
) -> CDnetSequence:
    """Load metadata for one CDnet sequence without loading all images into memory."""

    root = Path(dataset_root)
    sequence_dir = root / category / sequence
    input_dir = sequence_dir / "input"
    ground_truth_dir = sequence_dir / "groundtruth"

    if not sequence_dir.is_dir():
        raise FileNotFoundError(f"CDnet sequence was not found: {sequence_dir}")
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Missing input directory: {input_dir}")
    if require_ground_truth and not ground_truth_dir.is_dir():
        raise FileNotFoundError(f"Missing ground-truth directory: {ground_truth_dir}")

    input_paths = sorted(
        (path for path in input_dir.iterdir() if _INPUT_PATTERN.match(path.name)),
        key=_frame_index,
    )
    if not input_paths:
        raise ValueError(f"No CDnet input frames found in: {input_dir}")

    frames: list[CDnetFrame] = []
    for image_path in input_paths:
        index = _frame_index(image_path)
        ground_truth_path = _ground_truth_path(ground_truth_dir, index)

        if require_ground_truth and ground_truth_path is None:
            raise FileNotFoundError(
                f"Missing ground truth for frame {index}: expected gt{index:06d}.png or .bmp"
            )

        frames.append(
            CDnetFrame(
                index=index,
                image_path=image_path,
                ground_truth_path=ground_truth_path,
            )
        )

    return CDnetSequence(
        dataset_root=root,
        category=category,
        name=sequence,
        frames=tuple(frames),
        temporal_roi=_read_temporal_roi(sequence_dir / "temporalROI.txt"),
    )


def read_frame(frame: CDnetFrame) -> tuple[np.ndarray, np.ndarray | None]:
    """Read one input image and its ground-truth mask from disk."""

    image = cv2.imread(str(frame.image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot read image: {frame.image_path}")

    ground_truth = None
    if frame.ground_truth_path is not None:
        ground_truth = cv2.imread(str(frame.ground_truth_path), cv2.IMREAD_GRAYSCALE)
        if ground_truth is None:
            raise ValueError(f"Cannot read ground truth: {frame.ground_truth_path}")

    return image, ground_truth


def main() -> None:
    parser = argparse.ArgumentParser(description="Check that a local CDnet sequence can be loaded")
    parser.add_argument("dataset_root", help="Example: data/cdnet2014/dataset")
    parser.add_argument("category", help="Example: baseline")
    parser.add_argument("sequence", help="Example: highway")
    parser.add_argument("--limit", type=int, default=3, help="Number of frames to read")
    args = parser.parse_args()

    sequence = load_cdnet_sequence(args.dataset_root, args.category, args.sequence)
    frames_to_read = sequence.frames[: args.limit]

    for frame in frames_to_read:
        image, ground_truth = read_frame(frame)
        ground_truth_shape = None if ground_truth is None else ground_truth.shape
        print(
            f"frame={frame.index} image={image.shape} "
            f"ground_truth={ground_truth_shape}"
        )

    print(
        f"Loaded {len(sequence.frames)} frames from "
        f"{sequence.category}/{sequence.name}; temporal ROI={sequence.temporal_roi}"
    )


if __name__ == "__main__":
    main()