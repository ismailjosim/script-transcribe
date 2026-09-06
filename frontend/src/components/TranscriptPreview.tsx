import React from "react";

/**
 * TranscriptPreview component – displays the formatted transcript
 * with word count, duration info, and styled presentation.
 *
 * Props:
 *   transcript: string | null – transcript text to display
 *   wordCount: number – total word count
 *   duration: number – audio duration in seconds
 */
interface TranscriptPreviewProps {
  transcript: string | null;
  wordCount: number;
  duration: number;
}

export const TranscriptPreview: React.FC<TranscriptPreviewProps> = ({
  transcript,
  wordCount,
  duration,
}) => {
  if (!transcript) return null;

  const formatDuration = (seconds: number) => {
    if (!Number.isFinite(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="mt-6 p-4 bg-white border border-gray-200 rounded flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">Transcript</h3>
        <div className="flex gap-4 text-xs text-gray-600">
          <span>Words: {wordCount.toLocaleString()}</span>
          <span>Duration: {formatDuration(duration)}</span>
        </div>
      </div>

      {/* Transcript display area with scrollable content */}
      <div className="max-h-96 overflow-y-auto p-3 bg-gray-50 border border-gray-200 rounded">
        <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans leading-relaxed">
          {transcript}
        </pre>
      </div>

      {/* Statistics summary */}
      <div className="flex gap-6 text-xs text-gray-500 pt-2 border-t border-gray-200">
        <span>Characters: {transcript.length.toLocaleString()}</span>
        <span>
          Words per minute:{" "}
          {duration > 0 ? Math.round((wordCount / duration) * 60) : 0}
        </span>
      </div>
    </div>
  );
};
