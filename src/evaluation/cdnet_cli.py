"""Evaluate the MOG2 baseline on one local CDnet 2014 sequence."""

from __future__ import annotations

import argparse
from typing import Any

import cv2
import numpy as np

from src.data.cdnet_loader import load_cdnet_sequence, read_frame


def metrics_from_counts(tp: int, fp: int, fn: int, tn: int) -> dict[str, float | int]:
    """Calculate binary foreground-segmentation metrics."""

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    total = tp + fp + fn + tn
    pwc_percent = 100 * (fp + fn) / total if total else 0.0

    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "pwc_percent": pwc_percent,
    }


def compute_binary_metrics(
    predicted_mask: np.ndarray,
    ground_truth_mask: np.ndarray,
) -> dict[str, float | int]:
    """Compare a MOG2 mask with CDnet ground truth.

    CDnet foreground is 255 and background is 0. Shadow and unknown labels
    are excluded from the metric calculation.
    """

    if predicted_mask.shape != ground_truth_mask.shape:
        raise ValueError("Prediction and ground truth must have the same shape")

    valid = (ground_truth_mask == 0) | (ground_truth_mask == 255)
    predicted_foreground = predicted_mask == 255
    actual_foreground = ground_truth_mask == 255

    tp = int(np.count_nonzero(valid & predicted_foreground & actual_foreground))
    fp = int(np.count_nonzero(valid & predicted_foreground & ~actual_foreground))
    fn = int(np.count_nonzero(valid & ~predicted_foreground & actual_foreground))
    tn = int(np.count_nonzero(valid & ~predicted_foreground & ~actual_foreground))

    return metrics_from_counts(tp, fp, fn, tn)


def evaluate_sequence(
    dataset_root: str,
    category: str,
    sequence_name: str,
    max_frames: int | None = None,
) -> dict[str, Any]:
    """Run the B0 MOG2 baseline and aggregate metrics for a CDnet sequence."""

    sequence = load_cdnet_sequence(dataset_root, category, sequence_name)
    temporal_roi = sequence.temporal_roi or (
        sequence.frames[0].index,
        sequence.frames[-1].index,
    )

    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=16,
        detectShadows=True,
    )

    totals = {"true_positive": 0, "false_positive": 0, "false_negative": 0, "true_negative": 0}
    processed_frames = 0
    evaluated_frames = 0

    frames = sequence.frames if max_frames is None else sequence.frames[:max_frames]

    for frame in frames:
        image, ground_truth = read_frame(frame)
        predicted_mask = subtractor.apply(image)
        processed_frames += 1

        if ground_truth is None or not temporal_roi[0] <= frame.index <= temporal_roi[1]:
            continue

        metrics = compute_binary_metrics(predicted_mask, ground_truth)
        for key in totals:
            totals[key] += int(metrics[key])
        evaluated_frames += 1

    result = metrics_from_counts(
        totals["true_positive"],
        totals["false_positive"],
        totals["false_negative"],
        totals["true_negative"],
    )
    result.update(
        {
            "dataset": f"{category}/{sequence_name}",
            "processed_frames": processed_frames,
            "evaluated_frames": evaluated_frames,
            "temporal_roi": temporal_roi,
        }
    )
    return result


def format_metrics_table(result: dict[str, Any]) -> str:
    """Format evaluation results as a readable terminal table."""

    rows = [
        ("Dataset", result["dataset"]),
        ("Processed frames", result["processed_frames"]),
        ("Evaluated frames", result["evaluated_frames"]),
        ("Precision", f"{result['precision']:.4f}"),
        ("Recall", f"{result['recall']:.4f}"),
        ("F1 score", f"{result['f1']:.4f}"),
        ("PWC", f"{result['pwc_percent']:.2f}%"),
        ("True positive", result["true_positive"]),
        ("False positive", result["false_positive"]),
        ("False negative", result["false_negative"]),
        ("True negative", result["true_negative"]),
    ]
    width = max(len(name) for name, _ in rows)

    lines = [
        f"{'Metric':<{width}} | Value",
        f"{'-' * width}-|------",
    ]
    lines.extend(f"{name:<{width}} | {value}" for name, value in rows)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the MOG2 baseline on a local CDnet sequence"
    )
    parser.add_argument("dataset_root", help="Example: data/cdnet2014/dataset")
    parser.add_argument("category", help="Example: lowFramerate")
    parser.add_argument("sequence", help="Example: tramCrossroad_1fps")
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional limit for a short first evaluation run",
    )
    args = parser.parse_args()

    result = evaluate_sequence(
        args.dataset_root,
        args.category,
        args.sequence,
        max_frames=args.max_frames,
    )
    print(format_metrics_table(result))


if __name__ == "__main__":
    main()