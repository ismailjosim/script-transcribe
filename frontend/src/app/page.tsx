"use client";

import React, { useState } from "react";
import { UploadArea } from "../components/UploadArea";
import { AudioPreview } from "../components/AudioPreview";
import { ProcessingOptions, ProcessingOptions as POpts } from "../components/ProcessingOptions";
import { ProgressBar } from "../components/ProgressBar";
import { TranscriptPreview } from "../components/TranscriptPreview";
import { DownloadButton } from "../components/DownloadButton";

// API base URL from environment or default
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Processing status type
type ProcessingStatus = "idle" | "processing" | "completed" | "failed";

export default function Home() {
  // State management
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processingOptions, setProcessingOptions] = useState<POpts>({
    mode: "accuracy",
    pauseThreshold: 0.7,
    language: "auto",
  });
  const [status, setStatus] = useState<ProcessingStatus>("idle");
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [wordCount, setWordCount] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [outputFormat, setOutputFormat] = useState<string>("txt");

  // Handle file selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    // Reset previous results
    setTranscript(null);
    setJobId(null);
    setStatus("idle");
    setProgress(0);
    setStatusMessage("");
  };

  // Handle processing options change
  const handleOptionsChange = (options: POpts) => {
    setProcessingOptions(options);
  };

  // Start transcription
  const startTranscription = async () => {
    if (!selectedFile) return;

    setStatus("processing");
    setProgress(0);
    setStatusMessage("Preparing upload...");

    try {
      // Create form data
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("mode", processingOptions.mode);
      formData.append("pause_threshold", processingOptions.pauseThreshold.toString());
      formData.append("output_format", outputFormat);

      setProgress(10);
      setStatusMessage("Uploading audio file...");

      // Call the FastAPI backend
      const response = await fetch(`${API_URL}/api/transcribe`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Transcription failed");
      }

      setProgress(50);
      setStatusMessage("Transcribing audio...");

      const result = await response.json();
      setJobId(result.job_id);

      // Poll for status if processing
      if (result.status === "processing") {
        await pollStatus(result.job_id);
      } else if (result.status === "completed") {
        setProgress(100);
        setStatus("completed");
        setStatusMessage("Transcription complete!");
        await fetchTranscript(result.job_id);
      } else {
        throw new Error(result.error || "Transcription failed");
      }
    } catch (error) {
      console.error("Transcription error:", error);
      setStatus("failed");
      setStatusMessage(error instanceof Error ? error.message : "An error occurred");
    }
  };

  // Poll job status
  const pollStatus = async (id: string) => {
    const maxAttempts = 60; // 5 minutes max (5s intervals)
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await fetch(`${API_URL}/api/status/${id}`);
        const data = await response.json();

        if (data.status === "completed") {
          setProgress(100);
          setStatus("completed");
          setStatusMessage("Transcription complete!");
          await fetchTranscript(id);
          return;
        } else if (data.status === "failed") {
          throw new Error(data.error || "Processing failed");
        }

        // Update progress
        if (data.progress) {
          setProgress(data.progress);
        }

        setStatusMessage(getStatusMessage(data.progress));
        attempts++;

        // Wait 5 seconds before next poll
        await new Promise((resolve) => setTimeout(resolve, 5000));
      } catch (error) {
        throw error;
      }
    }

    throw new Error("Transcription timed out");
  };

  // Get status message based on progress
  const getStatusMessage = (prog: number | null) => {
    if (!prog) return "Processing...";
    if (prog < 25) return "Processing audio...";
    if (prog < 50) return "Transcribing...";
    if (prog < 75) return "Analyzing speech patterns...";
    if (prog < 100) return "Formatting transcript...";
    return "Finalizing...";
  };

  // Fetch completed transcript
  const fetchTranscript = async (id: string) => {
    try {
      const response = await fetch(`${API_URL}/api/download/${id}`);
      if (!response.ok) throw new Error("Failed to fetch transcript");

      const text = await response.text();
      setTranscript(text);
      setWordCount(text.split(/\s+/).filter(Boolean).length);
      // Duration would ideally come from API; using placeholder
      setDuration(0);
    } catch (error) {
      console.error("Error fetching transcript:", error);
    }
  };

  // Reset the application
  const handleReset = () => {
    setSelectedFile(null);
    setTranscript(null);
    setJobId(null);
    setStatus("idle");
    setProgress(0);
    setStatusMessage("");
    setWordCount(0);
    setDuration(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Audio Transcription
          </h1>
          <p className="text-gray-600">
            Upload an audio file and get a formatted transcript with word-level timestamps
          </p>
        </div>

        {/* Main content card */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Upload area */}
          <UploadArea onFileSelect={handleFileSelect} />

          {/* Audio preview */}
          <AudioPreview file={selectedFile} />

          {/* Processing options */}
          {selectedFile && status === "idle" && (
            <>
              <ProcessingOptions onOptionsChange={handleOptionsChange} />

              {/* Output format selector */}
              <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded flex flex-col gap-2">
                <label htmlFor="output-format" className="text-sm font-medium text-gray-700">
                  Output Format
                </label>
                <select
                  id="output-format"
                  value={outputFormat}
                  onChange={(e) => setOutputFormat(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded bg-white text-sm text-gray-700 hover:border-gray-400 focus:outline-none focus:ring focus:ring-indigo-200"
                >
                  <option value="txt">Plain Text (.txt)</option>
                  <option value="srt">SubRip Subtitle (.srt)</option>
                  <option value="vtt">WebVTT Subtitle (.vtt)</option>
                  <option value="json">JSON with Timestamps (.json)</option>
                </select>
              </div>

              {/* Start button */}
              <div className="mt-6 flex gap-4">
                <button
                  onClick={startTranscription}
                  className="flex-1 px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition"
                >
                  Start Transcription
                </button>
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition"
                >
                  Reset
                </button>
              </div>
            </>
          )}

          {/* Progress bar */}
          <ProgressBar status={status} progress={progress} message={statusMessage} />

          {/* Transcript preview */}
          {status === "completed" && (
            <>
              <TranscriptPreview
                transcript={transcript}
                wordCount={wordCount}
                duration={duration}
              />

              {/* Download and reset buttons */}
              <div className="mt-6 flex gap-4">
                <DownloadButton
                  jobId={jobId}
                  outputFormat={outputFormat}
                  disabled={status !== "completed"}
                />
                <button
                  onClick={handleReset}
                  className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition"
                >
                  Transcribe Another File
                </button>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Powered by Whisper • FastAPI • Next.js</p>
        </div>
      </div>
    </div>
  );
}
