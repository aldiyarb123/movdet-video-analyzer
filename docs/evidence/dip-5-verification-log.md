# DIP-5 verification log

Date: 24 October 2026. Method: downloaded the packages from PyPI without installing and read their metadata and files; read public documentation pages. No system was run on real video.

## Package checks

Command pattern: `pip download --no-deps <package>`, then read `*.dist-info/METADATA` and listed files in the wheel.

| Package | Version | Licence (from METADATA) |
|---|---|---|
| ultralytics | 8.4.184 | AGPL-3.0 |
| supervision | 0.31.1 | MIT |
| opencv-python-headless | 5.0.0.93 | Apache 2.0 |

Ultralytics `cfg/default.yaml`:
- `save_crop: False` (save cropped prediction regions), `save_txt: False`, `save_frames: False`, `vid_stride: 1`
- `tracker: tracktrack.yaml` with the comment listing botsort, bytetrack, ocsort, deepocsort, fasttrack, tracktrack
- `cfg/trackers/` contains botsort.yaml, bytetrack.yaml, deepocsort.yaml, fasttrack.yaml, ocsort.yaml, tracktrack.yaml

Supervision package: exports `CropAnnotator`, `crop_image`, `CSVSink`, `JSONSink`, `ImageSink`, `VideoSink`, `LineZone`, `PolygonZone`. No tracker module is present in 0.31.1.

## Documentation checks

- Google Cloud Video Intelligence, object tracking page: results contain bounding boxes with time segments and an entity ID; API only (REST, gcloud, client libraries); input is a Cloud Storage `inputUri` or base64 `inputContent` for a local file.
- Frigate repository page: MIT licence, trademark note for name and logo; "realtime object detection locally for IP cameras"; "Records video with retention settings based on detected objects". Docs navigation lists Exports and Snapshots; file analysis and tracked-object IDs were not confirmed on the pages read.

## Corrections this check caused

- Ultralytics can save crops with a built-in switch (earlier draft said this needed user code).
- Ultralytics licence is AGPL-3.0 (earlier draft: "check licence").
- The default tracker in the current package is `tracktrack.yaml`, not BoT-SORT as in older documentation.
- Supervision 0.31.1 contains no tracker module (older tutorials use `sv.ByteTrack`).
