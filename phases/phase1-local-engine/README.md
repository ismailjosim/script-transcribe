# Audio Transcription Project - Phase 1: Local Engine

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install FFmpeg
- **Windows**: Download from https://ffmpeg.org/download.html or use `choco install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `apt-get install ffmpeg`

### 3. Run Local Transcription
```bash
python transcribe.py example.mp3
```

This will produce `transcript.txt` with pause-aware timestamps.

## Project Structure

```
backend/
├── transcribe.py              # CLI entry point
├── requirements.txt           # Python dependencies
│
├── app/
│   ├── services/
│   │   ├── audio.py          # Audio processing & validation
│   │   ├── transcription.py   # Whisper transcription
│   │   ├── vad.py            # Voice Activity Detection
│   │   ├── chunking.py        # Pause-aware chunking
│   │   └── formatter.py       # Output formatting
│   │
│   ├── utils/
│   │   └── timestamps.py      # Timestamp utilities
│   │
│   └── models/
│       └── schemas.py         # Pydantic schemas (future)
│
└── tests/
    ├── test_timestamps.py
    ├── test_chunking.py
    └── test_formatter.py
```

## Phase 1 Completion Checklist

- [x] Audio processing service (validation, format detection, FFmpeg conversion)
- [x] Transcription service (faster-whisper with word-level timestamps)
- [x] VAD service (Silero VAD for silence detection)
- [x] Chunking service (pause-aware grouping)
- [x] Formatter service (timestamp formatting and output)
- [x] Timestamp utilities
- [x] Unit tests for core logic
- [x] CLI entry point

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Architecture

### Audio Processing Pipeline

```
Upload Audio File
    ↓
Validate File (format, size, duration)
    ↓
Extract with FFmpeg (convert to 16kHz mono WAV)
    ↓
Transcribe with Whisper (get word-level timestamps)
    ↓
Chunk by Pauses/Punctuation/Length
    ↓
Format Output ([M:SS] timestamps)
    ↓
Generate transcript.txt
```

### Key Features

1. **Pause Detection**: Configurable threshold (default 0.7s)
2. **Punctuation Boundaries**: Natural breaks at `.`, `?`, `!`
3. **Max Chunk Length**: Prevents very long lines (default 15 words)
4. **Word-Level Timestamps**: Foundation for accurate pause detection
5. **Multiple Format Support**: MP3, WAV, M4A, MP4, WebM

## Next Phases

- **Phase 2**: Expose word-level timestamps in output
- **Phase 3**: Make pause threshold configurable
- **Phase 4**: Add punctuation and length-based chunking refinements
- **Phase 5**: Generate final transcript format
- **Phase 6**: Wrap with FastAPI endpoints
- **Phase 7**: Build Next.js frontend
- **Phase 8**: Error handling and edge cases
- **Phase 9**: Performance optimization

## Configuration

Current defaults in services:

```python
# Pause threshold
pause_threshold = 0.7  # seconds

# Max chunk length
max_chunk_words = 15

# Whisper model
model = "small"  # or "medium", "large-v3"

# Audio limits
max_file_size = 100 * 1024 * 1024  # 100 MB
max_duration = 60 * 60  # 60 minutes
```

These will become CLI arguments and API parameters in future phases.
