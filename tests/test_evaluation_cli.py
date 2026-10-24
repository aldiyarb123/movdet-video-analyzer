import numpy as np
import pytest

from src.evaluation.cdnet_cli import compute_binary_metrics, format_metrics_table


def test_binary_metrics_are_calculated_correctly():
    predicted = np.array(
        [
            [255, 0],
            [255, 0],
        ],
        dtype=np.uint8,
    )
    ground_truth = np.array(
        [
            [255, 0],
            [0, 255],
        ],
        dtype=np.uint8,
    )

    metrics = compute_binary_metrics(predicted, ground_truth)

    assert metrics["true_positive"] == 1
    assert metrics["false_positive"] == 1
    assert metrics["false_negative"] == 1
    assert metrics["true_negative"] == 1
    assert metrics["precision"] == pytest.approx(0.5)
    assert metrics["recall"] == pytest.approx(0.5)
    assert metrics["f1"] == pytest.approx(0.5)
    assert metrics["pwc_percent"] == pytest.approx(50.0)


def test_metrics_table_contains_main_evaluation_values():
    table = format_metrics_table(
        {
            "dataset": "lowFramerate/tramCrossroad_1fps",
            "processed_frames": 450,
            "evaluated_frames": 51,
            "precision": 0.5,
            "recall": 0.5,
            "f1": 0.5,
            "pwc_percent": 50.0,
            "true_positive": 1,
            "false_positive": 1,
            "false_negative": 1,
            "true_negative": 1,
        }
    )

    assert "Precision" in table
    assert "Recall" in table
    assert "F1 score" in table
    assert "PWC" in table