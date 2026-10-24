# ADR-0003: Definition of a "moving" object

- **Status:** Accepted when the DIP-6 pull request is merged (team approval)
- **Date:** 2026-10-23

## Context
A detector reports objects, not motion. The product must separate moving objects from parked or standing ones.

## Decision
A track is *moving* if the distance between its center at the start and end of a window (default 15 frames) is at least a threshold (default 25 px, configurable). Static camera is assumed.

## Consequences
+ Simple, explainable, testable (unit tests exist for the baseline version).
− Slow movement and camera shake can be misclassified; thresholds may need scaling by resolution. Alternatives to evaluate: speed relative to object size, optical-flow check inside the box.
- Threshold and window are starting values; they are tuned and measured on test videos in DIP-12 and DIP-15 and the ADR is updated with the result.
