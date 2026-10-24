"""Extractor (FR-07, FR-08): save crops and clips of moving tracks.

Output layout (read by the API, src/backend/app.py):
    <out_dir>/crops/track_<id>/<frame>.jpg     1..max_crops images per moving track
    <out_dir>/clips/track_<id>.mp4             clip from first-padding to last+padding frame

The video is read once; crops and clips for all tracks are written in the same pass.

Usage (from the repository root), on tracks from YOLO or baseline B0:
    python src/vision/extractor.py video.mp4 out/tracks.json --out out/artefacts
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, Sequence

import cv2


def pick_indices(n: int, k: int) -> list[int]:
    """Up to `k` indices spread evenly over 0..n-1, always including the first and last."""
    if n <= 0 or k <= 0:
        return []
    if k >= n:
        return list(range(n))
    if k == 1:
        return [n // 2]
    return sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})


def crop_box(frame, box: Sequence[int], margin: float = 0.1):
    """Cut the box out of the frame with a small margin, clamped to the image."""
    h_img, w_img = frame.shape[:2]
    x, y, w, h = box[:4]
    mx, my = round(w * margin), round(h * margin)
    x0, y0 = max(0, x - mx), max(0, y - my)
    x1, y1 = min(w_img, x + w + mx), min(h_img, y + h + my)
    if x1 <= x0 or y1 <= y0:
        return None
    return frame[y0:y1, x0:x1]


def extract(
    video_path: str | Path,
    tracks: list[dict[str, Any]],
    out_dir: str | Path,
    max_crops_per_track: int = 5,
    clip_padding_seconds: float = 1.0,
    save_crops: bool = True,
    save_clips: bool = True,
    only_moving: bool = True,
    progress: Callable[[float], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> list[dict[str, Any]]:
    """Write artefacts and return copies of the tracks with `crops`, `clip`, `clip_start_frame`, `clip_end_frame`."""
    out_dir = Path(out_dir)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    pad = max(0, round(clip_padding_seconds * fps))

    result = [dict(t) for t in tracks]
    crop_jobs: dict[int, list[tuple[dict, Sequence[int]]]] = {}
    clip_starts: dict[int, list[dict]] = {}
    last_needed = -1
    for t in result:
        t["crops"], t["clip"] = [], None
        if only_moving and not t.get("moving"):
            continue
        if save_crops and t["frames"]:
            for i in pick_indices(len(t["frames"]), max_crops_per_track):
                crop_jobs.setdefault(t["frames"][i], []).append((t, t["boxes"][i]))
                last_needed = max(last_needed, t["frames"][i])
        if save_clips and t["frames"]:
            start = max(0, t["first_frame"] - pad)
            end = t["last_frame"] + pad
            if total:
                end = min(end, total - 1)
            t["clip_start_frame"], t["clip_end_frame"] = start, end
            clip_starts.setdefault(start, []).append(t)
            last_needed = max(last_needed, end)

    writers: dict[int, tuple[cv2.VideoWriter, dict]] = {}
    frame_idx = 0
    try:
        while frame_idx <= last_needed:
            if should_stop is not None and should_stop():
                break
            ok, frame = cap.read()
            if not ok:
                break
            for t in clip_starts.get(frame_idx, []):
                path = out_dir / "clips" / f"track_{t['id']}.mp4"
                path.parent.mkdir(parents=True, exist_ok=True)
                h, w = frame.shape[:2]
                writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                if not writer.isOpened():
                    raise RuntimeError(f"Cannot write clip: {path}")
                writers[t["id"]] = (writer, t)
                t["clip"] = str(path.relative_to(out_dir))
            for tid, (writer, t) in list(writers.items()):
                writer.write(frame)
                if frame_idx >= t["clip_end_frame"]:
                    writer.release()
                    del writers[tid]
            for t, box in crop_jobs.get(frame_idx, []):
                crop = crop_box(frame, box)
                if crop is None:
                    continue
                path = out_dir / "crops" / f"track_{t['id']}" / f"{frame_idx:06d}.jpg"
                path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(path), crop)
                t["crops"].append(str(path.relative_to(out_dir)))
            frame_idx += 1
            if progress is not None and last_needed > 0 and frame_idx % 25 == 0:
                progress(min(frame_idx / (last_needed + 1), 1.0))
    finally:
        for writer, t in writers.values():  # video ended before the padded end
            writer.release()
            t["clip_end_frame"] = frame_idx - 1
        cap.release()
    if progress is not None:
        progress(1.0)
    return result


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Save crops and clips of moving tracks")
    ap.add_argument("video")
    ap.add_argument("tracks", help="tracks.json from detector_tracker.py, baseline_mog2.py or the pipeline")
    ap.add_argument("--out", default="out/artefacts")
    ap.add_argument("--max-crops", type=int, default=5)
    ap.add_argument("--padding", type=float, default=1.0, help="clip padding in seconds")
    ap.add_argument("--min-displacement", type=float, default=25.0)
    ap.add_argument("--window-frames", type=int, default=15)
    args = ap.parse_args(argv)

    from motion_filter import classify_tracks  # noqa: PLC0415 (script mode)

    data = json.loads(Path(args.tracks).read_text())
    tracks = classify_tracks(data["tracks"], args.min_displacement, args.window_frames)
    tracks = extract(args.video, tracks, args.out, args.max_crops, args.padding)
    moving = [t for t in tracks if t["moving"]]
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out) / "tracks.json").write_text(json.dumps({**data, "tracks": tracks}, indent=2))
    print(f"{len(moving)} moving of {len(tracks)} tracks; "
          f"{sum(len(t['crops']) for t in moving)} crops, {sum(1 for t in moving if t['clip'])} clips -> {args.out}")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
