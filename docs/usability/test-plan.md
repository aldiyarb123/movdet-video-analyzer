
# DIP-21: Usability Test Plan

## 1. Objective

The purpose of this usability test is to evaluate how easily
users can interact with the MotionScope video analysis interface.

The evaluation focuses on video upload, analysis settings,
results viewing, and export functionality.

This test is related to non-functional requirement NFR-04.

## 2. Acceptance Criteria

The evaluation will check the following criteria:

- At least 5 real participants complete the usability session.
- System Usability Scale (SUS) is calculated.
- Target average SUS score: 68 or higher.
- Target task completion rate: at least 80%.

These targets are taken from the project requirements.
Actual results will be reported after testing.

## 3. Test Environment

Application: MotionScope
Frontend: React + TypeScript
Browser: Chrome, Firefox, or Edge
Platform: Windows
Test type: Moderated usability testing

The interface currently contains prototype functionality.
Object detection results may use simulated data.

## 4. Participants

At least five participants will be recruited.

Participants should have basic computer skills.
Previous experience with video analysis software is not required.

Each participant will be identified anonymously:

- P01
- P02
- P03
- P04
- P05

No personal identifying information will be collected.

## 5. Test Tasks

### Task 1: Video Upload

1. Open MotionScope.
2. Find the video upload area.
3. Select a local MP4 video.
4. Confirm that the filename is displayed.

Expected outcome:
The participant selects a video without assistance.

### Task 2: Analysis Configuration

1. Select the person and car object classes.
2. Change the confidence threshold.
3. Change the motion threshold.
4. Select a tracker.

Expected outcome:
The participant understands and adjusts analysis settings.

### Task 3: Start Analysis

1. Click Start Analysis.
2. Observe the response.
3. Explain whether the analysis was started successfully.

Expected outcome:
The participant understands the displayed job status or error.

The real backend may be unavailable during testing.
A mock server can be used and must be disclosed.

### Task 4: Results Viewer

1. Open Results Viewer.
2. Select a local video.
3. Start playback.
4. Find object bounding boxes and object IDs.
5. Disable and enable the overlay.
6. Seek to a different video position.

Expected outcome:
The participant can operate the video viewer independently.

Displayed object detections are simulated.

### Task 5: Export

1. Locate the export functionality.
2. Attempt to export an analysis report.
3. Identify whether the export was successful.

Expected outcome:
A report file is downloaded successfully.

If export is not implemented, record this task as
blocked or incomplete, rather than successful.

## 6. Data Collection

For each participant, record:

- Whether each task was completed without assistance.
- Any errors or usability difficulties.
- Time spent on each task, if measured.
- Responses to the 10 SUS questions.
- Additional participant feedback.

## 7. Success Measurement

Task success rate:

Successful unassisted attempts / Total applicable attempts * 100

The NFR-04 end-to-end scenario is:

Upload -> View -> Export

For the end-to-end criterion, count only participants
who complete the entire scenario without assistance.

End-to-end success rate:

Successful participants / Total participants * 100

## 8. SUS Scoring

The System Usability Scale contains 10 questions.

Each answer is scored from 1 to 5.

For odd-numbered questions:
Contribution = Answer - 1

For even-numbered questions:
Contribution = 5 - Answer

SUS score = Sum of contributions * 2.5

Possible scores range from 0 to 100.

The average SUS score is calculated across all participants.

## 9. Limitations

The current frontend is under development.

The results viewer uses simulated detection data.
Real API integration and full export functionality may
not be available during the usability session.

Any unavailable functionality must be documented clearly.

## 10. Evidence

Evidence may include:

- Screenshots of the tested interface.
- Anonymous task completion records.
- Completed SUS questionnaires.
- SUS calculation table.
- Summary of observed usability problems.

No participant scores or outcomes will be invented.
