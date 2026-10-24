# ADR-0001: Detector and tracker

- **Status:** Accepted when the DIP-6 pull request is merged (team approval)
- **Date:** 2026-10-23

## Context
We need class-aware detection and persistent identities, plus a classical baseline for evaluation. See [05-technology-comparison.md](../05-technology-comparison.md) D1, D2.

## Decision
YOLO family via Ultralytics as detector; ByteTrack as default tracker (BoT-SORT selectable); OpenCV MOG2 kept as baseline B0.

## Consequences
+ Fast integration, tracker support built in, strong detection under lighting change.
+ ByteTrack needs no appearance model.
− Ultralytics is licensed AGPL-3.0 (verified on package metadata, 24 Oct 2026): our code must be handled under AGPL terms or a commercial licence is needed. Decide consciously with the supervisor before the final release (risk R1); fallback RF-DETR.
− Tracking quality depends on detector quality; must be tuned and measured.
- `rfdetr` 1.11.2 metadata: Apache 2.0 (fallback). Model-weight terms not checked.
