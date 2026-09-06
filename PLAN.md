# Audio → Pause-Aware Timestamped Transcript Tool

## Project Plan

## 1. Project Goal

Build a web application where a user uploads an audio file and receives
a downloadable `.txt` transcript formatted like:

``` text
[0:00] You wake up to an alarm.
[0:01] You check the time.
[0:03] You already feel behind.
[0:05] You have emails.
[0:06] You have errands.
[0:07] You have a to-do list that never gets shorter,
[0:11] only longer.
[0:12] You tell yourself this is just how life works.
```

The defining feature is **pause-aware timestamping**.

The application should not simply split text into arbitrary sentences.
It should use the actual audio timing to determine when a new
timestamped line/chunk begins.

------------------------------------------------------------------------

# 2. Core Product Requirements

### Input

Support initially:

-   MP3
-   WAV
-   M4A
-   MP4/audio-containing video
-   WebM if practical

### Output

Generate:

-   `.txt` file
-   Timestamp format: `[M:SS]`
-   Timestamp represents the beginning of each generated text chunk
-   Preserve the spoken wording as accurately as possible

### Main processing pipeline

``` text
Upload
  ↓
Validate file
  ↓
FFmpeg audio extraction/normalization
  ↓
Voice Activity Detection
  ↓
Whisper transcription
  ↓
Word-level timestamps
  ↓
Pause detection
  ↓
Chunking algorithm
  ↓
Timestamp formatting
  ↓
TXT generation
  ↓
Download
```

------------------------------------------------------------------------

# 3. Recommended Technology Stack

## Frontend

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   Native HTML audio player initially

## Backend

-   Python
-   FastAPI

## Speech-to-text

-   `faster-whisper`

Recommended models:

-   Development: `small` or `medium`
-   Higher accuracy: `large-v3` or an appropriate distilled model

## Voice Activity Detection

-   Silero VAD

## Audio processing

-   FFmpeg

## Temporary storage

Development:

-   Local filesystem

Production:

-   Object storage such as S3-compatible storage if needed

## Database

Not required for MVP.

Add PostgreSQL later only if the application needs:

-   user accounts
-   job history
-   saved transcripts
-   usage tracking
-   billing
-   analytics

------------------------------------------------------------------------

# 4. Why Word-Level Timestamps Are Required

Do not build the first version around ordinary sentence-level
transcription.

The application needs information similar to:

``` text
word       start    end
-------------------------
You        0.20     0.42
wake       0.43     0.70
up         0.71     0.88
to         0.89     0.97
an         0.98     1.07
alarm      1.08     1.44
You        2.10     2.36
check      2.37     2.61
the        2.62     2.73
time       2.74     2.98
```

The program can then calculate:

``` text
pause = next_word.start - previous_word.end
```

For example:

``` text
2.10 - 1.44 = 0.66 seconds
```

This timing information is the foundation of the pause-aware transcript.

------------------------------------------------------------------------

# 5. Pause Detection Strategy

Start with a configurable pause threshold.

Recommended initial default:

``` text
0.7 seconds
```

Example:

``` text
pause < 0.7 seconds
    → continue current chunk

pause >= 0.7 seconds
    → start a new timestamped chunk
```

Do not assume one threshold will work perfectly for every speaker.

Eventually expose:

``` text
Pause Sensitivity

0.3s
0.5s
0.7s  ← default
1.0s
1.5s
```

------------------------------------------------------------------------

# 6. Chunking Algorithm

The first implementation should use three signals.

## Signal 1: Audio pause

Create a new chunk when:

``` text
pause >= configured threshold
```

## Signal 2: Punctuation

Consider a natural boundary after:

``` text
.
?
!
```

Do not blindly split after every comma.

## Signal 3: Maximum chunk length

Prevent very long lines.

Initial target:

``` text
10–15 words
```

Example algorithm:

``` python
for each word:

    if current chunk is empty:
        add word
        continue

    pause = current_word.start - previous_word.end

    punctuation_break = previous_word ends with ".", "?", or "!"

    too_long = current_chunk contains maximum number of words

    if pause >= pause_threshold:
        finish current chunk
        start new chunk

    elif punctuation_break:
        finish current chunk
        start new chunk

    elif too_long:
        finish current chunk
        start new chunk

    else:
        add word to current chunk
```

