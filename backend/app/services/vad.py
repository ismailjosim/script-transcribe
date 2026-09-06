"""
Voice Activity Detection service using Silero VAD.
Helps identify speech regions and long silences.
"""

from typing import List, Dict, Any, Optional
import os


class VADService:
    """Detect voice activity in audio using Silero VAD."""

    def __init__(self):
        """Initialize the VAD service."""
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the Silero VAD model (lazy loaded on first use)."""
        try:
            import torch
            print("Loading Silero VAD model...")
            self.model = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False,
            )
            print("✓ Silero VAD model loaded")
        except ImportError:
            raise ImportError(
                "torch not installed. Install with: pip install torch"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Silero VAD model: {e}")

    def detect_speech_regions(
        self,
        audio_path: str,
        threshold: float = 0.5,
        min_speech_ms: int = 250,
        min_silence_ms: int = 2000,
    ) -> List[Dict[str, Any]]:
        """
        Detect speech regions in audio.

        Args:
            audio_path: Path to WAV audio file.
            threshold: Probability threshold for speech detection (0.0-1.0).
            min_speech_ms: Minimum speech duration in milliseconds.
            min_silence_ms: Minimum silence duration in milliseconds.

        Returns:
            List of speech regions with start/end times.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.model is None:
            self._load_model()

        try:
            import torch
            import torchaudio

            # Load audio
            waveform, sample_rate = torchaudio.load(audio_path)

            # Resample to 16kHz if necessary
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)
                sample_rate = 16000

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)

            # Detect speech
            speech_timestamps = self.model.get_speech_timestamps(
                waveform,
                self.model,
                sampling_rate=sample_rate,
                threshold=threshold,
                min_speech_duration_ms=min_speech_ms,
                min_silence_duration_ms=min_silence_ms,
                speech_pad_ms=400,
            )

            # Convert to seconds
            regions = [
                {
                    'start': ts['start'] / sample_rate,
                    'end': ts['end'] / sample_rate,
                }
                for ts in speech_timestamps
            ]

            return regions

        except Exception as e:
            raise RuntimeError(f"Speech detection failed: {e}")

    def get_silence_regions(
        self,
        audio_path: str,
        threshold: float = 0.5,
        min_silence_ms: int = 2000,
    ) -> List[Dict[str, Any]]:
        """
        Get silence regions (inverse of speech regions).

        Args:
            audio_path: Path to WAV audio file.
            threshold: Probability threshold for speech detection.
            min_silence_ms: Minimum silence duration in milliseconds.

        Returns:
            List of silence regions with start/end times.
        """
        speech_regions = self.detect_speech_regions(
            audio_path,
            threshold=threshold,
            min_silence_ms=min_silence_ms,
        )

        if not speech_regions:
            return []

        silence_regions = []
        for i in range(len(speech_regions) - 1):
            silence_start = speech_regions[i]['end']
            silence_end = speech_regions[i + 1]['start']
            if silence_end - silence_start >= (min_silence_ms / 1000):
                silence_regions.append({
                    'start': silence_start,
                    'end': silence_end,
                    'duration': silence_end - silence_start,
                })

        return silence_regions
