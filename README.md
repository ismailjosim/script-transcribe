# Audio → Pause-Aware Timestamped Transcript Tool

A web application that converts audio files into pause-aware timestamped transcripts using local open-source models (Whisper, Silero VAD).

## Project Structure

```
script-transcribe/
├── PLAN.md                          # Complete project plan
├── README.md                         # This file
│
├── phases/                           # Development phases
│   ├── phase1-local-engine/         # ✓ CLI transcription engine
│   ├── phase2-word-timestamps/
│   ├── phase3-pause-detection/
│   ├── phase4-chunking/
│   ├── phase5-txt-generation/
│   ├── phase6-fastapi/
│   ├── phase7-nextjs-frontend/
│   ├── phase8-error-handling/
│   └── phase9-performance/
│
├── backend/
│   ├── transcribe.py               # CLI entry point
│   ├── requirements.txt
│   │
│   ├── app/
│   │   ├── services/
│   │   │   ├── audio.py           # Audio validation & FFmpeg conversion
│   │   │   ├── transcription.py   # Whisper with word-level timestamps
│   │   │   ├── vad.py             # Silero VAD for silence detection
│   │   │   ├── chunking.py        # Pause-aware grouping
│   │   │   └── formatter.py       # Output formatting
│   │   │
│   │   ├── utils/
│   │   │   └── timestamps.py      # Timestamp utilities
│   │   │
│   │   └── models/
│   │       └── schemas.py         # Pydantic schemas (future)
│   │
│   └── tests/
│       ├── test_timestamps.py
│       ├── test_chunking.py
│       └── test_formatter.py
│
├── frontend/                        # Next.js UI (Phase 7)
│   ├── package.json
│   ├── app/
│   └── components/
│
└── docker/                         # Containerization (future)
    ├── frontend.Dockerfile
    └── backend.Dockerfile
```

## Quick Start

### Prerequisites
- Python 3.9+
- FFmpeg
- pip

### Setup

```bash
# 1. Install FFmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: apt-get install ffmpeg

# 2. Install Python dependencies
cd backend
pip install -r requirements.txt

# 3. Run transcription
python transcribe.py example.mp3
```

Output: `transcript.txt` with pause-aware timestamps

## Current Status: Phase 1 ✓

### Completed
- [x] Audio processing (validation, FFmpeg conversion)
- [x] Whisper transcription with word-level timestamps
- [x] Silero VAD integration
- [x] Pause-aware chunking algorithm
- [x] Output formatter
- [x] Timestamp utilities
- [x] Unit tests
- [x] CLI entry point

### Example Output
```
[0:00] You wake up to an alarm.
[0:01] You check the time.
[0:03] You already feel behind.
[0:05] You have emails.
[0:06] You have errands.
[0:07] You have a to-do list that never gets shorter,
[0:11] only longer.
[0:12] You tell yourself this is just how life works.
```

## Features

### Phase 1: Local Transcription Engine
✓ **Audio Input Support**
- MP3, WAV, M4A, MP4, WebM
- Automatic format detection
- File size validation (max 100 MB)
- Duration validation (max 60 min)

✓ **Transcription**
- Faster-Whisper models (small, medium, large-v3)
- Word-level timestamp precision
- Automatic language detection
- GPU/CPU auto-detection

✓ **Pause-Aware Chunking**
- Configurable pause threshold (default 0.7s)
- Punctuation boundaries (`.`, `?`, `!`)
- Maximum chunk length (default 15 words)
- Natural grouping based on speech patterns

✓ **Output**
- Timestamps in `[M:SS]` format
- Plain UTF-8 text files
- No metadata bloat

## Configuration

Current service defaults (will become configurable in Phase 6):

```python
# Pause Detection
pause_threshold = 0.7  # seconds

# Chunking
max_chunk_words = 15

# Transcription
whisper_model = "small"  # options: tiny, base, small, medium, large-v3

# Audio Limits
max_file_size = 100 * 1024 * 1024  # 100 MB
max_duration = 60 * 60              # 60 minutes
```

## Architecture

### Processing Pipeline
```
Audio Upload
    ↓
Validate (format, size, duration)
    ↓
FFmpeg → 16kHz Mono WAV
    ↓
Whisper Transcription
    ↓
Word-Level Timestamps
    ↓
Pause Detection
    ↓
Chunking Algorithm
    ↓
Timestamp Formatting
    ↓
TXT Generation
    ↓
Download
```

### Core Services

**AudioProcessor** (`audio.py`)
- Validates file format and size
- Detects audio duration
- Converts to 16kHz mono WAV using FFmpeg

**TranscriptionService** (`transcription.py`)
- Loads Whisper model
- Transcribes with word-level timestamps
- Detects language automatically
- Returns structured word data

**VADService** (`vad.py`)
- Uses Silero VAD for silence detection
- Identifies speech regions
- Helps validate pause detection

**ChunkingService** (`chunking.py`)
- Groups words into natural chunks
- Three chunking signals:
  1. Pause threshold
  2. Punctuation boundaries
  3. Maximum chunk length

**FormatterService** (`formatter.py`)
- Converts chunks to timestamped format
- Generates plain text output
- Calculates transcript statistics

## Testing

```bash
cd backend
pytest tests/ -v

# Test specific module
pytest tests/test_chunking.py -v
```

## Development Roadmap

### Phase 1 (Complete)
Local CLI transcription engine

### Phase 2
Word-level timestamp display and debugging

### Phase 3
Configurable pause thresholds and testing

### Phase 4
Refined chunking algorithm

### Phase 5
Final TXT generation and formatting

### Phase 6
FastAPI backend with HTTP endpoints

### Phase 7
Next.js frontend UI

### Phase 8
Comprehensive error handling

### Phase 9
Performance optimization and GPU support

## Cost

**Development: $0**
- All open-source components
- Local models (no API costs)
- Runs on your own hardware

**Production (future):**
- Domain + hosting: ~$10-50/month
- GPU if cloud-hosted: $100-500/month (optional)
- Database: $0-50/month (if needed)

## Next Steps

1. **Phase 2**: Expose word-level timestamps for debugging
2. **Phase 3**: Make pause threshold configurable
3. **Phase 4**: Fine-tune chunking algorithm with real audio samples
4. **Phase 5**: Generate final transcript format
5. **Phase 6**: Wrap with FastAPI (`POST /api/transcribe`)

## Technology Stack

**Backend**
- Python 3.9+
- FastAPI (Phase 6)
- faster-whisper (Whisper implementation)
- Silero VAD (Voice Activity Detection)
- FFmpeg (audio processing)

**Frontend** (Phase 7)
- Next.js 14+
- React 18+
- TypeScript
- Tailwind CSS

**Deployment** (Phase 9)
- Docker
- Optional: GPU worker + job queue for async processing

## Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

## License

MIT (to be configured)

## Contributing

This is a personal project. See PLAN.md for detailed implementation strategy.
