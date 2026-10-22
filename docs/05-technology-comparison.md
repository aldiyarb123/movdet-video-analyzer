# 5. Technology Comparison

Six key technical decisions, each with 2–3 alternatives. Scores are 1 (poor) to 5 (excellent), weights 1–3. **Scores are the author's draft judgement from the cited sources and general engineering knowledge; the team must review them, adjust weights to its real skills and constraints, and record the final choice in an ADR.** Items marked *(verify)* need a check or a quick experiment.

Score = Σ(weight × score). Maximum is 5 × Σweights.

## D1. Moving-object detection approach

| Criterion | Weight | MOG2 background subtraction | YOLO family (Ultralytics) | RF-DETR (transformer) |
|---|---|---|---|---|
| Gives object class | 3 | 1 | 5 | 5 |
| Robust to lighting / dynamic background | 3 | 2 | 4 | 4 |
| Speed on modest hardware | 2 | 5 | 4 | 3 |
| Setup effort and ecosystem | 2 | 5 | 5 | 3 |
| Licence and cost *(verify)* | 2 | 5 | 2 | 4 |
| **Total / 60** | | **39** | **49** | **47** |

**Decision (proposed):** YOLO family as the main detector; MOG2 kept as the **baseline** for evaluation. Licence is the weak point of YOLO (see risk R1): confirm terms; RF-DETR is the fallback.
Evidence: [L1], [L6]–[L8], [G1].

## D2. Tracker

| Criterion | Weight | ByteTrack | BoT-SORT | DeepSORT |
|---|---|---|---|---|
| Handles low-confidence / partly hidden objects | 3 | 4 | 4 | 4 |
| Speed and low complexity | 3 | 5 | 4 | 2 |
| No extra appearance (re-ID) model needed | 2 | 5 | 3 | 1 |
| Built-in support in detector stack | 2 | 5 | 5 | 3 |
| **Total / 50** | | **47** | **40** | **26** |

**Decision (proposed):** ByteTrack default, BoT-SORT selectable. Evidence: [L11]–[L14], [G1], [G5]. The choice must be re-checked on our own footage ([09-verification-plan.md](09-verification-plan.md)).

## D3. Backend framework

| Criterion | Weight | FastAPI | Django REST | Flask |
|---|---|---|---|---|
| Python CV integration | 3 | 5 | 5 | 5 |
| Built-in validation and OpenAPI docs | 2 | 5 | 3 | 2 |
| Async / streaming (SSE, WebSocket) | 2 | 5 | 3 | 3 |
| Learning curve and boilerplate | 2 | 4 | 3 | 4 |
| **Total / 45** | | **43** | **33** | **33** |

**Decision (proposed):** FastAPI (typed models and auto-generated API docs support FR-16 directly). *(verify against the backend owner's experience.)*

## D4. Data storage

| Criterion | Weight | PostgreSQL | SQLite | MongoDB |
|---|---|---|---|---|
| Concurrent job and metadata access | 3 | 5 | 3 | 4 |
| Setup effort | 2 | 3 | 5 | 3 |
| Structured queries on tracks and events | 3 | 5 | 4 | 3 |
| Path to scaling | 2 | 5 | 2 | 4 |
| **Total / 50** | | **46** | **35** | **35** |

**Decision (proposed):** PostgreSQL for metadata (SQLite acceptable in unit tests via an ORM). Large artefacts (videos, crops, clips) on the local file system behind a storage interface, so an S3-compatible store can replace it later.

## D5. Component interaction and job processing

| Criterion | Weight | REST + Redis queue (RQ) + SSE progress | REST + BackgroundTasks + polling | gRPC with streaming |
|---|---|---|---|---|
| Reliability for long jobs | 3 | 5 | 2 | 4 |
| Progress reporting to the UI | 2 | 4 | 3 | 4 |
| Setup effort | 2 | 3 | 5 | 2 |
| Testability | 2 | 4 | 4 | 3 |
| **Total / 45** | | **37** | **30** | **30** |

**Decision (proposed):** REST API, Redis-backed worker queue, progress via Server-Sent Events. Browser access to gRPC needs a proxy, which adds complexity *(verify)*.

## D6. Frontend

| Criterion | Weight | React + TypeScript + Vite | Vue 3 | Svelte |
|---|---|---|---|---|
| Video + canvas overlay libraries and examples | 3 | 5 | 4 | 3 |
| Ecosystem and typing | 2 | 5 | 4 | 3 |
| Team familiarity *(frontend owner to set)* | 3 | 4 | 3 | 2 |
| Build tooling | 2 | 5 | 5 | 5 |
| **Total / 50** | | **47** | **39** | **31** |

**Decision (proposed):** React + TypeScript. The familiarity row is a placeholder: Asylkhan should rescore it.

## Summary of proposed stack

| Decision | Choice | Fallback |
|---|---|---|
| Detector | YOLO (Ultralytics) | RF-DETR |
| Baseline | OpenCV MOG2 | |
| Tracker | ByteTrack | BoT-SORT |
| Backend | FastAPI | Django REST |
| Storage | PostgreSQL + file storage | SQLite |
| Jobs | Redis + RQ, SSE progress | BackgroundTasks |
| Frontend | React + TypeScript | Vue 3 |

Each final choice becomes an ADR in [adr/](adr/).
