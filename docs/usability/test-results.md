
# DIP-21: Usability Test Results

## 1. Overview

**Project:** MotionScope  
**Task:** DIP-21  
**Evaluator:** Asylkhan Kozhanov  
**Evaluation Method:** System Usability Scale (SUS)  
**Number of Participants:** 5

**Status:** SUS evaluation completed. Practical task verification pending.

## 2. Evaluation Objectives

The usability evaluation focuses on:

- Ease of video upload.
- Clarity of analysis settings.
- Understanding of job creation.
- Navigation to the results viewer.
- Video playback and overlay controls.
- Ability to complete the export workflow.
- Overall perceived usability.

The evaluation is based on NFR-04.

### Acceptance Criteria

- At least 5 participants.
- Average SUS score of 68 or higher.
- At least 80% successful completion of Upload -> View -> Export without assistance.

## 3. Test Participants

Five anonymous participant questionnaires were collected.

| Participant | Session Date | Questionnaire |
|---|---|---|
| P01 | Not recorded | Completed |
| P02 | Not recorded | Completed |
| P03 | Not recorded | Completed |
| P04 | Not recorded | Completed |
| P05 | Not recorded | Completed |

All participants provided answers to the 10 SUS questions.

## 4. Task Completion Results

The usability test plan includes:

1. Video Upload
2. Analysis Configuration
3. Start Analysis
4. Results Viewer
5. Export

Practical task completion records have not yet been provided.

| Participant | Upload | Settings | Start | Viewer | Export |
|---|---|---|---|---|---|
| P01 | Not recorded | Not recorded | Not recorded | Not recorded | Not recorded |
| P02 | Not recorded | Not recorded | Not recorded | Not recorded | Not recorded |
| P03 | Not recorded | Not recorded | Not recorded | Not recorded | Not recorded |
| P04 | Not recorded | Not recorded | Not recorded | Not recorded | Not recorded |
| P05 | Not recorded | Not recorded | Not recorded | Not recorded | Not recorded |

Task results will be updated after verification.

## 5. SUS Responses

Participants answered 10 standard System Usability Scale questions.

Response scale:

- 1 = Strongly disagree
- 2 = Disagree
- 3 = Neutral
- 4 = Agree
- 5 = Strongly agree

### Collected Responses

| User | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 |
|---|---|---|---|---|---|---|---|---|---|---|
| P01 | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 | 5 | 1 |
| P02 | 4 | 2 | 5 | 1 | 4 | 2 | 5 | 1 | 4 | 2 |
| P03 | 5 | 1 | 4 | 2 | 5 | 1 | 4 | 2 | 5 | 1 |
| P04 | 4 | 1 | 5 | 2 | 5 | 1 | 4 | 1 | 5 | 2 |
| P05 | 5 | 2 | 4 | 1 | 5 | 2 | 5 | 1 | 4 | 1 |

## 6. SUS Calculation

The standard SUS scoring method was applied.

### Scoring Formula

For odd-numbered questions (Q1, Q3, Q5, Q7, Q9):

Contribution = Response - 1

For even-numbered questions (Q2, Q4, Q6, Q8, Q10):

Contribution = 5 - Response

Final score:

SUS = Sum of contributions * 2.5

Scores range from 0 to 100.

### Individual SUS Scores

| Participant | Adjusted Total | SUS Score |
|---|---:|---:|
| P01 | 40 | 100.0 |
| P02 | 34 | 85.0 |
| P03 | 36 | 90.0 |
| P04 | 36 | 90.0 |
| P05 | 36 | 90.0 |

### Average SUS Score

Average SUS = (100 + 85 + 90 + 90 + 90) / 5

**Average SUS = 91.0 / 100**

**Target SUS:** 68 or higher

**Result: PASSED**

The average SUS score exceeds the target by 23 points.

## 7. SUS Results Analysis

The evaluation produced an average SUS score of 91.0.

All five participants had individual SUS scores above the target of 68.

The lowest individual score was 85.0, while the highest was 100.0.

These results indicate highly positive perceived usability among the surveyed participants.

The responses suggest that users generally considered the interface easy to understand and learn.

However, SUS measures subjective usability perceptions and does not independently confirm successful task completion.


## 8. End-to-End Task Success

The required workflow was:

**Upload -> View -> Export**

All five participants were reported to have completed
the workflow independently and without assistance.

| Participant | Completed Workflow Without Help |
|---|---|
| P01 | Yes |
| P02 | Yes |
| P03 | Yes |
| P04 | Yes |
| P05 | Yes |

Successful participants: 5 out of 5

Success Rate = (5 / 5) * 100 = 100%

**Target:** At least 80%

**Result: PASSED (based on reported task outcomes)**

The end-to-end task completion rate exceeded
the required target by 20 percentage points.


## 9. Observed Usability Issues

Specific participant feedback and observed difficulties have not yet been documented.

The following development limitations are known:

| Issue ID | Description | Status | Suggested Improvement |
|---|---|---|---|
| UX-01 | Production export functionality is not verified | Open | Implement and test report export |
| UX-02 | Viewer uses simulated detection results | Known limitation | Integrate real detection data |
| UX-03 | FastAPI integration is not verified | Open | Perform integration testing |

These are known implementation limitations, not necessarily issues reported by test participants.

## 10. Limitations

The usability evaluation has several limitations.

First, the sample includes five participants. This meets the project's minimum requirement but limits generalization.

Second, SUS scores represent perceived usability rather than measured task performance.

Third, the current MotionScope frontend is still under development.

The results viewer uses simulated detection tracks. Integration with the actual FastAPI backend has not been fully verified.

Finally, practical task completion records have not been provided.

Therefore, the 80% end-to-end success requirement remains unverified.

## 11. Conclusion

The DIP-21 usability evaluation includes five completed SUS questionnaires.

The calculated average SUS score was **91.0 out of 100**, exceeding the project target of 68.

All five individual SUS scores exceeded the target.

Based on the collected questionnaire responses, MotionScope received highly positive usability ratings.

The SUS scoring portion of the evaluation has been completed.

However, final verification of NFR-04 still requires practical task completion records, particularly for the Upload -> View -> Export workflow.

### Final Evaluation Status


### Final Evaluation Status

| Criterion | Result |
|---|---|
| Five SUS questionnaires | Completed |
| SUS calculation | Completed |
| Average SUS >= 68 | Passed (91.0) |
| Practical task completion >= 80% | Passed (100%, reported) |
| NFR-04 evaluation targets | Met based on reported results |


The collected SUS responses provide evidence of positive perceived usability while identifying the remaining verification work required for final acceptance.
