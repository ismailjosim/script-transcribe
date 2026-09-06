import React, { ChangeEvent, useState } from "react";

/**
 * UploadArea component – handles audio file selection, validation and size display.
 *
 * Props:
 *   onFileSelect: (file: File) => void – callback when a valid file is selected.
 */
interface UploadAreaProps {
  onFileSelect: (file: File) => void;
}

// Accepted audio MIME types and extensions.
const ACCEPTED_TYPES = [
  "audio/mpeg", // .mp3
  "audio/wav",
  "audio/mp4",
  "audio/webm",
  "audio/x-m4a",
];

export const UploadArea: React.FC<UploadAreaProps> = ({ onFileSelect }) => {
  const [error, setError] = useState<string>("");
  const [fileInfo, setFileInfo] = useState<{ name: string; size: number } | null>(
    null,
  );

  const formatSize = (size: number) => {
    // format bytes to human readable string
    if (size < 1024) return `${size} B`;
    const kb = size / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KiB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MiB`;
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setError("");
    const file = e.target.files?.[0];
    if (!file) return;
    // Validate MIME type (fallback to extension check if MIME missing)
    if (!ACCEPTED_TYPES.includes(file.type)) {
      const ext = file.name.split(".").pop()?.toLowerCase();
      const allowedExts = ["mp3", "wav", "m4a", "mp4", "webm"];
      if (!allowedExts.includes(ext ?? "")) {
        setError("Unsupported audio format. Accepted: mp3, wav, m4a, mp4, webm.");
        return;
      }
    }
    // Optional: limit file size (e.g., 100 MiB)
    const maxSize = 100 * 1024 * 1024; // 100 MiB
    if (file.size > maxSize) {
      setError("File is too large. Maximum allowed size is 100 MiB.");
      return;
    }
    setFileInfo({ name: file.name, size: file.size });
    onFileSelect(file);
  };

  return (
    <div className="border border-gray-300 rounded p-4 bg-white flex flex-col gap-2">
      <label className="block font-medium text-gray-700" htmlFor="audio-upload">
        Choose an audio file to transcribe
      </label>
      <input
        id="audio-upload"
        type="file"
        accept={ACCEPTED_TYPES.map((t) => t.replace("audio/", ".")).join(",")}
        onChange={handleChange}
        className="mt-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
          file:rounded file:border-0 file:text-sm file:font-semibold
          file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
      />
      {fileInfo && (
        <p className="text-sm text-gray-600">
          Selected: {fileInfo.name} ({formatSize(fileInfo.size)})
        </p>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
};
