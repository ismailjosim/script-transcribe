import React, { useState } from "react";

/**
 * ProcessingOptions component – allows user to configure transcription settings:
 * quality mode (Fast/Accuracy), pause threshold slider, and language selection.
 *
 * Props:
 *   onOptionsChange: (options: ProcessingOptions) => void – called when settings change
 */
export interface ProcessingOptions {
  mode: "fast" | "accuracy";
  pauseThreshold: number;
  language: string;
}

interface ProcessingOptionsProps {
  onOptionsChange: (options: ProcessingOptions) => void;
}

export const ProcessingOptions: React.FC<ProcessingOptionsProps> = ({
  onOptionsChange,
}) => {
  const [mode, setMode] = useState<"fast" | "accuracy">("accuracy");
  const [pauseThreshold, setPauseThreshold] = useState<number>(0.7);
  const [language, setLanguage] = useState<string>("auto");

  const handleModeChange = (newMode: "fast" | "accuracy") => {
    setMode(newMode);
    onOptionsChange({ mode: newMode, pauseThreshold, language });
  };

  const handleThresholdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setPauseThreshold(value);
    onOptionsChange({ mode, pauseThreshold: value, language });
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setLanguage(value);
    onOptionsChange({ mode, pauseThreshold, language: value });
  };

  return (
    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded flex flex-col gap-4">
      <h3 className="font-semibold text-gray-800">Processing Options</h3>

      {/* Quality mode selector */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-gray-700">Quality Mode</label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="fast"
              checked={mode === "fast"}
              onChange={() => handleModeChange("fast")}
              className="cursor-pointer"
            />
            <span className="text-sm text-gray-600">Fast (Quicker)</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="accuracy"
              checked={mode === "accuracy"}
              onChange={() => handleModeChange("accuracy")}
              className="cursor-pointer"
            />
            <span className="text-sm text-gray-600">Accuracy (More Precise)</span>
          </label>
        </div>
      </div>

      {/* Pause threshold slider */}
      <div className="flex flex-col gap-2">
        <label htmlFor="pause-threshold" className="text-sm font-medium text-gray-700">
          Pause Threshold: {pauseThreshold.toFixed(2)}s
        </label>
        <input
          id="pause-threshold"
          type="range"
          min="0.1"
          max="3"
          step="0.1"
          value={pauseThreshold}
          onChange={handleThresholdChange}
          className="cursor-pointer"
        />
        <p className="text-xs text-gray-500">
          Minimum pause duration (in seconds) to separate speech chunks.
        </p>
      </div>

      {/* Language selector */}
      <div className="flex flex-col gap-2">
        <label htmlFor="language" className="text-sm font-medium text-gray-700">
          Language Detection
        </label>
        <select
          id="language"
          value={language}
          onChange={handleLanguageChange}
          className="px-3 py-2 border border-gray-300 rounded bg-white text-sm text-gray-700 hover:border-gray-400 focus:outline-none focus:ring focus:ring-indigo-200"
        >
          <option value="auto">Auto-detect</option>
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="it">Italian</option>
          <option value="pt">Portuguese</option>
          <option value="zh">Chinese</option>
          <option value="ja">Japanese</option>
        </select>
      </div>
    </div>
  );
};
