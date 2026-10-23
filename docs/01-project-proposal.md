# 1. Project Proposal

## Title
Development of an Application for Automatic Analysis and Extraction of Moving Objects in a Video Stream

## Team and supervisor

| Name | Role |
|---|---|
| Asylkhan Kozhanov | Frontend, user interface, visualization of results |
| Aldiyar Bazarbayev | Backend, video processing, API |
| Alikhan Sekenov | Functional components, integration, testing, documentation |

Programme: Software Engineering · Group: SE-2416 · Supervisor: Shuryn Tutkyshbayeva

## Problem statement

People who need to know *what moved, where, and when* in a video usually have two bad options: watch it manually (slow, tiring, error-prone) or assemble a pipeline from computer-vision libraries (requires programming skill). Ready-made products exist, but each leaves a gap (see [04-existing-systems-comparison.md](04-existing-systems-comparison.md)):

- libraries (OpenCV, Ultralytics, Supervision) give building blocks but no application;
- cloud video APIs process data on a third-party server and bill per minute of video;
- camera-recording systems (e.g. Frigate) are designed around IP cameras and home-automation integration rather than analysing an arbitrary video file and extracting results.

Classical motion detection (background subtraction) is cheap but breaks under lighting changes, dynamic backgrounds and camera motion, and cannot say *what* an object is. Modern detectors recognise objects but do not by themselves say which ones are moving or give each a persistent identity ([03-literature-review.md](03-literature-review.md)). Combining detection, tracking and a motion criterion, and wrapping it in a usable interface, is the engineering problem of this project.

## Target users (hypotheses to validate, see [02](02-evidence-of-relevance.md))

1. Operators reviewing security or site recordings.
2. Students and researchers needing trajectories and clips of moving objects.
3. Analysts counting or timing movement (traffic, retail, facilities).

## Aim

Build and evaluate a web application that automatically detects, tracks and extracts moving objects from video, and demonstrate that it is more useful than a classical baseline on defined accuracy, speed and usability measures.

## Objectives

| # | Objective | Measured by |
|---|---|---|
| O1 | Establish requirements from users and analysis of existing solutions | Interviews, requirements with acceptance criteria |
| O2 | Select and justify detection, tracking and platform technologies | Technology comparison, ADRs |
| O3 | Implement a processing pipeline: detection, tracking, motion filtering, extraction | Automated tests, pipeline demo |
| O4 | Implement an API and a web UI for upload, configuration, results and export | Functional tests, usability test |
| O5 | Evaluate against a classical baseline on public benchmarks and own videos | Metrics in the verification plan |
| O6 | Document and manage the project transparently | Git history, YouTrack, documentation |

## Expected outcomes

- Working web application (MVP) deployable locally.
- Pipeline producing per-object tracks, crops, clips and a JSON/CSV report.
- Evaluation report comparing the solution with the baseline.
- Repository with documentation, diagrams, tests and traceable task history.

## Scope

**In scope (MVP)**
- Upload of video files (common formats), validation, job queue and progress display.
- Detection of objects of configurable classes; multi-object tracking with persistent IDs.
- Motion criterion: an object is *moving* if its track displaces more than a configurable threshold over a time window (static camera assumed in MVP).
- Results viewer: video with overlays, object list, timeline, filters.
- Export: JSON and CSV report, cropped images, per-object clips.
- Job history, configurable thresholds and classes, local deployment.

**Optional / later**
- Live stream input (RTSP). Line-crossing and zone counting. Alert rules.

**Out of scope**
- Face or person identification. Multi-camera re-identification. Moving-camera compensation. Model training from scratch. Multi-tenant cloud hosting.
## MVP scope decisions

The following decisions make the first version of MotionScope feasible and testable within the diploma project timeframe.

| Area | MVP decision | Reason |
|---|---|---|
| Video input | The user uploads a recorded video file. | It allows the team to focus on analysis quality before adding live-stream complexity. |
| Camera conditions | The MVP assumes a static camera. | Moving-camera compensation requires a separate stabilization approach and is outside the first release. |
| Moving-object rule | An object is treated as moving when its tracked position changes beyond a configurable threshold during a defined time window. | This makes the decision explainable and measurable during evaluation. |
| Processing location | Video processing and storage run locally. | This reduces privacy risks and avoids dependence on paid cloud video services. |
| User result | The system provides overlays, object tracks, cropped images, short clips, and JSON/CSV export. | Users can inspect results visually and use structured data in later analysis. |
| Excluded features | Face identification, multi-camera re-identification, model training from scratch, RTSP streams, and cloud multi-tenant hosting are not included in the MVP. | These features would substantially increase technical scope and evaluation effort. |
## Engineering complexity (for committee evaluation)

- Asynchronous long-running processing with job queue, progress reporting and failure handling.
- Computer-vision pipeline integrating detector, tracker and a motion criterion, with tunable parameters.
- Efficient video decoding, overlay rendering and clip extraction.
- Evaluation methodology with standard metrics (detection, tracking, change detection) and a reproducible baseline.
- A usable interface for result inspection and export, covering performance on long videos.

## Assumptions and constraints

- Static camera in MVP; moving camera is a documented limitation ([03](03-literature-review.md), [Chapel & Bouwmans]).
- Model licences must permit the intended use (see risk R1 in [10](10-project-management-and-risks.md)).
- GPU availability is not guaranteed; CPU performance targets must be measured, not assumed.
- Videos of people are personal data; only consented or public-benchmark data is used.