This should be treated as the initial algorithm, not the final
algorithm.

------------------------------------------------------------------------

# 7. Important Timestamp Rule

The timestamp should normally be based on:

``` text
chunk[0].start
```

Example:

``` text
chunk starts at 7.84 seconds

→ [0:07]
```

Use floor/integer seconds for the initial TXT format.

Later, optionally support:

``` text
[0:07.84]
```

for users who need precise timing.

------------------------------------------------------------------------

# 8. Output Formatter

Create:

``` text
transcript.txt
```

Example:

``` text
[0:00] You wake up to an alarm.
[0:01] You check the time.
[0:03] You already feel behind.
[0:05] You have emails.
[0:06] You have errands.
[0:07] You have a to-do list that never gets shorter,
[0:11] only longer.
[0:12] You tell yourself this is just how life works.
[0:16] Modern life is busy.
[0:17] Ancient life must have been impossible.
```

The generated file should be plain UTF-8 text.

------------------------------------------------------------------------

# 9. Project Structure

Recommended monorepo:

``` text
audio-transcriber/
│
├── README.md
├── PLAN.md
├── .gitignore
├── docker-compose.yml
│
├── frontend/
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   │
│   ├── components/
│   │   ├── AudioUploader.tsx
│   │   ├── AudioPreview.tsx
│   │   ├── ProcessingOptions.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── TranscriptPreview.tsx
│   │   └── DownloadButton.tsx
│   │
│   └── lib/
│       └── api.ts
│
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── services/
│   │   │   ├── audio.py
│   │   │   ├── transcription.py
│   │   │   ├── vad.py
│   │   │   ├── chunking.py
│   │   │   └── formatter.py
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   └── utils/
│   │       └── timestamps.py
│   │
│   ├── tests/
│   │   ├── test_chunking.py
│   │   ├── test_formatter.py
│   │   └── test_timestamps.py
│   │
│   └── temp/
│
└── docker/
    ├── frontend.Dockerfile
    └── backend.Dockerfile
```

------------------------------------------------------------------------

# 10. API Design

## POST `/api/transcribe`

Input:

``` text
multipart/form-data
```

Fields:

``` text
file
mode
pause_threshold
```

Example:

``` text
file = audio.mp3
mode = accuracy
pause_threshold = 0.7
```

Response:

``` json
{
  "job_id": "abc123",
  "status": "completed",
  "filename": "transcript.txt",
  "download_url": "/api/download/abc123"
}
```

For the first MVP, processing can be synchronous for short files.

For longer files, move to background jobs.

------------------------------------------------------------------------

# 11. Processing Service Design

## `audio.py`

Responsibilities:

-   Validate file
-   Detect file type
-   Call FFmpeg
-   Convert to suitable WAV/PCM format
-   Normalize audio if necessary
-   Remove temporary files after processing

## `transcription.py`

Responsibilities:

-   Load faster-whisper
-   Select model
-   Transcribe audio
-   Enable word timestamps
-   Return words and timestamps

Conceptual result:

``` python
[
    {
        "text": "You",
        "start": 0.20,
        "end": 0.42
    },
    ...
]
```

## `vad.py`

Responsibilities:

-   Detect speech regions
-   Detect long silence
-   Help prevent false pause detection caused by noise

## `chunking.py`

Responsibilities:

-   Calculate pauses
-   Apply pause threshold
-   Apply punctuation boundaries
-   Apply maximum chunk length
-   Return natural chunks

## `formatter.py`

Responsibilities:

-   Convert seconds to `[M:SS]`
-   Join words
-   Create TXT content
-   Write UTF-8 file

------------------------------------------------------------------------

# 12. Frontend UX

Build the interface in stages.

## Initial screen

``` text
Turn Audio Into Accurate Text

Upload any audio → language auto-detected
→ pause-aware timestamped transcript
```

Upload area:

