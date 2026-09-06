# Phase 6: FastAPI Backend

## Objective

Create REST API endpoints for transcription processing.

## Tasks

### 1. API Design

- [ ] POST /api/transcribe - Upload and transcribe audio
- [ ] GET /api/download/{job_id} - Download transcript
- [ ] GET /api/status/{job_id} - Check processing status

### 2. Request/Response Schema

- [ ] Define Pydantic schemas
- [ ] Add input validation
- [ ] Generate OpenAPI/Swagger docs

### 3. File Handling

- [ ] Temporary file management
- [ ] Job tracking
- [ ] Cleanup after download

## API Endpoints

```
POST /api/transcribe
├── Input: multipart/form-data
│   ├── file: audio file
│   ├── mode: "fast" | "accuracy" (default: "accuracy")
│   └── pause_threshold: float (default: 0.7)
└── Output: {job_id, status, download_url}

GET /api/status/{job_id}
└── Output: {status, progress, error}

GET /api/download/{job_id}
└── Output: transcript.txt file
```

## Success Criteria

- API endpoints functional
- Swagger docs generated
- File uploads working
- Downloads functional
