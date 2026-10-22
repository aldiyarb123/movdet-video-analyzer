# 10. Project Management and Risks

## 10.1 Tools

| Item | Value |
|---|---|
| Git repository | `<REPO_URL>` (GitHub or GitLab; supervisor and committee have access) |
| YouTrack project | `<YOUTRACK_URL>`, key `DIP` |
| Workflow | [CONTRIBUTING.md](../CONTRIBUTING.md) |

## 10.2 Responsibilities

| Area | Lead | Backup / reviewer |
|---|---|---|
| Frontend, UX, visualization | Asylkhan Kozhanov | Alikhan |
| Backend, video processing, API | Aldiyar Bazarbayev | Alikhan |
| Integration, testing, documentation | Alikhan Sekenov | Asylkhan |

Rule: a pull request is reviewed by someone other than its author.

## 10.3 Milestones (draft; adjust to the official schedule)

| Milestone | Date | Content |
|---|---|---|
| Pre-defense 1 | 24 Oct 2026 | Analysis, design, planning; tag `pre-defense-1` |
| Interviews and evidence complete | `<date>` | 3–5 discussions logged |
| Backend + pipeline MVP | `<date>` | Upload → job → tracks, FR-01..08 |
| Frontend MVP | `<date>` | Viewer, export, FR-09..12 |
| Evaluation results | `<date>` | Metrics vs baseline |
| Pre-defense 2 | `<date>` | Tag `pre-defense-2` |
| Final pre-defense | `<date>` | Tag `final-pre-defense` |

## 10.4 YouTrack backlog to create (key DIP)

Each task needs: owner, expected outcome, acceptance criteria, deadline (deadlines below are suggestions).

| ID | Task | Owner | Acceptance criteria | Deadline |
|---|---|---|---|---|
| DIP-1 | Create repository, README, structure | Alikhan | README completed; access for supervisor | 23 Oct |
| DIP-2 | Project proposal and scope | Alikhan | `01-project-proposal.md` reviewed | 23 Oct |
| DIP-3 | Literature review | All | ≥12 sources, table, verified metadata | 24 Oct |
| DIP-4 | Existing systems comparison with hands-on checks | Aldiyar | All "to verify" cells replaced by tested facts | 30 Oct |
| DIP-5 | Technology comparison and ADRs | Aldiyar | Scores reviewed, ADRs accepted | 24 Oct |
| DIP-6 | Requirements and acceptance criteria | Alikhan | Reviewed with supervisor | 24 Oct |
| DIP-7 | Architecture diagrams | Aldiyar | 3 diagrams with sources and exports | 24 Oct |
| DIP-8 | UI prototype | Asylkhan | 4 screens clickable | 24 Oct |
| DIP-9 | Verification plan | Alikhan | Metrics, datasets, conditions defined | 24 Oct |
| DIP-10 | Conduct 3–5 interviews | All | Notes in `docs/evidence/` | 5 Nov |
| DIP-11 | Baseline B0 + tests | Aldiyar | `pytest` green | 24 Oct |
| DIP-12 | Download datasets, write loader | Alikhan | CDnet subset loads | 10 Nov |
| DIP-13 | Backend skeleton + OpenAPI | Aldiyar | `POST /api/jobs` works with stub | 14 Nov |
| DIP-14 | Detector + tracker integration | Aldiyar | Tracks produced on sample video | 28 Nov |
| DIP-15 | Motion filter + extractor | Aldiyar | FR-06..08 tests pass | 5 Dec |
| DIP-16 | Frontend skeleton + API client | Asylkhan | Upload view calls API | 21 Nov |
| DIP-17 | Results viewer with overlay | Asylkhan | FR-09 acceptance met | 12 Dec |
| DIP-18 | Export (JSON/CSV) | Alikhan | FR-11 schema validated | 12 Dec |
| DIP-19 | Evaluation CLI + first results | Alikhan | One command prints metrics table | 19 Dec |
| DIP-20 | Usability test | Asylkhan | ≥5 users, SUS computed | `<date>` |
| DIP-21 | CI: tests on pull request | Alikhan | Workflow green on PR | 21 Nov |
| DIP-22 | Docker compose setup | Aldiyar | Fresh machine runs in ≤10 commands | `<date>` |

## 10.5 Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Detector licence conflicts with intended use (Ultralytics terms to verify) | Medium | High | Read licence now; fallback RF-DETR; record in ADR | Aldiyar |
| R2 | No GPU, CPU too slow for targets | Medium | High | Smallest model, frame skipping, document measured limits, adjust NFR-01 | Aldiyar |
| R3 | Poor accuracy on small, distant or occluded objects | High | Medium | Tune thresholds, report limitations honestly, own test videos | Alikhan |
| R4 | Privacy of video of people | Medium | High | Only consented or public data; local processing; no data in repo | All |
| R5 | Interviews not arranged in time | Medium | High | Start now; fall back to client agreement or process observation | All |
| R6 | Scope creep (RTSP, zones) | Medium | Medium | Keep as *Could*; scope frozen after pre-defense 2 | Alikhan |
| R7 | Uneven contribution history | Medium | High | Per-member tasks, PR reviews, check history weekly | All |
| R8 | Benchmark dataset terms or availability | Low | Medium | Check licences; use own videos as backup | Alikhan |
| R9 | Moving camera in real footage breaks motion criterion | Medium | Medium | Document as limitation; later compensation is out of scope | Aldiyar |
| R10 | Supervisor feedback arrives late | Low | Medium | Schedule regular meetings, log in `11-supervisor-feedback.md` | Alikhan |

## 10.6 Dependencies

- Detector weights and licence (R1) → blocks DIP-14.
- Interviews (DIP-10) → may change requirements (DIP-6).
- API contract (DIP-13) → blocks frontend integration (DIP-16, 17).
- Datasets (DIP-12) → blocks evaluation (DIP-19).

## 10.7 Next steps after 24 Oct

1. Create YouTrack tasks above and link them to branches and pull requests.
2. Book interviews; log them.
3. Check the Ultralytics licence and finalize ADR-0001.
4. Start DIP-13 and DIP-16 in parallel.
