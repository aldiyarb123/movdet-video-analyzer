"""Benchmark baseline B0 (MOG2 + centroid tracker) on one video.

Measures processing speed for NFR-01 and records the machine, so the number can be
reproduced (NFR-09). Writes `benchmark.json` and `benchmark.md` to the output folder.

Usage (from the repository root):
    python src/vision/benchmark_baseline.py video.avi --out docs/evidence/dip-12
    python src/vision/benchmark_baseline.py video.avi --resize-height 720 --repeat 3
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from baseline_mog2 import run  # noqa: E402


def machine_info() -> dict:
    return {
        "os": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "cpu_count": os.cpu_count(),
        "python": platform.python_version(),
        "opencv": cv2.__version__,
    }


def benchmark(video: Path, repeat: int = 3, resize_height: int | None = None) -> dict:
    timings = []
    result = None
    for _ in range(repeat):
        start = time.perf_counter()
        result = run(video, resize_height=resize_height)
        timings.append(time.perf_counter() - start)
    assert result is not None
    best = min(timings)
    tracks = result["tracks"]
    return {
        "video": video.name,
        "frames": result["frames"],
        "resolution": f"{result['width']}x{result['height']}",
        "video_fps": result["fps"],
        "repeat": repeat,
        "seconds": [round(t, 3) for t in timings],
        "median_seconds": round(statistics.median(timings), 3),
        "processing_fps": round(result["frames"] / best, 1),
        "tracks_total": len(tracks),
        "tracks_moving": sum(1 for t in tracks if t["moving"]),
        "params": result["params"],
        "machine": machine_info(),
        "date": time.strftime("%Y-%m-%d %H:%M %z"),
    }


def to_markdown(b: dict) -> str:
    m = b["machine"]
    return f"""# Baseline B0 benchmark

| Item | Value |
|---|---|
| Date | {b['date']} |
| Video | `{b['video']}`, {b['resolution']}, {b['frames']} frames, {b['video_fps']:.1f} fps |
| Machine | {m['os']}, {m['machine']}, {m['cpu_count']} CPU threads, Python {m['python']}, OpenCV {m['opencv']} |
| Runs | {b['repeat']} (seconds: {', '.join(map(str, b['seconds']))}) |
| **Processing speed (best run)** | **{b['processing_fps']} frames/s** on CPU |
| Tracks / moving tracks | {b['tracks_total']} / {b['tracks_moving']} |

Parameters: `{json.dumps(b['params'])}`

Reproduce: `python src/vision/benchmark_baseline.py <video> --repeat {b['repeat']}`
"""


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, default=Path("out/benchmark"))
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--resize-height", type=int, default=None)
    args = ap.parse_args(argv)

    b = benchmark(args.video, args.repeat, args.resize_height)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "benchmark.json").write_text(json.dumps(b, indent=2) + "\n")
    (args.out / "benchmark.md").write_text(to_markdown(b))
    print(f"{b['processing_fps']} frames/s, {b['tracks_moving']} moving tracks -> {args.out}")


if __name__ == "__main__":
    main()