``` text
┌───────────────────────────────────────┐
│                                       │
│       Upload your audio               │
│                                       │
│       MP3 • WAV • M4A • MP4           │
│                                       │
└───────────────────────────────────────┘
```

After upload:

``` text
audio.mp3
4m 56s

[ audio player ]

✓ Uploaded — ready to transcribe
```

Options:

``` text
Transcription Quality

○ Fast
  Faster processing

● Accuracy
  Better transcription
```

Pause settings:

``` text
Pause threshold

[ 0.7 seconds ]
```

Button:

``` text
[ Transcribe Audio ]
```

------------------------------------------------------------------------

# 13. Processing States

The frontend should show clear states:

``` text
idle
↓
uploading
↓
uploaded
↓
processing
↓
transcribing
↓
detecting pauses
↓
generating transcript
↓
completed
```

Possible UI:

``` text
Uploading audio...
████████░░░░░░░░ 50%
```

Then:

``` text
Transcribing audio...
```

Then:

``` text
Detecting pauses...
```

Finally:

``` text
✓ Transcript ready

[ Download TXT ]
```

------------------------------------------------------------------------

# 14. Transcript Preview

Before downloading, show:

``` text
Transcript Preview

[0:00] You wake up to an alarm.
[0:01] You check the time.
[0:03] You already feel behind.
[0:05] You have emails.
[0:06] You have errands.
...
```

Also show:

``` text
Words: 824
Duration: 4:56
Language: English
```

------------------------------------------------------------------------

# 15. Fast vs Accuracy Modes

## Fast

Use a smaller/faster Whisper model.

Goal:

``` text
lower CPU/GPU usage
faster processing
good enough transcription
```

## Accuracy

Use a larger model.

Goal:

``` text
better recognition
better handling of difficult speech
better multilingual performance
```

Do not promise that the larger model will always be perfect.

------------------------------------------------------------------------

# 16. Language Detection

Whisper can detect the spoken language.

Store:

``` text
language
language_probability
```

Example:

``` json
{
  "language": "en",
  "language_probability": 0.98
}
```

Display:

``` text
Language: English
```

Later support manual language selection:

``` text
Auto Detect
English
Bangla
Hindi
Spanish
French
German
Japanese
...
```

------------------------------------------------------------------------

# 17. Audio Validation

Before processing:

-   Reject unsupported formats
-   Check file size
-   Check duration
-   Prevent empty files
-   Prevent obviously invalid audio
-   Generate safe temporary filenames

Initial limits can be something like:

``` text
Maximum file size: 100 MB
Maximum duration: 60 minutes
```

These are product settings, not technical requirements.

Increase them later if needed.

------------------------------------------------------------------------

# 18. Security Requirements

Never trust the uploaded filename.

Do not execute user-supplied filenames as shell commands.

Use:

``` text
UUID/random temporary filename
```

Run FFmpeg safely using argument arrays rather than constructing unsafe
shell strings.

Delete uploaded temporary files after processing.

Set reasonable:

-   file size limits
-   duration limits
-   request timeouts
-   concurrency limits

If the service becomes public, add rate limiting.

------------------------------------------------------------------------

# 19. MVP Development Order

## Phase 1 --- Local transcription engine

Do NOT build the beautiful frontend yet.

Create a Python script:

``` text
transcribe.py audio.mp3
```

It should produce:

``` text
transcript.txt
```

Success criteria:

``` text
audio.mp3
    ↓
transcribe.py
    ↓
transcript.txt
```

------------------------------------------------------------------------

## Phase 2 --- Word timestamps

Add:

``` text
word.start
word.end
```

Print the timestamps to the terminal.

Verify that they correspond to the audio.

------------------------------------------------------------------------

## Phase 3 --- Pause detection

Implement:

``` text
pause = next.start - previous.end
```

Test:

``` text
0.3 sec
0.5 sec
0.7 sec
1.0 sec
1.5 sec
```

Find a useful default.

------------------------------------------------------------------------

## Phase 4 --- Chunking

Implement:

-   pause boundary
-   punctuation boundary
-   maximum chunk length

Generate the desired format.

------------------------------------------------------------------------

