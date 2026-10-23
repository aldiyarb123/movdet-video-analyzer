
import { useState } from "react";
import {
  createJob,
  type AnalysisSettings,
  type JobResponse,
} from "./api/jobs";
import ResultsViewer from "./components/ResultsViewer";
import "./App.css";

const objectClasses = ["person", "car", "bicycle", "truck", "bus"];

function App() {
  const [video, setVideo] = useState<File | null>(null);
  const [classes, setClasses] = useState<string[]>(["person", "car"]);
  const [confidence, setConfidence] = useState(0.35);
  const [motionThreshold, setMotionThreshold] = useState(25);
  const [tracker, setTracker] = useState("bytetrack");
  const [loading, setLoading] = useState(false);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState("");

  // DIP-18: Navigation between upload and results viewer
  const [page, setPage] = useState<"upload" | "results">("upload");

  function handleFile(file?: File) {
    setError("");
    setJob(null);

    if (!file) return;

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!["mp4", "avi", "mov", "mkv"].includes(extension ?? "")) {
      setError("Unsupported video format. Use MP4, AVI, MOV or MKV.");
      setVideo(null);
      return;
    }

    if (file.size > 500 * 1024 * 1024) {
      setError("File must be smaller than 500 MB.");
      setVideo(null);
      return;
    }

    setVideo(file);
  }

  function toggleClass(className: string) {
    setClasses((current) =>
      current.includes(className)
        ? current.filter((item) => item !== className)
        : [...current, className]
    );
  }

  async function handleSubmit(
    event: React.SubmitEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!video || classes.length === 0 || loading) return;

    const settings: AnalysisSettings = {
      classes,
      confidence,
      tracker,
      motion: {
        min_displacement_px: motionThreshold,
        window_frames: 15,
      },
    };

    setLoading(true);
    setError("");
    setJob(null);

    try {
      const result = await createJob(video, settings);
      setJob(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  }

  // DIP-18: Results viewer screen
  if (page === "results") {
    return (
      <div className="app">
        <header className="header">
          <div className="logo">▣ MotionScope</div>
          <span className="headerTag">
            Results Viewer · DIP-18
          </span>
        </header>

        <main className="container">
          <ResultsViewer
            onBack={() => setPage("upload")}
          />
        </main>
      </div>
    );
  }

  // DIP-17: Existing upload screen
  return (
    <div className="app">
      <header className="header">
        <div className="logo">▣ MotionScope</div>
        <span className="headerTag">
          Frontend + API Client · DIP-17
        </span>
      </header>

      <main className="container">
        <h1>New Analysis</h1>

        <p className="subtitle">
          Upload a video, configure detection settings and
          create an analysis job.
        </p>

        <form onSubmit={handleSubmit} className="layout">
          <section className="card">
            <h2>1. Upload Video</h2>

            <label
              className="uploadArea"
              htmlFor="videoUpload"
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                handleFile(event.dataTransfer.files[0]);
              }}
            >
              <span className="uploadIcon">↑</span>

              <strong>
                {video
                  ? video.name
                  : "Choose a video or drag it here"}
              </strong>

              <span>
                MP4, AVI, MOV, MKV · Maximum 500 MB
              </span>

              {video && (
                <span className="fileSize">
                  {(video.size / (1024 * 1024)).toFixed(2)}
                  {" "}MB selected
                </span>
              )}
            </label>

            <input
              id="videoUpload"
              className="hiddenInput"
              type="file"
              accept=".mp4,.avi,.mov,.mkv"
              onChange={(event) =>
                handleFile(event.target.files?.[0])
              }
            />

            <div className="infoBox">
              <strong>How it works</strong>

              <p>
                This frontend sends the video and
                configuration to the FastAPI endpoint{" "}
                <code>POST /api/jobs</code>.
              </p>

              <p>
                Actual video processing requires
                the backend service.
              </p>
            </div>
          </section>

          <section className="card">
            <h2>2. Analysis Settings</h2>

            <label className="fieldLabel">
              Object Classes
            </label>

            <div className="chips">
              {objectClasses.map((className) => (
                <button
                  type="button"
                  key={className}
                  className={
                    classes.includes(className)
                      ? "chip active"
                      : "chip"
                  }
                  aria-pressed={classes.includes(className)}
                  onClick={() => toggleClass(className)}
                >
                  {className}
                </button>
              ))}
            </div>

            {classes.length === 0 && (
              <p className="hint errorText">
                Select at least one object class.
              </p>
            )}

            <label
              className="fieldLabel"
              htmlFor="confidence"
            >
              Confidence Threshold: {confidence.toFixed(2)}
            </label>

            <input
              id="confidence"
              type="range"
              min="0.1"
              max="0.9"
              step="0.05"
              value={confidence}
              onChange={(event) =>
                setConfidence(Number(event.target.value))
              }
            />

            <div className="rangeHints">
              <span>More detections</span>
              <span>Higher confidence</span>
            </div>

            <label
              className="fieldLabel"
              htmlFor="motion"
            >
              Moving Threshold: {motionThreshold} px
            </label>

            <input
              id="motion"
              type="range"
              min="5"
              max="100"
              step="5"
              value={motionThreshold}
              onChange={(event) =>
                setMotionThreshold(Number(event.target.value))
              }
            />

            <label
              className="fieldLabel"
              htmlFor="tracker"
            >
              Tracker
            </label>

            <select
              id="tracker"
              value={tracker}
              onChange={(event) =>
                setTracker(event.target.value)
              }
            >
              <option value="bytetrack">
                ByteTrack (recommended)
              </option>

              <option value="botsort">
                BoT-SORT
              </option>
            </select>

            <button
              type="submit"
              className="primaryButton"
              disabled={
                !video ||
                classes.length === 0 ||
                loading
              }
            >
              {loading
                ? "Sending to API..."
                : "Start Analysis"}
            </button>
          </section>
        </form>

        {error && (
          <div
            className="message errorMessage"
            role="alert"
          >
            <strong>Request failed</strong>
            <p>{error}</p>
          </div>
        )}

        {job && (
          <div
            className="message successMessage"
            role="status"
          >
            <strong>
              Analysis job created successfully
            </strong>

            <p>Job ID: {job.id}</p>
            <p>Status: {job.status}</p>

            <p>
              Progress:{" "}
              {typeof job.progress === "number"
                ? `${Math.round(job.progress * 100)}%`
                : "Not available"}
            </p>
          </div>
        )}

        {/* DIP-18: Navigation to Results Viewer */}
        <div className="viewerNavigation">
          <button
            type="button"
            className="primaryButton"
            onClick={() => setPage("results")}
          >
            Open Results Viewer →
          </button>
        </div>

        <p className="footerNote">
          MotionScope Diploma Project · Frontend
          Skeleton & Results Viewer
        </p>
      </main>
    </div>
  );
}

export default App;
