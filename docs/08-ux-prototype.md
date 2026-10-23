
# 8. UX and Prototype

## 8.1 Overview

MotionScope is a video analysis application designed to
detect, track, and identify moving objects in recorded videos.

For DIP-9, an interactive UI prototype was reviewed and improved.

The prototype contains four clickable screens and demonstrates
the intended user workflow without requiring a backend service.

Prototype location:
`prototype/index.html`

The prototype runs directly in a web browser.

## 8.2 Prototype Screens

### Screen 1: New Analysis

The user can:
- Select a local video file.
- Drag and drop a video.
- Choose object classes.
- Adjust the confidence threshold.
- Configure the motion threshold.
- Select a tracking algorithm.
- Start simulated analysis.

Supported file extensions:
MP4, AVI, MOV, MKV.

The prototype applies a 500 MB file-size limit.

### Screen 2: Analysis Progress

The screen demonstrates:
- Analysis progress percentage.
- Five processing stages.
- A progress bar.
- Cancellation.
- Navigation to the results screen.

Progress is simulated using JavaScript.

### Screen 3: Results Viewer

The prototype demonstrates:
- Object bounding boxes.
- Track IDs and object classes.
- Moving and stationary object labels.
- Playback and seeking controls.
- Object filtering.
- Object timeline.
- Overlay visibility toggle.
- Demo JSON report export.

Objects and tracking results use simulated data.

Real video playback with frame-synchronized overlays
will be implemented separately under DIP-18.

### Screen 4: Analysis History

The history screen displays example jobs with statuses:
- Done
- Running
- Failed

Users can navigate to example results and remove
a failed example job from the demonstration table.

History data is not stored in a database.

## 8.3 Improvements in DIP-9

The prototype was refined with:

1. Local file selection.
2. Drag-and-drop file interaction.
3. File extension and size validation.
4. Keyboard support for the upload area.
5. Progress reset for repeated demonstrations.
6. Interactive object list and timeline.
7. Simulated JSON export.
8. Clear labeling of simulated functionality.

The original four-screen design was retained.

## 8.4 Prototype Limitations

The prototype does not perform real video analysis.

It does not:
- Upload files to an API.
- Run an object detection model.
- Perform real video tracking.
- Save jobs to a database.
- Generate real object clips or crops.

The frontend API integration is planned under DIP-17.

The real results viewer is planned under DIP-18.

Usability evaluation is planned under DIP-21.

## 8.5 Verification Checklist

The following checks should be completed manually
in a browser before the DIP-9 pull request is merged:

- [ ] All four screens can be opened.
- [ ] A supported video can be selected.
- [ ] Unsupported file extensions are rejected.
- [ ] Files above 500 MB are rejected.
- [ ] Drag and drop works.
- [ ] Start analysis activates after file selection.
- [ ] Simulated progress reaches 100%.
- [ ] Cancel returns to New Analysis.
- [ ] Open results displays demo objects.
- [ ] Object filters update the list.
- [ ] Overlay visibility can be toggled.
- [ ] History navigation works.
- [ ] Demo JSON report can be downloaded.

## 8.6 Evidence

Capture screenshots after testing:

- `docs/evidence/dip-9-new-analysis.png`
- `docs/evidence/dip-9-progress.png`
- `docs/evidence/dip-9-results.png`
- `docs/evidence/dip-9-history.png`

Only completed and verified actions should be
marked as passed in the final pull request.

## 8.7 Conclusion

DIP-9 provides an interactive four-screen prototype
of the MotionScope video analysis application.

The prototype is intended to demonstrate navigation,
user interactions, and the future system workflow.

It is not the final production frontend.
