# 4. Existing Systems Comparison

Five systems, eight criteria. Every cell is limited to what the cited source states. Cells marked **to verify** must be checked by the team by installing and testing the system; they are not claims.

## 4.1 Systems

| ID | System | Kind | Source |
|---|---|---|---|
| S1 | **Frigate NVR** | Open-source network video recorder with real-time object detection | Project repository and docs [G3] |
| S2 | **Google Cloud Video Intelligence API** | Cloud service, pre-trained models | Product and pricing pages [G4] |
| S3 | **Ultralytics YOLO tracking** | Library and CLI | Ultralytics docs [G1] |
| S4 | **Roboflow Supervision** | Open-source Python library | Supervision docs [G2] |
| S5 | **OpenCV MOG2 script** | Classical background subtraction (our baseline) | OpenCV docs, Zivkovic [L1] |

## 4.2 Criteria

C1 Deployment and data location · C2 Detection approach · C3 Persistent object tracking · C4 Interface for a non-programmer · C5 Works on an uploaded video file · C6 Extraction of per-object results (crops/clips/report) · C7 Cost and licence · C8 Configurability (thresholds, classes, zones)

## 4.3 Comparison

| Criterion | S1 Frigate | S2 Google Video Intelligence | S3 Ultralytics tracking | S4 Supervision | S5 OpenCV MOG2 |
|---|---|---|---|---|---|
| **C1** | Local; runs on user hardware, designed for Home Assistant, communicates over MQTT | Cloud; video is sent to Google | Local library | Local library | Local library |
| **C2** | Low-overhead motion detection decides where to run neural object detection (TensorFlow, optional Google Coral accelerator) | Pre-trained models; object tracking is one feature among labels, shots, text, faces | YOLO detect/segment/pose models | Model-agnostic; wraps detections from many models | Gaussian-mixture background model; class-agnostic |
| **C3** | Not stated in the sources reviewed (**to verify**) | Object tracking feature offered | Yes: BoT-SORT (default) and ByteTrack with persistent IDs | Yes: tracking with persistent IDs, ByteTrack used in docs | No (needs extra code) |
| **C4** | Built-in web UI with events view | API (console/client libraries); no review UI built for our use case (**to verify**) | CLI and Python API only | Python API only | None |
| **C5** | Focus is IP-camera streams and recording (**to verify** file analysis) | Stored video annotation supported | Yes (`model.track(source=...)`) | Yes (processes video frames) | Yes |
| **C6** | Records video with retention based on detected objects; events and exports in UI | Returns annotations via API; clips/crops not provided by the service itself (**to verify**) | Output includes track IDs; saving crops/clips needs user code | Annotators, zones, line counting; clip/crop export needs user code | Masks and boxes only |
| **C7** | Open source; donations accepted; Coral hardware optional | Pay per minute: object tracking listed at $0.15 per minute after the first 1,000 free minutes per month (stored video) | Open source; **check licence terms** (see risk R1) | MIT licence | Open source (licence **to verify**) |
| **C8** | Retention and detection settings in config | Limited to API options (**to verify**) | Confidence, IoU, tracker YAML configuration | Zones and line counters via code | Thresholds in code |

Sources: Frigate repository README; Google Cloud Video Intelligence pricing page; Ultralytics tracking documentation; Supervision documentation and Roboflow tutorials; OpenCV documentation.

## 4.4 What the comparison shows

1. **Libraries (S3, S4, S5)** are flexible and local but are not applications. Producing a reviewable result needs programming.
2. **Cloud API (S2)** removes the setup but sends video off the machine and bills per minute. For a long recording the cost is predictable from the published rate (for example, 100 hours of video is 6,000 minutes; this exceeds the free tier).
3. **Frigate (S1)** is the closest product, but its stated purpose is a camera recorder integrated with home automation, not analysis and extraction of results from an arbitrary video file.
4. **Gap:** no reviewed system combines (a) local processing, (b) a GUI for non-programmers, (c) analysis of an uploaded video file, (d) per-object extraction of crops and clips with a report. This is the niche of MotionScope.

## 4.5 Limits of this comparison

- Information comes from public documentation, not hands-on tests. Before the defense, the team should install S1, S3 and S4 and replace every **to verify** with a tested result and a screenshot in `docs/evidence/`.
- Prices and features change; the table records the state in October 2026.
- Frigate and similar systems may be extended by users in ways not covered here.
