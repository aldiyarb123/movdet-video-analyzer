# 8. UX and Prototype

Open the clickable mockup: [`../prototype/index.html`](../prototype/index.html) (any browser, no install). Data is simulated; it shows the interaction, not real analysis.

Screenshots: `evidence/prototype-*.png`.

## 8.1 Key user scenarios

| Scenario | Steps | Screen |
|---|---|---|
| S1 Analyse a recording | Choose video → pick classes and thresholds → start | New analysis |
| S2 Follow a job | See stage and percentage; cancel if needed | Progress |
| S3 Inspect results | Play with overlay; click an object to jump to it; filter by moving / class | Results |
| S4 Take the output | Download clip, crops, report | Results |
| S5 Come back later | Open an earlier job; delete a failed one | History |

## 8.2 Screens

1. **New analysis**: drop area, class chips, confidence slider, motion threshold, tracker, what to save. Start is disabled until a file is chosen.
2. **Progress**: stage list with current step, percentage bar, cancel.
3. **Results**: video with canvas overlay (box, ID, class), seek bar, timeline of when each object is present, filterable object list, export actions.
4. **History**: table of jobs with status (done, running, failed with reason).

## 8.3 Design decisions

- Settings have plain-language hints ("more objects / fewer false alarms") for non-programmers.
- Moving and static objects are visibly distinct (label and pill) because the motion criterion is the project's core idea.
- The overlay can be switched off to judge the raw video.
- Failures give a reason (FR-03, NFR-05).
- Light and dark themes follow the system setting.

## 8.4 API interaction (for external systems)

The same functions are available through the REST API; request and response examples are in [07-architecture.md](07-architecture.md#75-api-sketch-examples-for-the-contract).

## 8.5 Open questions for the frontend owner and for interviews

- Which export formats do real users need first?
- Is a per-object clip or a single summary video more useful?
- Should the user be able to correct a wrong class or merge two tracks?
- Accessibility: keyboard navigation and contrast review.
