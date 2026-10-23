# 6. Requirements Specification

Priority uses MoSCoW: **M** must, **S** should, **C** could. Every mandatory requirement has an acceptance criterion that can be checked by a test or a measurement. Numeric targets marked *provisional* are the team's starting goals and must be calibrated after the first baseline benchmark ([09](09-verification-plan.md)); they are not measured results.

## 6.1 Functional requirements

| ID | Requirement | Pri | Acceptance criteria | Objective |
|---|---|---|---|---|
| FR-01 | The user can upload a video file (mp4, avi, mov, mkv) | M | Valid file → job created and ID returned. Unsupported type or size over the limit → 4xx with a readable message. Checked with 3 valid and 3 invalid files. | O4 |
| FR-02 | The user can configure analysis: classes, confidence, tracker, motion threshold | M | Defaults applied when omitted; out-of-range values rejected; chosen values stored with the job. | O4 |
| FR-03 | Analysis runs as an asynchronous job with status (queued, running, done, failed, cancelled) and progress % | M | Status endpoint reflects the real state; progress never decreases; failure includes a reason. | O3 |
| FR-04 | The system detects objects of the selected classes in each frame | M | Detection precision, recall, F1 computed on the evaluation set and reported against the baseline. | O3, O5 |
| FR-05 | The system tracks objects and keeps a persistent ID per object | M | IDF1 and ID switches reported on the evaluation set; tracker beats the baseline centroid tracker. | O3, O5 |
| FR-06 | The system marks each track as moving or stationary using a displacement criterion | M | On synthetic videos the moving object is marked moving and the static object is not (unit tests pass); threshold is configurable. | O3 |
| FR-07 | The system saves cropped images of each moving track | M | Each moving track has 1 to N crop files (N configurable); files open and show the object. | O3 |
| FR-08 | The system saves a clip for each moving track with padding | S | Clip plays; starts within the padding of first appearance (±1 frame). | O3 |
| FR-09 | The viewer plays the video with overlays (boxes, IDs) in sync | M | Overlay for frame t corresponds to data for frame t (±1 frame); works on a 10-minute video. | O4 |
| FR-10 | The user can list and filter objects (class, duration, moving) and see a timeline | S | Filters change the list as expected; selecting an object seeks the video. | O4 |
| FR-11 | The user can export a JSON and a CSV report | M | Files validate against the published schema; contain track ID, class, first/last time, moving flag. | O4 |
| FR-12 | The user can view job history and delete a job | S | History lists jobs newest first; deletion removes records and files. | O4 |
| FR-13 | The user can cancel a running job | S | Job reaches *cancelled* within 5 s *(provisional)* and releases resources. | O3 |
| FR-14 | The API is documented (OpenAPI) | M | Documentation page lists all endpoints with request and response examples. | O4 |
| FR-15 | An evaluation tool runs the baseline and the main pipeline on a dataset and prints metrics | S | One command reproduces the metrics table in the evaluation report. | O5 |
| FR-16 | Live RTSP stream input | C | Stream analysed with end-to-end delay recorded. | |
| FR-17 | Zone and line-crossing counting | C | Counts match manual counts on a test clip. | |

## 6.2 Non-functional requirements

| ID | Requirement | Pri | Acceptance criteria (*provisional* where marked) |
|---|---|---|---|
| NFR-01 | Performance | M | Throughput measured on a documented reference machine at 720p; target *provisional*: at least 10 FPS on CPU with the smallest model, at least 25 FPS with a GPU. Final numbers set after the baseline benchmark. |
| NFR-02 | Responsiveness | S | Results page shows the first frame within 3 s for a 10-minute video *(provisional)*. |
| NFR-03 | Privacy | M | Analysis makes no external network calls: verified by running a full job with the network disabled. |
| NFR-04 | Usability | M | At least 5 test users; System Usability Scale score of 68 or higher; at least 80% complete *upload → view → export* without help. |
| NFR-05 | Reliability | M | A corrupt or unsupported video ends in *failed* with a reason, and the service keeps running (fault-injection test). |
| NFR-06 | Maintainability | S | CI runs tests on every pull request; unit-test coverage on pipeline and API logic of at least 70% *(provisional)*. |
| NFR-07 | Portability | S | Setup instructions verified on Windows and Linux; optional `docker compose up`. |
| NFR-08 | Security | M | Upload size limit, extension and content-type checks, sanitised file names; no secrets in the repository (secret scan clean). |
| NFR-09 | Reproducibility | M | Evaluation scripts, configs and seeds are versioned; a second team member reproduces the reported metrics. |
| NFR-10 | Browser support | S | Works in current Chrome, Firefox and Edge. |

## 6.3 Validation and review status

This is an initial specification for Pre-defense 1. Requirements derived from the proposal, comparison, and technical analysis are treated as design assumptions until they are confirmed by user interviews or supervisor feedback. The team will record each confirmed change in YouTrack and in the relevant document.

| Requirement group | Current basis | Validation before the final specification |
|---|---|---|
| FR-01 to FR-03, FR-09 to FR-14 | Project proposal, UX prototype, and anticipated user workflow | Review the core user flow with the supervisor and interview user representatives. |
| FR-04 to FR-08, FR-13, and FR-15 | Literature review, technology comparison, and verification plan | Confirm feasibility through the baseline benchmark and pipeline tests. |
| FR-16 and FR-17 | Optional future scope from the project proposal | Keep outside the MVP unless approved after the core workflow is complete. |
| NFR-01 to NFR-10 | Project risks, privacy constraints, and evaluation plan | Calibrate provisional numerical targets after the first benchmark; validate privacy and reliability through tests. |

## 6.4 Constraints and assumptions

- Static camera in the MVP.
- Only consented or public-benchmark videos are used for evaluation.
- Model and library licences must allow the intended use (risk R1).
- Requirements are drafts until interviews are completed ([02](02-evidence-of-relevance.md)); update this file and note the source of each change.

## 6.5 Traceability

| Objective | Requirements | Verified by |
|---|---|---|
| O1 Requirements | all | Interviews, review with supervisor |
| O2 Technology | NFR-01, NFR-07 | ADRs, benchmark |
| O3 Pipeline | FR-03..FR-08, FR-13, NFR-01, NFR-05 | Unit and integration tests, benchmark |
| O4 API and UI | FR-01, FR-02, FR-09..FR-12, FR-14, NFR-02, NFR-04, NFR-08, NFR-10 | API tests, UI tests, usability test |
| O5 Evaluation | FR-04, FR-05, FR-15, NFR-09 | Evaluation report |
| O6 Management | | Git and YouTrack history |
