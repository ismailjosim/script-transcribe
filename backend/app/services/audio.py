"""
Audio processing service.
Handles file validation, format detection, and FFmpeg conversion.
"""

import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional


class AudioProcessorError(Exception):
    """Base exception for audio processing errors."""
    pass


class AudioProcessor:
    """Process audio files: validate, detect format, convert to WAV."""

    SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.mp4', '.webm'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    MAX_DURATION = 60 * 60  # 60 minutes in seconds

    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize the audio processor.

        Args:
            temp_dir: Directory for temporary files. Defaults to system temp.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self._ensure_ffmpeg_available()

    def _ensure_ffmpeg_available(self) -> None:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise AudioProcessorError(
                "FFmpeg is not installed or not in PATH. "
                "Install FFmpeg from https://ffmpeg.org/download.html"
            )

    def validate(self, file_path: str) -> None:
        """
        Validate audio file.

        Args:
            file_path: Path to the audio file.

        Raises:
            AudioProcessorError: If validation fails.
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise AudioProcessorError(f"File not found: {file_path}")

        # Check file extension
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise AudioProcessorError(
                f"Unsupported format: {path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            raise AudioProcessorError("File is empty")
        if file_size > self.MAX_FILE_SIZE:
            raise AudioProcessorError(
                f"File too large: {file_size / 1024 / 1024:.1f} MB "
                f"(max: {self.MAX_FILE_SIZE / 1024 / 1024:.0f} MB)"
            )

        # Check if file is actually audio using FFmpeg
        try:
            result = subprocess.run(
                ['ffmpeg', '-i', str(path)],
                capture_output=True,
                timeout=10,
                text=True
            )
            # FFmpeg always exits with non-zero, check stderr for audio stream
            if 'Audio:' not in result.stderr:
                raise AudioProcessorError("File does not contain audio")

            # Extract duration
            duration = self._extract_duration(result.stderr)
            if duration and duration > self.MAX_DURATION:
                raise AudioProcessorError(
                    f"Audio too long: {duration / 60:.1f} minutes "
                    f"(max: {self.MAX_DURATION / 60:.0f} minutes)"
                )

        except subprocess.TimeoutExpired:
            raise AudioProcessorError("Timeout checking audio file")

    def _extract_duration(self, ffmpeg_output: str) -> Optional[float]:
        """Extract duration from FFmpeg output."""
        import re
        match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', ffmpeg_output)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return None

    def process(self, file_path: str) -> str:
        """
        Process audio file: validate and convert to WAV format.

        Args:
            file_path: Path to the audio file.

        Returns:
            Path to the processed WAV file in temp directory.

        Raises:
            AudioProcessorError: If processing fails.
        """
        self.validate(file_path)

        # Generate safe temporary filename
        safe_filename = f"audio_{uuid.uuid4().hex}.wav"
        output_path = os.path.join(self.temp_dir, safe_filename)

        try:
            # Convert to WAV using FFmpeg
            # -i: input file
            # -vn: no video
            # -acodec pcm_s16le: PCM 16-bit LE encoding
            # -ar 16000: 16kHz sample rate (required for Whisper)
            # -ac 1: mono
            # -y: overwrite output
            subprocess.run(
                [
                    'ffmpeg',
                    '-i', str(file_path),
                    '-vn',
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    output_path
                ],
                capture_output=True,
                check=True,
                timeout=300  # 5 minute timeout
            )

            if not os.path.exists(output_path):
                raise AudioProcessorError("Failed to create output WAV file")

            return output_path

        except subprocess.CalledProcessError as e:
            self._cleanup_file(output_path)
            raise AudioProcessorError(f"FFmpeg conversion failed: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            self._cleanup_file(output_path)
            raise AudioProcessorError("Audio processing timeout")

    @staticmethod
    def _cleanup_file(file_path: str) -> None:
        """Safely delete a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # Ignore cleanup errors
