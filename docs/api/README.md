# API contract

`openapi.json` is generated from the FastAPI code and is the contract between the backend (DIP-14) and the frontend (DIP-17).

```bash
uvicorn src.backend.app:app --reload           # API on http://127.0.0.1:8000, docs at /docs
python -m src.backend.export_openapi docs/api/openapi.json   # regenerate after API changes
```

| Endpoint | Purpose | Requirement |
|---|---|---|
| `GET /api/health` | Service check | — |
| `POST /api/jobs` | Upload `video` + `settings` (JSON), returns the job (201) | FR-01, FR-02, NFR-08 |
| `GET /api/jobs` | History, newest first | FR-12 |
| `GET /api/jobs/{id}` | Status and progress 0..1 | FR-03 |
| `GET /api/jobs/{id}/events` | Server-Sent Events until the job ends | FR-03 |
| `POST /api/jobs/{id}/cancel` | Cancel | FR-03 |
| `DELETE /api/jobs/{id}` | Delete job and files | FR-12 |
| `GET /api/jobs/{id}/video` | Uploaded video for the viewer | FR-09 |
| `GET /api/jobs/{id}/tracks` | Tracks, boxes as `[frame, x, y, w, h]`; `?moving_only=true` | FR-09 |
| `GET /api/jobs/{id}/report.json` · `report.csv` | Export in `docs/schemas/export-report.schema.json` | FR-11 |
| `GET /api/jobs/{id}/tracks/{tid}/crop?index=0` · `clip` | Artefacts of a moving track | FR-07, FR-08 |

Errors return `{"detail": "<readable message>"}`: 400 empty file, 413 too large, 415 wrong type, 422 invalid settings or unreadable video, 404 unknown job, 409 results not ready.

`MOVDET_PROCESSOR=stub` (default) fakes the analysis so the UI can be built without models; `pipeline` runs `src/vision/pipeline.py` (DIP-16).
