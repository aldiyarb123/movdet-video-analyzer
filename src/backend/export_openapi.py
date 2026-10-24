"""Write the OpenAPI contract to a file.

Usage (from the repository root):
    python -m src.backend.export_openapi docs/api/openapi.json
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from .app import create_app
from .config import Settings


def main(argv: list[str] | None = None) -> None:
    out = Path((argv or sys.argv[1:] or ["docs/api/openapi.json"])[0])
    with tempfile.TemporaryDirectory() as tmp:
        app = create_app(Settings(data_dir=Path(tmp)))
        spec = app.openapi()
        app.state.manager.shutdown()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"{len(spec['paths'])} paths -> {out}")


if __name__ == "__main__":
    main()
