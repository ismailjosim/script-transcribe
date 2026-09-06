import React, { useEffect, useRef, useState } from "react";

/**
 * AudioPreview component – renders an HTML5 audio player with controls,
 * displays duration and current playback time.
 *
 * Props:
 *   file: File | null – audio file to preview
 */
interface AudioPreviewProps {
  file: File | null;
}

export const AudioPreview: React.FC<AudioPreviewProps> = ({ file }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [duration, setDuration] = useState<number>(0);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  useEffect(() => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    if (audioRef.current) {
      audioRef.current.src = url;
    }
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handlePlayPause = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (time: number) => {
    if (!Number.isFinite(time)) return "0:00";
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (!file) return null;

  return (
    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded flex flex-col gap-3">
      <h3 className="font-semibold text-gray-800">Audio Preview</h3>
      <div className="flex items-center gap-2">
        <button
          onClick={handlePlayPause}
          className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
        >
          {isPlaying ? "⏸ Pause" : "▶ Play"}
        </button>
        <span className="text-sm text-gray-600">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>
      <audio
        ref={audioRef}
        onLoadedMetadata={handleLoadedMetadata}
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        className="w-full"
      />
      <div className="w-full bg-gray-300 h-1 rounded overflow-hidden">
        <div
          className="bg-indigo-600 h-full transition-all"
          style={{
            width: duration > 0 ? `${(currentTime / duration) * 100}%` : "0%",
          }}
        />
      </div>
    </div>
  );
};
