# 7. Architecture and Diagrams

Diagrams (editable Graphviz sources in `diagrams/src/`, exports in `diagrams/export/`):

1. System context: [SVG](../diagrams/export/01-system-context.svg) · [PNG](../diagrams/export/01-system-context.png)
2. Use case: [SVG](../diagrams/export/02-use-case.svg) · [PNG](../diagrams/export/02-use-case.png)
3. Component (draft): [SVG](../diagrams/export/03-component-draft.svg) · [PNG](../diagrams/export/03-component-draft.png)

Regenerate: `dot -Tsvg diagrams/src/03-component-draft.dot -o diagrams/export/03-component-draft.svg`

## 7.1 Architectural overview

A web UI talks to a REST backend. Uploads are stored on disk; analysis is an asynchronous job placed on a Redis queue and executed by a vision worker (decode → detect → track → motion filter → extract). Progress reaches the browser through Server-Sent Events. Results (tracks, crops, clips, report) are stored in PostgreSQL and the file store and served by the results service.

## 7.2 Components

| Component | Responsibility | Requirements | Owner |
|---|---|---|---|
| Frontend (React + TS) | Upload, settings, progress, results viewer with canvas overlay, history, export buttons | FR-01, 02, 09–12 | Asylkhan |
| Backend API (FastAPI) | Validation, jobs, results, export, OpenAPI docs | FR-01–03, 11–14, NFR-08 | Aldiyar |
| Job queue (Redis + RQ) | Decouples requests from long processing, carries progress | FR-03, 13 | Aldiyar |
| Vision worker | Decoder, detector, tracker, motion filter, extractor | FR-04–08, NFR-01 | Aldiyar |
| Storage | PostgreSQL for metadata; file store for media | FR-12 | Aldiyar, Alikhan |
| Evaluation tool | Baseline B0, metrics, reports | FR-15, NFR-09 | Alikhan |

## 7.3 Core data (draft)

| Entity | Main fields |
|---|---|
| Job | id, status, progress, created_at, video_path, fps, frame_count, settings (JSON), error |
| Track | id, job_id, class, first_frame, last_frame, moving (bool), displacement_px, mean_confidence |
| Detection | track_id, frame, x, y, w, h, confidence (stored compactly per track) |
| Artifact | id, track_id, kind (crop, clip), path |

## 7.4 Main flow

1. `POST /api/jobs` with video and settings → validated, saved, job `queued`, ID returned.
2. Worker takes the job, decodes frames, runs detector and tracker, updates progress.
3. Motion filter marks tracks moving or stationary by displacement over a window.
4. Extractor writes crops, clips, report; job becomes `done`.
5. UI opens the results: video, overlay from `GET /api/jobs/{id}/tracks`, artefacts, export.

## 7.5 API sketch (examples for the contract)

| Method and path | Purpose |
|---|---|
| `POST /api/jobs` | Upload video + settings, create job |
| `GET /api/jobs` | History |
| `GET /api/jobs/{id}` | Status and progress |
| `GET /api/jobs/{id}/events` | SSE progress stream |
| `POST /api/jobs/{id}/cancel` | Cancel |
| `GET /api/jobs/{id}/tracks` | Tracks with boxes per frame |
| `GET /api/jobs/{id}/report.json` · `report.csv` | Exports |
| `GET /api/jobs/{id}/tracks/{tid}/crop` · `clip` | Artefacts |
| `DELETE /api/jobs/{id}` | Delete job and files |

Create-job request (multipart): `video` (file), `settings` (JSON):
```json
{ "classes": ["person", "car"], "confidence": 0.35, "tracker": "bytetrack",
  "motion": { "min_displacement_px": 25, "window_frames": 15 } }
```
Status response:
```json
{ "id": "a1b2c3", "status": "running", "progress": 0.42, "error": null }
```
Track response (abridged):
```json
{ "id": 7, "class": "person", "first_frame": 120, "last_frame": 310,
  "moving": true, "displacement_px": 412.5,
  "boxes": [[120, 340, 88, 52, 160], [121, 344, 88, 52, 160]] }
```
(box = frame, x, y, w, h in the abridged example; final schema to be fixed in the OpenAPI file.)

## 7.6 Definition of "moving"

A track is *moving* if the straight-line displacement of its center within the configured window exceeds a threshold (static camera assumed). The baseline implements this criterion in `src/vision/baseline_mog2.py` (`is_moving`) and it is covered by unit tests. The criterion is deliberately simple and measurable; limitations (slow motion, camera shake) are listed in the risks. See [ADR-0003](adr/0003-moving-definition.md).

## 7.7 Quality attributes and tactics

| Attribute | Tactic |
|---|---|
| Performance | Smallest sufficient model, frame skipping option, batch decoding, benchmark in CI later |
| Privacy | Local processing only, no external calls during analysis |
| Reliability | Isolated worker process, job states, timeouts, cleanup on failure |
| Security | Upload validation, size limits, sanitised names, `.env` for secrets |
| Maintainability | Detector and tracker behind interfaces, so models are replaceable |

## 7.8 Alignment check (requirements ↔ components ↔ scenarios)

Every use case UC1–UC12 maps to at least one component and requirement: UC1 → Upload service, FR-01; UC2/UC3 → Jobs service, FR-02/03; UC4 → SSE, FR-03; UC5 → Jobs service, FR-13; UC6/UC7 → Results viewer, FR-09/10; UC8 → Extractor, FR-07/08; UC9 → Export service, FR-11; UC10/UC11 → History, FR-12; UC12 → Evaluation tool, FR-15.

## 7.9 Decisions

[ADR-0001 Detector and tracker](adr/0001-detector-and-tracker.md) · [ADR-0002 Asynchronous job processing](adr/0002-async-job-processing.md) · [ADR-0003 Definition of moving](adr/0003-moving-definition.md)
