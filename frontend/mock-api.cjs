
const express = require("express");

const app = express();
const PORT = 8000;

// Mock API for DIP-17.
// Receives the upload stream without storing video data.

app.post("/api/jobs", (req, res) => {
  const contentType = req.headers["content-type"] || "";

  if (!contentType.includes("multipart/form-data")) {
    return res.status(400).json({
      detail: "Expected multipart/form-data",
    });
  }

  let receivedBytes = 0;

  req.on("data", (chunk) => {
    receivedBytes += chunk.length;
  });

  req.on("end", () => {
    console.log("Upload received:", receivedBytes, "bytes");

    res.status(201).json({
      id: "test-job-001",
      status: "queued",
      progress: 0,
      error: null,
    });
  });

  req.on("error", (error) => {
    console.error("Upload stream error:", error.message);
  });
});

app.listen(PORT, "127.0.0.1", () => {
  console.log(`Mock API running at http://127.0.0.1:${PORT}`);
});
