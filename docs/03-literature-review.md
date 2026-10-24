# 3. Literature Review

> Sources were located through web search in October 2026. Metadata not visible in the search results (marked ⚠) must be checked against the publisher page before the final citation list is frozen. Numbers quoted below are taken from the cited abstracts or pages.

## 3.1 Scope of the review

The project combines three technical areas: (1) detecting moving regions or objects, (2) tracking objects across frames, (3) evaluating the result. The review follows that order and ends with the limitations that shape the project.

## 3.2 Classical motion detection: background subtraction

Background subtraction models the scene background per pixel and flags pixels that deviate. Zivkovic's improved adaptive Gaussian mixture model [L1] is the basis of OpenCV's `BackgroundSubtractorMOG2`, which we use as the baseline. Sobral and Vacavant [L2] compared 29 background-subtraction methods from BGSLibrary on the BMC dataset for robustness and processor/memory cost, showing that the field is large and that practical cost differs between methods. The known weakness is the non-static scene: Kumar and Yadav [L3] list rippling water, moving curtains and illumination change as conditions that degrade subtraction-based segmentation.

A moving camera is a separate and harder case. Chapel and Bouwmans [L4] state that earlier surveys concentrate on the static camera and review methods for moving cameras, grouped into classes such as background modelling with motion compensation and trajectory classification. Yao et al. [L5] survey video object segmentation and tracking and describe the classic pipeline of background model, deviation, connected components.

**Take-away:** cheap and needs no training, but class-agnostic and fragile. Good baseline, weak final solution. A moving camera is out of MVP scope.

## 3.3 Deep object detection

YOLO reframes detection as a single regression problem and predicts boxes and classes in one forward pass, which suits real-time use. Terven and Cordova-Esparza [L6] review YOLOv1 to YOLOv8 and YOLO-NAS. Kotthapalli et al. [L7] extend the survey to YOLOv11 and note that early versions struggled with small objects and had lower localisation precision than two-stage detectors, while later versions (CSP-based backbones, GELAN) address efficiency. Ramos and Sappa [L8] review a decade of YOLO up to YOLOv13, including deployment and ethical implications. Zulfqar et al. [L9] give a broader overview of deep models for object detection in video and images, and the traffic-video survey [L10] reviews detectors and foreground detection for traffic scenes.

**Take-away:** detectors give class labels and are robust to illumination changes, but a detector alone does not say whether an object *moves* and gives no identity across frames. Small and distant objects remain a known weakness.

## 3.4 Multi-object tracking

The dominant paradigm is tracking-by-detection. SORT [L11] combines a Kalman filter for motion prediction with the Hungarian algorithm for association and reports an update rate of 260 Hz; its authors argue that adding re-identification adds overhead that limits real-time use. DeepSORT [L12] adds a deep appearance metric learned offline on a person re-identification dataset and reports a 45% reduction in identity switches. ByteTrack [L13] associates almost every detection box, including low-score ones, instead of discarding them; the paper reports 80.3 MOTA, 77.3 IDF1 and 63.1 HOTA on MOT17 at 30 FPS on one V100 GPU, and an IDF1 gain of 1 to 10 points when applied to nine other trackers.

A comparison on SoccerNet-Tracking [L14] shows that detection quality dominates: with ground-truth detections DeepSORT and ByteTrack reach HOTA 69.6 and 71.5, but with real detections the values fall to 36.7 and 47.2. Practical guidance published in October 2026 [G5] suggests SORT for simple scenes, DeepSORT when crowded objects cross, ByteTrack for blurred, partly hidden or low-confidence detections, and OC-SORT for sudden direction changes. Ultralytics supports BoT-SORT and ByteTrack out of the box [G1]; the package version 8.4.184 checked on 24 Oct 2026 also ships OC-SORT and other trackers and uses a different default tracker than older documentation (see [04](04-existing-systems-comparison.md)).

