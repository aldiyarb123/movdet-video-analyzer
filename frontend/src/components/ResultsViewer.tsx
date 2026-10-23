
import { useCallback, useEffect, useRef, useState } from "react";
import "./ResultsViewer.css";

type BoundingBox = {
  frame: number;
  x: number;
  y: number;
  w: number;
  h: number;
};

type ObjectTrack = {
  id: number;
  className: string;
  moving: boolean;
  boxes: BoundingBox[];
};

interface ResultsViewerProps {
  onBack: () => void;
}

const DEMO_FPS = 24;

// Demonstration tracks. These are not real detections.
function createDemoTracks(totalFrames: number): ObjectTrack[] {
  const tracks: ObjectTrack[] = [];

  for (let objectId = 1; objectId <= 3; objectId++) {
    const boxes: BoundingBox[] = [];

    for (let frame = 0; frame < totalFrames; frame++) {
      const progress = frame / Math.max(1, totalFrames - 1);

      boxes.push({
        frame,
        x: objectId === 1
          ? 0.08 + progress * 0.55
          : objectId === 2
            ? 0.72 - progress * 0.35
            : 0.4,
        y: objectId === 1 ? 0.50 : objectId === 2 ? 0.62 : 0.18,
        w: objectId === 2 ? 0.16 : 0.09,
        h: objectId === 2 ? 0.13 : 0.25,
      });
    }

    tracks.push({
      id: objectId,
      className: objectId === 2 ? "car" : "person",
      moving: objectId !== 3,
      boxes,
    });
  }

  return tracks;
}

export default function ResultsViewer({ onBack }: ResultsViewerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [showOverlay, setShowOverlay] = useState(true);
  const [tracks, setTracks] = useState<ObjectTrack[]>([]);

  const currentFrame = Math.floor(currentTime * DEMO_FPS);

  const drawOverlay = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    const context = canvas.getContext("2d");
    if (!context) return;

    const width = video.videoWidth;
    const height = video.videoHeight;

    if (!width || !height) return;

    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }

    context.clearRect(0, 0, width, height);

    if (!showOverlay) return;

    const frame = Math.floor(video.currentTime * DEMO_FPS);

    tracks.forEach((track) => {
      const box = track.boxes[frame];
      if (!box) return;

      const x = box.x * width;
      const y = box.y * height;
      const w = box.w * width;
      const h = box.h * height;

      const color = track.moving ? "#22c55e" : "#f59e0b";

      context.strokeStyle = color;
      context.lineWidth = Math.max(2, width / 480);
      context.strokeRect(x, y, w, h);

      const label = `#${track.id} ${track.className}`;

      context.font = `${Math.max(14, width / 65)}px sans-serif`;
      const labelWidth = context.measureText(label).width + 12;
      const labelHeight = Math.max(22, width / 45);
      const labelY = Math.max(0, y - labelHeight);

      context.fillStyle = color;
      context.fillRect(x, labelY, labelWidth, labelHeight);

      context.fillStyle = "#ffffff";
      context.fillText(label, x + 6, labelY + labelHeight * 0.73);
    });
  }, [showOverlay, tracks]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let frameCallbackId: number | null = null;
    let animationFrameId: number | null = null;
    let stopped = false;

    const update = () => {
      if (stopped) return;

      drawOverlay();
      setCurrentTime(video.currentTime);

      if ("requestVideoFrameCallback" in video) {
        frameCallbackId = video.requestVideoFrameCallback(() => {
          update();
        });
      } else {
        animationFrameId = requestAnimationFrame(update);
      }
    };

    update();

    return () => {
      stopped = true;
      if (frameCallbackId !== null) {
        video.cancelVideoFrameCallback(frameCallbackId);
      }
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [drawOverlay, videoUrl]);

  useEffect(() => {
    return () => {
      if (videoUrl) URL.revokeObjectURL(videoUrl);
    };
  }, [videoUrl]);

  function handleVideo(file?: File) {
    if (!file) return;

    const extension = file.name.split(".").pop()?.toLowerCase();
    if (!["mp4", "webm", "mov", "avi", "mkv"].includes(extension ?? "")) {
      alert("Please select a supported video file.");
      return;
    }

    const url = URL.createObjectURL(file);
    setVideoUrl(url);
    setFileName(file.name);
    setCurrentTime(0);
    setDuration(0);
    setTracks([]);
  }

  function handleMetadata() {
    const video = videoRef.current;
    if (!video) return;

    const length = Number.isFinite(video.duration) ? video.duration : 0;

    setDuration(length);
    setCurrentTime(0);

    if (length > 0) {
      const totalFrames = Math.ceil(length * DEMO_FPS);
      setTracks(createDemoTracks(totalFrames));
    }
  }

  function handleSeek(value: number) {
    const video = videoRef.current;
    if (!video || !duration) return;

    video.currentTime = value;
    setCurrentTime(value);
    drawOverlay();
  }

  return (
    <div className="resultsPage">
      <div className="resultsHeading">
        <div>
          <h1>Results Viewer</h1>
          <p>Video playback with simulated object detection overlays.</p>
        </div>
        <button className="backButton" onClick={onBack}>
          ← Back to Upload
        </button>
      </div>

      <div className="resultsLayout">
        <section className="resultsCard">
          <h2>Video Preview</h2>

          <label className="videoPicker">
            Select a video
            <input
              type="file"
              accept="video/*,.mp4,.mov,.avi,.mkv,.webm"
              onChange={(event) => handleVideo(event.target.files?.[0])}
            />
          </label>

          {videoUrl ? (
            <>
              <div className="videoWrapper">
                <video
                  ref={videoRef}
                  src={videoUrl}
                  controls
                  playsInline
                  onLoadedMetadata={handleMetadata}
                  onSeeked={drawOverlay}
                  onTimeUpdate={() => {
                    setCurrentTime(videoRef.current?.currentTime ?? 0);
                  }}
                />
                <canvas ref={canvasRef} className="overlayCanvas" />
              </div>

              <div className="videoInformation">
                <span>{fileName}</span>
                <span>Frame: {currentFrame}</span>
              </div>

              <input
                className="videoSeek"
                type="range"
                min={0}
                max={duration || 1}
                step={1 / DEMO_FPS}
                value={Math.min(currentTime, duration || 1)}
                onChange={(event) => handleSeek(Number(event.target.value))}
                aria-label="Video timeline"
              />

              <label className="overlayToggle">
                <input
                  type="checkbox"
                  checked={showOverlay}
                  onChange={(event) => setShowOverlay(event.target.checked)}
                />
                Show Object Overlay
              </label>
            </>
          ) : (
            <div className="videoPlaceholder">
              Select a local video to preview object overlays.
            </div>
          )}
        </section>

        <section className="resultsCard">
          <h2>Detected Objects</h2>
          <p className="demoNotice">
            Demonstration data only — not produced by AI inference.
          </p>

          {tracks.map((track) => (
            <div className="trackItem" key={track.id}>
              <div>
                <strong>Object #{track.id}</strong>
                <p>{track.className}</p>
              </div>
              <span className={track.moving ? "movingTag" : "staticTag"}>
                {track.moving ? "Moving" : "Stationary"}
              </span>
            </div>
          ))}

          {tracks.length === 0 && (
            <p className="emptyText">No video loaded.</p>
          )}
        </section>
      </div>

      <p className="viewerDisclaimer">
        DIP-18 prototype: frame positions assume 24 FPS.
        Exact frame synchronization with real detection data and
        the required 10-minute test remain to be verified.
      </p>
    </div>
  );
}
