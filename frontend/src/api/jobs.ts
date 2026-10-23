
export interface AnalysisSettings {
  classes: string[];
  confidence: number;
  tracker: string;
  motion: {
    min_displacement_px: number;
    window_frames: number;
  };
}

export interface JobResponse {
  id: string;
  status: string;
  progress?: number;
  error?: string | null;
}

const API_BASE_URL = "/api";

export async function createJob(
  video: File,
  settings: AnalysisSettings
): Promise<JobResponse> {
  const formData = new FormData();

  formData.append("video", video);
  formData.append("settings", JSON.stringify(settings));

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/jobs`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      "Cannot connect to the API server. Check that FastAPI is running."
    );
  }

  if (!response.ok) {
    let message = `Upload failed (HTTP ${response.status}).`;

    try {
      const data = await response.json();
      if (typeof data.detail === "string") {
        message = data.detail;
      }
    } catch {
      // Keep the HTTP error message if the response is not JSON.
    }

    throw new Error(message);
  }

  const data: unknown = await response.json();

  if (
    typeof data !== "object" ||
    data === null ||
    !("id" in data) ||
    typeof data.id !== "string" ||
    !("status" in data) ||
    typeof data.status !== "string"
  ) {
    throw new Error("API returned an invalid job response.");
  }

  return data as JobResponse;
}