**Take-away:** ByteTrack is a strong default without an appearance model. A tracker cannot repair poor detections, so detector choice and evaluation on our own footage matter.

## 3.5 Benchmarks and metrics

CDnet 2014 [L15] is a pixel-annotated change-detection benchmark (53 videos, 11 categories in later descriptions of the dataset) with challenges such as bad weather, night and dynamic background; its metrics are recall, specificity, FPR, FNR, PWC, F-measure and precision. MOT20 [L16] provides 8 sequences from 3 very crowded scenes (up to 246 pedestrians per frame) for tracking evaluation. Tracking quality is reported with MOTA, IDF1 and HOTA, used by [L13] and [L14].

**Take-away:** CDnet suits evaluation of the motion-detection stage and the baseline; MOTChallenge-style data and metrics suit the tracking stage. Public benchmarks do not match our footage, so own labelled videos are also needed.

## 3.6 Gaps and limitations the project takes into account

1. No source above delivers an end-user application that turns a video file into extracted per-object clips; they provide algorithms, benchmarks or libraries.
2. Moving-camera scenes remain a research problem [L4]; MVP assumes a static camera.
3. Tracking quality depends on detector quality [L14]; thresholds must be tuned and measured.
4. Benchmarks emphasise pedestrians and vehicles; other classes need own data.
5. Detector licence and privacy of video data are practical constraints (risks R1, R4).

## 3.7 Structured analysis table

| ID | Source | Year | Type | Topic | Main contribution used | Limitation / relevance |
|---|---|---|---|---|---|---|
| L1 | Zivkovic, *Improved adaptive Gaussian mixture model for background subtraction*, ICPR | 2004 | Conference (foundational) | Background subtraction | Algorithm behind OpenCV MOG2 (baseline) | Class-agnostic; old; sensitive to dynamic scenes |
| L2 | Sobral & Vacavant ⚠, *A comprehensive review of background subtraction algorithms evaluated with synthetic and real videos*, Computer Vision and Image Understanding | 2014 | Journal | BS review | Compares 29 methods on BMC for robustness and CPU/memory | Pre-deep-learning |
| L3 | Kumar & Yadav, *Segmentation of Moving Objects using Background Subtraction Method in Complex Environments*, Radioengineering 25(2) | 2016 | Journal | BS in complex scenes | Lists failure conditions (water, curtains, illumination) | Not real-time per its own discussion of MRF methods |
| L4 | Chapel & Bouwmans ⚠, *Moving Objects Detection with a Moving Camera: A Comprehensive Review*, arXiv 2001.05238 (Computer Science Review) | 2020 | Survey | Moving camera | Taxonomy; shows static-camera focus of earlier surveys | Defines out-of-scope case for MVP |
| L5 | Yao et al., *Video Object Segmentation and Tracking: A Survey*, arXiv 1904.09172 | 2019/2020 | Survey | VOS and tracking | Classic BS pipeline and segmentation-based tracking | Segmentation focus, wider than our scope |
| L6 | Terven & Cordova-Esparza, *A Comprehensive Review of YOLO Architectures in Computer Vision: From YOLOv1 to YOLOv8 and YOLO-NAS*, arXiv 2304.00501 (Machine Learning and Knowledge Extraction) | 2023 | Survey | YOLO | Architecture evolution, single-pass detection | Ends at v8 |
| L7 | Kotthapalli et al., *YOLOv1 to YOLOv11: A Comprehensive Survey of Real-Time Object Detection Innovations and Challenges*, arXiv 2508.02067 | 2025 | Survey (preprint) | YOLO | Small-object and localisation limits; deployment notes | Preprint |
| L8 | Ramos & Sappa, *A Decade of You Only Look Once (YOLO) for Object Detection: A Review*, arXiv 2504.18586 | 2025 | Survey (preprint) | YOLO | Evolution to v13, ethics, constraints | Preprint |
| L9 | Zulfqar et al., *A comprehensive overview of deep learning models for object detection from videos/images*, arXiv 2601.14677 | 2026 | Survey (preprint) | Video detection | Current effectiveness of semantic detection | Preprint |
| L10 | *Object Detection in Traffic Videos: A Survey*, vol. 24(7) ⚠ authors and journal to confirm | 2023 | Journal survey | Traffic video | Foreground detection and instance segmentation for traffic | Domain-specific |
| L11 | Bewley et al., *Simple online and realtime tracking*, ICIP, doi:10.1109/ICIP.2016.7533003 | 2016 | Conference (foundational) | MOT | Kalman + Hungarian, 260 Hz; detector quality matters | No appearance, weak on occlusion |
| L12 | Wojke et al., *Simple Online and Realtime Tracking with a Deep Association Metric*, ICIP, doi:10.1109/ICIP.2017.8296962 | 2017 | Conference (foundational) | MOT | Appearance metric, 45% fewer ID switches | Needs re-ID model; heavier |
| L13 | Zhang et al., *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*, ECCV | 2022 | Conference | MOT | Associates low-score boxes; MOT17 80.3 MOTA, 30 FPS | Depends on detector; no appearance cue |
| L14 | *SoccerNet-Tracking: Multiple Object Tracking Dataset and Benchmark in Soccer Videos*, arXiv 2204.06918 ⚠ authors | 2022 | Benchmark paper | MOT evaluation | Shows DeepSORT/FairMOT/ByteTrack gap with and without GT detections | Sports domain |
| L15 | Wang et al., *CDnet 2014: An Expanded Change Detection Benchmark Dataset*, CVPR Workshops, doi:10.1109/CVPRW.2014.126 | 2014 | Conference (dataset) | Evaluation | Dataset, categories, metrics for change detection | Fixed-camera videos, older |
| L16 | Dendorfer et al., *MOT20: A benchmark for multi object tracking in crowded scenes*, arXiv 2003.09003 | 2020 | Benchmark paper | Evaluation | Crowded-scene tracking benchmark, HOTA/MOTA/IDF1 context | Pedestrian only |

