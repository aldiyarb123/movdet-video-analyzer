"""Backend settings, read from environment variables (see .env.example)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ALLOWED_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv")
ALLOWED_CONTENT_TYPES = ("video/", "application/octet-stream")


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("MOVDET_DATA_DIR", "data")))
    max_upload_mb: int = field(default_factory=lambda: int(os.environ.get("MOVDET_MAX_UPLOAD_MB", "2048")))
    # "stub" fakes the analysis (for API and UI work); "pipeline" runs src/vision/pipeline.py.
    processor: str = field(default_factory=lambda: os.environ.get("MOVDET_PROCESSOR", "stub"))

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024
