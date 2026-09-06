import React from "react";

/**
 * ProgressBar component – displays processing state, progress percentage,
 * and status messages during transcription.
 *
 * Props:
 *   status: 'idle' | 'processing' | 'completed' | 'failed'
 *   progress: number (0-100)
 *   message: string – status message to display
 */
interface ProgressBarProps {
  status: "idle" | "processing" | "completed" | "failed";
  progress: number;
  message: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  status,
  progress,
  message,
}) => {
  if (status === "idle") return null;

  const statusColors = {
    processing: "bg-blue-500",
    completed: "bg-green-500",
    failed: "bg-red-500",
  };

  const statusBgColor = statusColors[status] || "bg-gray-500";

  return (
    <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">Processing</h3>
        <span className="text-xs font-medium text-gray-600">
          {status === "completed" ? "Complete" : `${Math.round(progress)}%`}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-300 h-2 rounded overflow-hidden">
        <div
          className={`h-full transition-all ${statusBgColor}`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>

      {/* Status message */}
      <p
        className={`text-sm ${
          status === "failed" ? "text-red-600" : "text-gray-700"
        }`}
      >
        {message}
      </p>

      {/* Spinner for processing state */}
      {status === "processing" && (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-gray-500">Processing your audio...</span>
        </div>
      )}
    </div>
  );
};