## Phase 5 --- TXT generation

Make sure the output is exactly:

``` text
[0:00] ...
[0:01] ...
[0:03] ...
```

No unnecessary metadata.

------------------------------------------------------------------------

## Phase 6 --- FastAPI

Create:

``` text
POST /api/transcribe
GET  /api/download/{job_id}
```

Test using Swagger/OpenAPI or curl.

------------------------------------------------------------------------

## Phase 7 --- Next.js frontend

Build:

1.  Upload UI
2.  Audio preview
3.  Processing options
4.  Progress state
5.  Transcript preview
6.  Download button

------------------------------------------------------------------------

## Phase 8 --- Error handling

Handle:

-   invalid audio
-   corrupted files
-   unsupported formats
-   transcription failures
-   FFmpeg failures
-   model loading errors
-   out-of-memory errors
-   very long audio
-   no speech detected

------------------------------------------------------------------------

## Phase 9 --- Performance

Measure:

``` text
audio duration
processing duration
CPU usage
RAM usage
model loading time
```

Then optimize.

------------------------------------------------------------------------

# 20. Testing Strategy

Create a test audio collection containing:

### Test A --- Normal speech

``` text
Hello, this is a test.
```

### Test B --- Long pause

``` text
Hello.

[2 second pause]

This is another sentence.
```

Expected:

``` text
[0:00] Hello.
[0:02] This is another sentence.
```

### Test C --- Short pause

``` text
Hello, this is a test.
```

Expected to remain a natural chunk.

### Test D --- Fast speaker

Test whether words and pauses are still correctly aligned.

### Test E --- Multiple speakers

Determine how the system behaves before implementing speaker
diarization.

### Test F --- Background noise

Test VAD and transcription quality.

### Test G --- Multilingual audio

Verify language detection.

------------------------------------------------------------------------

# 21. Important Product Decision: Do Not Add Speaker Diarization Initially

Version 1 should focus on:

``` text
audio → accurate text → pause timestamps
```

Do not initially add:

``` text
Speaker 1:
Speaker 2:
```

Speaker diarization makes the system more complicated.

Add it later if needed.

------------------------------------------------------------------------

# 22. Optional Future Features

After the MVP works:

## Export formats

-   TXT
-   SRT
-   VTT
-   JSON
-   CSV

## Editing

Allow users to edit:

``` text
[0:07] You have a to-do list...
```

directly in the browser.

## Timestamp precision

Support:

``` text
[0:07]
[0:07.84]
```

## Custom pause threshold

Let users control sensitivity.

## AI cleanup mode

Optional:

``` text
Raw Transcript
Clean Transcript
```

Important: keep the raw transcript available so AI rewriting does not
accidentally change the spoken meaning.

## Speaker detection

``` text
Speaker 1
Speaker 2
```

## Search

Search within transcripts.

## Batch processing

Upload multiple audio files.

## Accounts

Add authentication only when necessary.

------------------------------------------------------------------------

# 23. Cost Plan

## Local development

You can build the entire MVP for **\$0 in software/API fees** if you run
the models locally.

The main components are open-source/free to use:

``` text
Python              $0
FastAPI              $0
Next.js              $0
React                $0
faster-whisper       $0
Silero VAD           $0
FFmpeg               $0
Tailwind CSS         $0
```

Your computer does the transcription.

------------------------------------------------------------------------

# 24. Hardware Cost

The main limitation of local transcription is hardware.

A GPU makes larger Whisper models much faster.

You can still develop on CPU, but processing may be slower.

If you already have a suitable computer:

``` text
Additional software cost = $0
```

You do not need an ElevenLabs subscription to create this transcription
system.

------------------------------------------------------------------------

# 25. When Money Becomes Necessary

You only need to spend money when you want to turn the local project
into a hosted public service.

Possible costs:

``` text
Domain
Hosting server
Cloud GPU
Cloud storage
Database
Monitoring
Email service
```

The biggest potential cost is GPU compute if you want users to upload
audio and have your server run large Whisper models.

------------------------------------------------------------------------

# 26. Cheapest Development Strategy

