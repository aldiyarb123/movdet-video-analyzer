"""JSON and CSV export for MotionScope analysis tracks."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPORT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "schemas" / "export-report.schema.json"
)

CSV_FIELDS = (
    "job_id",
    "track_id",
    "class",
    "first_time_s",
    "last_time_s",
    "moving",
)


@dataclass(frozen=True)
class TrackReport:
    """A single tracked object included in an export report."""

    track_id: str
    class_name: str
    first_time_s: float
    last_time_s: float
    moving: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "class": self.class_name,
            "first_time_s": self.first_time_s,
            "last_time_s": self.last_time_s,
            "moving": self.moving,
        }


def build_report(job_id: str, tracks: Iterable[TrackReport]) -> dict[str, Any]:
    """Build a versioned report payload from one completed analysis job."""

    report = {
        "schema_version": "1.0",
        "job_id": job_id,
        "tracks": [track.to_dict() for track in tracks],
    }
    validate_report(report)
    return report


def export_json_report(
    output_path: str | Path,
    job_id: str,
    tracks: Iterable[TrackReport],
) -> dict[str, Any]:
    """Write a JSON report that conforms to the published report schema."""

    report = build_report(job_id, tracks)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def export_csv_report(
    output_path: str | Path,
    job_id: str,
    tracks: Iterable[TrackReport],
) -> None:
    """Write the same report fields as a CSV file."""

    report = build_report(job_id, tracks)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for track in report["tracks"]:
            writer.writerow(
                {
                    "job_id": report["job_id"],
                    "track_id": track["track_id"],
                    "class": track["class"],
                    "first_time_s": track["first_time_s"],
                    "last_time_s": track["last_time_s"],
                    "moving": str(track["moving"]).lower(),
                }
            )


def validate_report(
    report: dict[str, Any],
    schema_path: str | Path = REPORT_SCHEMA_PATH,
) -> None:
    """Validate a report against the published project JSON schema."""

    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    _validate_value(report, schema, "report")

    for track in report["tracks"]:
        if track["last_time_s"] < track["first_time_s"]:
            raise ValueError("last_time_s must be greater than or equal to first_time_s")


def _validate_value(value: Any, schema: dict[str, Any], location: str) -> None:
    expected_type = schema.get("type")

    if expected_type == "object":
        if not isinstance(value, dict):
            raise ValueError(f"{location} must be an object")

        for field in schema.get("required", []):
            if field not in value:
                raise ValueError(f"{location} is missing required field: {field}")

        if schema.get("additionalProperties") is False:
            allowed_fields = set(schema.get("properties", {}))
            unexpected = set(value) - allowed_fields
            if unexpected:
                raise ValueError(f"{location} has unexpected fields: {sorted(unexpected)}")

        for field, field_schema in schema.get("properties", {}).items():
            if field in value:
                _validate_value(value[field], field_schema, f"{location}.{field}")

    elif expected_type == "array":
        if not isinstance(value, list):
            raise ValueError(f"{location} must be an array")

        item_schema = schema.get("items", {})
        for index, item in enumerate(value):
            _validate_value(item, item_schema, f"{location}[{index}]")

    elif expected_type == "string":
        if not isinstance(value, str):
            raise ValueError(f"{location} must be a string")
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"{location} must not be empty")

    elif expected_type == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{location} must be a number")
        if value < schema.get("minimum", float("-inf")):
            raise ValueError(f"{location} is below the minimum value")

    elif expected_type == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{location} must be a boolean")

    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{location} must equal {schema['const']!r}")