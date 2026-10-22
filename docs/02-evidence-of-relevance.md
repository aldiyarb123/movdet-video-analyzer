# 2. Evidence of Relevance

> **Status: NOT YET COLLECTED.** The committee requires 3–5 discussions with user representatives or a substantive agreement with a real client. This file contains the plan, the interview guide and the log to fill in. Nothing below is presented as a finding until the team has real notes. Verified findings and assumptions are kept separate on purpose.

## 1. Plan

| Item | Plan |
|---|---|
| Method | 20–30 minute semi-structured interviews (in person or video call) |
| Number | 3–5 representatives, at least 2 distinct user types |
| Candidates | Security staff at a university or building; a researcher or lab that analyses video; a traffic or retail analyst; a small business owner with cameras |
| Consent | Ask permission to take notes; do not record voice or store personal data without written consent |
| Output | One note per interview in `docs/evidence/interview-NN.md`, then fill the tables below |

## 2. Interview guide

1. What video do you work with (source, length, quality, volume per week)?
2. Which questions do you try to answer from it ("who entered", "how many vehicles", "when did something move")?
3. How do you do this today? How long does it take? What goes wrong?
4. What tools have you tried? What stopped you from using them?
5. What would the ideal output look like (clips, images, table, alerts)?
6. Where does the video live, and can it leave your computer or network?
7. What would make you trust the result (accuracy, ability to review)?
8. Show the prototype ([../prototype/index.html](../prototype/index.html)) and observe: what is unclear, what is missing?

## 3. Interview log (fill in)

| # | Date | Person / role (anonymised) | Type | Notes file | Key requirements raised |
|---|---|---|---|---|---|
| 1 | | | | `evidence/interview-01.md` | |
| 2 | | | | `evidence/interview-02.md` | |
| 3 | | | | `evidence/interview-03.md` | |
| 4 | | | | | |
| 5 | | | | | |

## 4. Verified findings vs. assumptions

| ID | Statement | Status | Evidence |
|---|---|---|---|
| A1 | Users review video manually to find moving objects | **Assumption** | Pending interviews |
| A2 | Users want extracted clips/crops, not only detection boxes | **Assumption** | Pending interviews |
| A3 | Users prefer local processing for privacy | **Assumption** | Pending interviews |
| A4 | Cloud APIs are too costly or unsuitable for the intended volume | **Partly supported** | Per-minute pricing of Google Video Intelligence object tracking is published ([04](04-existing-systems-comparison.md)); whether it is "too costly" depends on user volume (pending) |
| A5 | Existing libraries need programming skill to produce a usable result | **Supported by documentation** | Ultralytics and Supervision are code/CLI-based ([04](04-existing-systems-comparison.md)) |
| A6 | Classical background subtraction fails under dynamic backgrounds, lighting change and camera motion | **Supported by literature** | [03](03-literature-review.md) (Kumar & Yadav 2016; Chapel & Bouwmans 2020) |

Rule: an item moves from *Assumption* to *Verified* only when it links to a real interview note, data analysis or an agreement.

## 5. Alternative evidence (if interviews are hard to arrange)

- A short written agreement with a real client who states the need and agrees to test the system.
- Analysis of available data (for example, the length and number of recordings a university security office holds).
- Observation of a real review process, with notes.
