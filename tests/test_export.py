import csv
import json

import pytest

from src.reporting.export import (
    TrackReport,
    export_csv_report,
    export_json_report,
    validate_report,
)


def sample_tracks():
    return [
        TrackReport(
            track_id="track-001",
            class_name="person",
            first_time_s=1.25,
            last_time_s=4.75,
            moving=True,
        ),
        TrackReport(
            track_id="track-002",
            class_name="car",
            first_time_s=2.0,
            last_time_s=2.0,
            moving=False,
        ),
    ]


def test_json_and_csv_exports_follow_the_report_schema(tmp_path):
    json_path = tmp_path / "report.json"
    csv_path = tmp_path / "report.csv"

    report = export_json_report(json_path, "job-001", sample_tracks())
    export_csv_report(csv_path, "job-001", sample_tracks())

    saved_report = json.loads(json_path.read_text(encoding="utf-8"))
    validate_report(saved_report)

    assert report == saved_report
    assert saved_report["tracks"][0]["track_id"] == "track-001"
    assert saved_report["tracks"][0]["class"] == "person"
    assert saved_report["tracks"][0]["moving"] is True

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows[0]["job_id"] == "job-001"
    assert rows[0]["track_id"] == "track-001"
    assert rows[0]["class"] == "person"
    assert rows[0]["first_time_s"] == "1.25"
    assert rows[0]["last_time_s"] == "4.75"
    assert rows[0]["moving"] == "true"


def test_report_rejects_last_time_before_first_time(tmp_path):
    invalid_track = TrackReport(
        track_id="track-003",
        class_name="person",
        first_time_s=5.0,
        last_time_s=2.0,
        moving=True,
    )

    with pytest.raises(ValueError, match="last_time_s"):
        export_json_report(tmp_path / "invalid.json", "job-002", [invalid_track])