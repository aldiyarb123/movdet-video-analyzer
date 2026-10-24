# 4. Existing Systems Comparison

Five systems, eight criteria. Each cell is marked with how it was checked:

- **[T]** tested or inspected directly on 24 Oct 2026 (package metadata and contents, see [evidence/dip-5-verification-log.md](evidence/dip-5-verification-log.md))
- **[D]** stated in public documentation, not run by us
- **[?]** not confirmed; needs a hands-on test (see 4.5)

## 4.1 Systems

| ID | System | Kind | Source |
|---|---|---|---|
| S1 | **Frigate NVR** | Open-source network video recorder with real-time object detection | Repository and docs [G3] |
| S2 | **Google Cloud Video Intelligence API** | Cloud service, pre-trained models | Product, pricing and object tracking pages [G4] |
| S3 | **Ultralytics YOLO tracking** | Library and CLI | Package `ultralytics` 8.4.184, docs [G1] |
| S4 | **Roboflow Supervision** | Open-source Python library | Package `supervision` 0.31.1, docs [G2] |
| S5 | **OpenCV MOG2 script** | Classical background subtraction (our baseline) | Package `opencv-python-headless` 5.0.0.93, [L1] |

## 4.2 Criteria

C1 Deployment and data location · C2 Detection approach · C3 Persistent object tracking · C4 Interface for a non-programmer · C5 Works on an uploaded video file · C6 Extraction of per-object results (crops, clips, report) · C7 Cost and licence · C8 Configurability

## 4.3 Comparison

| Criterion | S1 Frigate | S2 Google Video Intelligence | S3 Ultralytics tracking | S4 Supervision | S5 OpenCV MOG2 |
|---|---|---|---|---|---|
| **C1** | Local, for IP cameras, MQTT, Home Assistant [D] | Cloud; video goes to Google as a Cloud Storage object or base64 content in the request [D] | Local library [T] | Local library [T] | Local library [T] |
| **C2** | Low-overhead motion detection decides where to run neural detection; TensorFlow, optional Coral [D] | Pre-trained models; object tracking is one feature among labels, shots, text, faces [D] | YOLO detect, segment, pose models [D] | Model-agnostic: wraps detections from other models [D] | Gaussian-mixture background model, class-agnostic [D] |
| **C3** | Docs mention "tracked objects"; ID handling not described [D][?] | Each track is returned as its own annotation with bounding boxes per time segment and an entity ID [D] | Yes. Version 8.4.184 ships tracker configs: botsort, bytetrack, ocsort, deepocsort, fasttrack, tracktrack; the default in `default.yaml` is `tracktrack.yaml` [T] | No tracker module in version 0.31.1 [T]. Older tutorials use `sv.ByteTrack`; with this version tracking must come from another package [?] | No (needs extra code) |
| **C4** | Built-in web UI [D] | None: REST, gcloud CLI and client libraries only [D] | CLI and Python API only [T] | Python API only [T] | None |
| **C5** | Built for live camera streams; analysing recorded files is not stated on the pages read [?] | Yes (stored or local video file) [D] | Yes (`source=` video path) [D] | Yes (frame-by-frame processing) [D] | Yes [T] |
| **C6** | Records video with retention by detected objects; docs list Exports and Snapshots sections [D][?] | Returns annotations only; no clips or crops [D] | Built-in switches `save_crop`, `save_txt`, `save_frames` (all default False) [T]. Per-track clips need user code | `CropAnnotator`, `crop_image`, `CSVSink`, `JSONSink`, `ImageSink`, `VideoSink`, `LineZone`, `PolygonZone` exist [T]. Per-track clips need user code | Masks and boxes only |
| **C7** | MIT licence for the code; name and logo are trademarks [D]. Coral hardware optional | Per-minute price: object tracking $0.15 per minute after the first 1,000 free minutes per month (stored video) [D] | **AGPL-3.0** [T] | **MIT** [T] | **Apache 2.0** [T] |
| **C8** | Config file settings [D] | API options only [D] | `conf`, `iou`, `tracker`, `classes`, `vid_stride` and more in `default.yaml` [T] | Zones and line counters via code [D] | Thresholds in code |

## 4.4 What the comparison shows

1. **Libraries (S3, S4, S5)** are flexible and local but are not applications. Ultralytics can already save crops with one switch; per-track clips, a report and a review interface still need programming.
2. **Cloud API (S2)** needs no setup but sends the video to Google and bills per minute. Its output is annotations only, with no interface.
3. **Frigate (S1)** is the closest product, but its stated purpose is real-time detection for IP cameras with home-automation integration. Whether it can analyse an arbitrary recorded file and export per-object results was not confirmed.
4. **Licence finding that affects our project (R1):** Ultralytics is AGPL-3.0. If we use it, our code must be handled under AGPL terms (source made available to users of the network service) unless a separate commercial licence is obtained. For an open-source diploma project this can be acceptable, but the team must decide consciously; RF-DETR remains the fallback. This is a technical note, not legal advice: confirm with the supervisor.
5. **Gap:** none of the reviewed systems was confirmed to combine (a) local processing, (b) a GUI for non-programmers, (c) analysis of an uploaded video file, and (d) per-object extraction of crops and clips together with a report. This is the niche of MotionScope.

## 4.5 What was not tested and what the team must do

| System | Not done | Needed |
|---|---|---|
| S1 Frigate | Not run (needs Docker and a camera or test stream) | Install with Docker; try a recorded video; check tracked-object IDs, Exports, Snapshots; add screenshots to `docs/evidence/` |
| S3 Ultralytics | Not run on real video (needs model weights and a real video) | `pip install ultralytics`, run `yolo track` on a short clip, check `save_crop` output; save a screenshot |
| S4 Supervision | Tracker location not confirmed | Check the current docs for the package that provides ByteTrack |
| S2 Google | Not run | Optional: run the free tier on one short clip |

Cells marked [?] stay open until that is done; do not present them as facts.

## 4.6 Limits

- Prices and features change; this table records 24 October 2026.
- Package contents are those of the versions named in 4.1.
