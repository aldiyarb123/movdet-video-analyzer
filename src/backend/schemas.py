"""API data models. They define the OpenAPI contract (docs/api/openapi.json)."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

DEFAULT_CLASSES = ["person", "car", "bicycle", "motorcycle", "bus", "truck"]


class MotionSettings(BaseModel):
    """ADR-0003: moving = centre travels at least `min_displacement_px` within `window_frames`."""

    model_config = ConfigDict(extra="forbid")
    min_displacement_px: float = Field(25.0, gt=0, le=10_000)
    window_frames: int = Field(15, ge=1, le=1_000)


class AnalysisSettings(BaseModel):
    """FR-02: analysis settings. Omitted fields get defaults; out-of-range values are rejected."""

    model_config = ConfigDict(extra="forbid")
    classes: list[str] = Field(default_factory=lambda: list(DEFAULT_CLASSES), min_length=1, max_length=80)
    confidence: float = Field(0.35, ge=0.05, le=0.95)
    tracker: Literal["bytetrack", "botsort"] = "bytetrack"
    backend: Literal["yolo", "mog2"] = Field("yolo", description="yolo = main pipeline, mog2 = baseline B0")
    motion: MotionSettings = Field(default_factory=MotionSettings)

    @field_validator("classes")
    @classmethod
    def _clean_classes(cls, value: list[str]) -> list[str]:
        cleaned = []
        for name in value:
            name = name.strip().lower()
            if not name or len(name) > 40:
                raise ValueError("class names must be 1-40 characters")
            if name not in cleaned:
                cleaned.append(name)
        return cleaned


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"
    cancelled = "cancelled"


TERMINAL = {JobStatus.done, JobStatus.failed, JobStatus.cancelled}


class JobSummary(BaseModel):
    frames: int
    fps: float
    tracks_total: int
    tracks_moving: int


class Job(BaseModel):
    id: str
    status: JobStatus
    progress: float = Field(0.0, ge=0, le=1, description="0..1, never decreases")
    error: str | None = None
    filename: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime
    settings: AnalysisSettings
    summary: JobSummary | None = None


class JobList(BaseModel):
    jobs: list[Job]


class Track(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: int
    class_name: str = Field(alias="class")
    first_frame: int
    last_frame: int
    moving: bool | None = None
    displacement_px: float | None = None
    boxes: list[list[int]] = Field(description="[frame, x, y, w, h] per observation")


class TracksResponse(BaseModel):
    job_id: str
    fps: float
    frames: int
    width: int
    height: int
    tracks: list[Track]


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    processor: str