Start completely locally:

``` text
Your PC
 │
 ├── Next.js
 ├── FastAPI
 ├── FFmpeg
 ├── faster-whisper
 └── Silero VAD
```

No paid API.

No database.

No cloud.

No authentication.

No payment system.

Build the complete pipeline first.

------------------------------------------------------------------------

# 27. Production Architecture Later

When the MVP works:

``` text
                    ┌───────────────┐
                    │    Browser    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Next.js    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    └───────┬───────┘
                            │
                     create job
                            │
                            ▼
                    ┌───────────────┐
                    │    Job Queue  │
                    └───────┬───────┘
                            │
                            ▼
                 ┌────────────────────┐
                 │   GPU Worker(s)    │
                 │                    │
                 │ faster-whisper     │
                 │ Silero VAD         │
                 │ FFmpeg             │
                 └─────────┬──────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │ Object Storage│
                    └───────────────┘
```

Only introduce this architecture when traffic requires it.

------------------------------------------------------------------------

# 28. Monetization Possibilities

If you eventually turn it into a SaaS:

### Free

``` text
10 minutes/month
```

### Starter

``` text
X minutes/month
```

### Pro

``` text
larger limits
faster processing
SRT/VTT export
batch processing
```

The exact pricing should be determined after measuring your actual
server/GPU cost.

------------------------------------------------------------------------

# 29. Definition of Done for MVP

The MVP is complete when all of these work:

-   [ ] User can upload MP3
-   [ ] Audio duration is detected
-   [ ] Audio can be played in browser
-   [ ] Backend receives the file
-   [ ] FFmpeg processes the audio
-   [ ] Whisper transcribes it
-   [ ] Word-level timestamps are available
-   [ ] Silence/pause duration is calculated
-   [ ] Pause threshold is configurable
-   [ ] Text is grouped into natural chunks
-   [ ] Timestamps use `[M:SS]`
-   [ ] `.txt` file is generated
-   [ ] User can preview the transcript
-   [ ] User can download the `.txt`
-   [ ] Temporary files are deleted
-   [ ] Basic error handling works
-   [ ] Tests cover pause/chunk logic

------------------------------------------------------------------------

# 30. Recommended First Milestone

Do not start by copying the screenshot UI.

First make this command work:

``` bash
python transcribe.py example.mp3
```

and produce:

``` text
transcript.txt
```

with:

``` text
[0:00] You wake up to an alarm.
[0:01] You check the time.
[0:03] You already feel behind.
...
```

Once that works reliably, build the FastAPI API.

Once the API works, build the Next.js interface.

This order dramatically reduces debugging complexity.

------------------------------------------------------------------------

# 31. Final Development Roadmap

``` text
WEEK / STAGE 1
────────────────────────────
Python
FFmpeg
faster-whisper
Silero VAD
Word timestamps

                ↓

STAGE 2
────────────────────────────
Pause detection
Chunking
Timestamp formatter
TXT generator

                ↓

STAGE 3
────────────────────────────
FastAPI
Upload endpoint
Transcription endpoint
Download endpoint

                ↓

STAGE 4
────────────────────────────
Next.js
Upload UI
Audio player
Progress UI
Transcript preview
Download UI

                ↓

STAGE 5
────────────────────────────
Testing
Error handling
Performance
Large files

                ↓

STAGE 6
────────────────────────────
Deployment
GPU worker
Storage
Rate limiting
Monitoring

                ↓

STAGE 7
────────────────────────────
Accounts
History
SRT/VTT
Batch processing
Speaker diarization
AI cleanup
Payments
```

# 32. Bottom Line

For the first version:

``` text
                    COST

Software             $0
Whisper               $0
Silero VAD            $0
FFmpeg                $0
Next.js               $0
FastAPI               $0
API calls             $0
Database              $0
Cloud hosting         $0
                         ───
Development total     $0
```

**provided you run everything locally on your own computer.**

The first thing you should build is therefore **not the UI**. Build the
local Python transcription engine and prove that it can turn a real
audio recording into the exact pause-aware `.txt` format you want. Then
put the web application around that engine.
