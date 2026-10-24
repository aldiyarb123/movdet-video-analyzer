# 10. Project Management and Risks

## 10.1 Tools

| Item | Value |
|---|---|
| Git repository | `https://github.com/aldiyarb123/movdet-video-analyzer` (GitHub or GitLab; supervisor and committee have access) |
| YouTrack project | `https://movdet-video-analyzer.youtrack.cloud/projects/DIP`, key `DIP` |
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

## 10.4 YouTrack backlog (project key DIP; IDs match YouTrack)

Imported into YouTrack on 23 Oct 2026. The first YouTrack number is DIP-2 (DIP-1 was an empty placeholder and was deleted); the initial repository commit is therefore recorded under `DIP-1` in git history only.

Each task needs: owner, expected outcome, acceptance criteria, deadline (deadlines below are suggestions).

| ID | Task | Owner | Acceptance criteria | Deadline |
|---|---|---|---|---|
| DIP-2 | Create repository, README, structure | Alikhan | README completed; access for supervisor | 23 Oct |
| DIP-3 | Project proposal and scope | Alikhan | `01-project-proposal.md` reviewed | 23 Oct |
| DIP-4 | Literature review | All | ≥12 sources, table, verified metadata | 24 Oct |
| DIP-5 | Existing systems comparison with hands-on checks | Aldiyar | All "to verify" cells replaced by tested facts | 30 Oct |
| DIP-6 | Technology comparison and ADRs | Aldiyar | Scores reviewed, ADRs accepted | 24 Oct |
| DIP-7 | Requirements and acceptance criteria | Alikhan | Reviewed with supervisor | 24 Oct |
| DIP-8 | Architecture diagrams | Aldiyar | 3 diagrams with sources and exports | 24 Oct |
| DIP-9 | UI prototype | Asylkhan | 4 screens clickable | 24 Oct |
| DIP-10 | Verification plan | Alikhan | Metrics, datasets, conditions defined | 24 Oct |
| DIP-11 | Conduct 3–5 interviews | All | Notes in `docs/evidence/` | 5 Nov |
| DIP-12 | Baseline B0 + tests | Aldiyar | `pytest` green | 24 Oct |
| DIP-13 | Download datasets, write loader | Alikhan | CDnet subset loads | 10 Nov |
| DIP-14 | Backend skeleton + OpenAPI | Aldiyar | `POST /api/jobs` works with stub | 14 Nov |
| DIP-15 | Detector + tracker integration | Aldiyar | Tracks produced on sample video | 28 Nov |
| DIP-16 | Motion filter + extractor | Aldiyar | FR-06..08 tests pass | 5 Dec |
| DIP-17 | Frontend skeleton + API client | Asylkhan | Upload view calls API | 21 Nov |
| DIP-18 | Results viewer with overlay | Asylkhan | FR-09 acceptance met | 12 Dec |
| DIP-19 | Export (JSON/CSV) | Alikhan | FR-11 schema validated | 12 Dec |
| DIP-20 | Evaluation CLI + first results | Alikhan | One command prints metrics table | 19 Dec |
| DIP-21 | Usability test | Asylkhan | ≥5 users, SUS computed | `<date>` |
| DIP-22 | CI: tests on pull request | Alikhan | Workflow green on PR | 21 Nov |
| DIP-23 | Docker compose setup | Aldiyar | Fresh machine runs in ≤10 commands | `<date>` |

## 10.5 Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Detector licence conflicts with intended use (Ultralytics is AGPL-3.0, verified) | Medium | High | Read licence now; fallback RF-DETR; record in ADR | Aldiyar |
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

- Detector weights and licence (R1) → blocks DIP-15.
- Interviews (DIP-11) → may change requirements (DIP-7).
- API contract (DIP-14) → blocks frontend integration (DIP-17, 17).
- Datasets (DIP-13) → blocks evaluation (DIP-20).

## 10.7 Next steps after 24 Oct

1. Create YouTrack tasks above and link them to branches and pull requests.
2. Book interviews; log them.
3. Check the Ultralytics licence and finalize ADR-0001.
4. Start DIP-14 and DIP-17 in parallel.
