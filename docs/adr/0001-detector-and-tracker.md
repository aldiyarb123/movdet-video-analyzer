# ADR-0001: Detector and tracker

- **Status:** Proposed (team to confirm)
- **Date:** 2026-10-23

## Context
We need class-aware detection and persistent identities, plus a classical baseline for evaluation. See [05-technology-comparison.md](../05-technology-comparison.md) D1, D2.

## Decision
YOLO family via Ultralytics as detector; ByteTrack as default tracker (BoT-SORT selectable); OpenCV MOG2 kept as baseline B0.

## Consequences
+ Fast integration, tracker support built in, strong detection under lighting change.
+ ByteTrack needs no appearance model.
− Ultralytics licence terms must be checked before the final release (risk R1); fallback RF-DETR.
− Tracking quality depends on detector quality; must be tuned and measured.
