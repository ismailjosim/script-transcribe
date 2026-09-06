import React from "react";

/**
 * DownloadButton component – provides download functionality for
 * completed transcripts with file naming and success confirmation.
 *
 * Props:
 *   jobId: string | null – completed job identifier
 *   outputFormat: string – file format (txt, srt, vtt, json)
 *   onDownload: () => void – callback when download is triggered
 */
interface DownloadButtonProps {
  jobId: string | null;
  outputFormat: string;
  disabled?: boolean;
  onDownload?: () => void;
}

export const DownloadButton: React.FC<DownloadButtonProps> = ({
  jobId,
  outputFormat,
  disabled = false,
  onDownload,
}) => {
  const [downloading, setDownloading] = React.useState(false);
  const [success, setSuccess] = React.useState(false);

  const handleDownload = async () => {
    if (!jobId || disabled) return;

    setDownloading(true);
    setSuccess(false);

    try {
      // Call the FastAPI backend download endpoint
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/download/${jobId}`,
      );

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      // Create a blob from the response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      // Create temporary download link
      const link = document.createElement("a");
      link.href = url;
      link.download = `transcript.${outputFormat}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up
      window.URL.revokeObjectURL(url);

      setSuccess(true);
      if (onDownload) onDownload();

      // Reset success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      console.error("Download error:", error);
      alert("Failed to download transcript. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  if (!jobId) return null;

  return (
    <div className="mt-4 flex flex-col gap-2">
      <button
        onClick={handleDownload}
        disabled={disabled || downloading}
        className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg
          hover:bg-indigo-700 transition disabled:bg-gray-400
          disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {downloading ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span>Downloading...</span>
          </>
        ) : (
          <>
            <span>⬇</span>
            <span>Download Transcript ({outputFormat.toUpperCase()})</span>
          </>
        )}
      </button>

      {success && (
        <p className="text-sm text-green-600 text-center">
          ✓ Download successful!
        </p>
      )}
    </div>
  );
};
