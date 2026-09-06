"""
Transcription service using faster-whisper.
Handles speech-to-text conversion with word-level timestamps.
"""

from typing import Dict, List, Any, Optional
import os


class TranscriptionService:
    """Transcribe audio to text using faster-whisper with word-level timestamps."""

    # Model size: small, medium, large-v3
    # Development: small or medium
    # Production: large-v3 or distilled models
    DEFAULT_MODEL = "small"

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the transcription service.

        Args:
            model: Whisper model size. Defaults to 'small'.
                  Options: tiny, base, small, medium, large, large-v3
        """
        self.model_name = model or self.DEFAULT_MODEL
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model (lazy loaded on first use)."""
        try:
            from faster_whisper import WhisperModel
            print(f"Loading Whisper model: {self.model_name}...")
            self.model = WhisperModel(
                self.model_name,
                device="auto",  # auto-detects GPU/CPU
                compute_type="default"
            )
            print(f"✓ Model loaded: {self.model_name}")
        except ImportError:
            raise ImportError(
                "faster-whisper not installed. "
                "Install with: pip install faster-whisper"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text with word-level timestamps.

        Args:
            audio_path: Path to WAV audio file.

        Returns:
            Dictionary containing:
                - words: List of words with start/end timestamps
                - language: Detected language code (e.g., 'en')
                - language_probability: Language detection confidence
                - full_text: Complete transcription
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.model is None:
            self._load_model()

        try:
            print("Transcribing audio...")
            # Transcribe with word-level timestamps
            segments, info = self.model.transcribe(
                audio_path,
                word_level=True,
                language=None,  # Auto-detect language
                vad_filter=True,  # Use VAD to remove silence
                vad_parameters={
                    'threshold': 0.5,
                    'min_speech_duration_ms': 250,
                    'min_silence_duration_ms': 2000,
                    'speech_pad_ms': 400,
                }
            )

            print(f"✓ Transcription complete")
            print(f"  Language: {info.language}")
            print(f"  Language probability: {info.language_probability:.2%}")

            # Extract words with timestamps
            words = self._extract_words(segments)

            return {
                'words': words,
                'language': info.language,
                'language_probability': info.language_probability,
                'full_text': ' '.join(w['text'] for w in words),
            }

        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")

    @staticmethod
    def _extract_words(segments) -> List[Dict[str, Any]]:
        """
        Extract word-level information from Whisper segments.

        Args:
            segments: Generator of segments from Whisper.

        Returns:
            List of words with start/end timestamps.
        """
        words = []
        for segment in segments:
            if hasattr(segment, 'words'):
                for word_info in segment.words:
                    words.append({
                        'text': word_info.word.strip(),
                        'start': word_info.start,
                        'end': word_info.end,
                    })
            else:
                # Fallback: if word-level data not available, estimate from segment
                # This shouldn't happen with word_level=True, but just in case
                words.append({
                    'text': segment.text.strip(),
                    'start': segment.start,
                    'end': segment.end,
                })

        return words