Grey sources (documentation and practice, not scientific publications):

| ID | Source | Use |
|---|---|---|
| G1 | Ultralytics docs, *Multi-Object Tracking with Ultralytics YOLO* (docs.ultralytics.com/modes/track) | Supported trackers, tracker config, API (default tracker differs by version, see doc 04) |
| G2 | Roboflow *Supervision* documentation | Detections, tracking, zones |
| G3 | Frigate NVR repository and documentation | Existing system comparison |
| G4 | Google Cloud Video Intelligence API pricing | Existing system comparison |
| G5 | Roboflow blog, *SORT vs DeepSORT vs ByteTrack vs OC-SORT*, 19 Oct 2026 | Tracker choice guidance |

## 3.8 Compliance with the committee requirement

- **At least 12 meaningfully used sources:** 16 academic + 5 documentation sources, each used above.
- **At least 8 scientific publications:** 16 listed (journal, conference, survey, benchmark). Four are arXiv preprints (L7, L8, L9, L14); the team should cite published versions where they exist.
- **Recent core (last five years):** L6, L7, L8, L9, L10, L13, L14 are from 2022–2026; L16 is from 2020. Foundational works (L1, L11, L12, L15) are kept deliberately. **Recommended:** add 3–4 more recent (2021–2026) peer-reviewed papers, for example on transformer-based real-time detectors and on deep-learning motion detection, so the recent core is stronger.

## 3.9 To verify before submission

- ⚠ Confirm authors and venue for L2, L4, L10, L14 on the publisher or arXiv page.
- Replace preprint citations with published versions where available.
- Each member should read and annotate their share of sources (suggested split: L1–L5 Alikhan, L6–L10 Asylkhan, L11–L16 Aldiyar) and be ready to explain them at the defense.
