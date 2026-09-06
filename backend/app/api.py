"""
FastAPI REST API for audio transcription.
Phase 6: REST API backend.
"""

import os
import uuid
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import aiofiles

from app.services.audio import AudioProcessor
from app.services.transcription import TranscriptionService
from app.services.chunking import ChunkingService
from app.services.formatter import FormatterService


# Pydantic schemas for request/response validation
class TranscribeRequest(BaseModel):
    """Schema for transcription request (form data)."""
    mode: str = Field(default="accuracy", description="'fast' or 'accuracy'")
    pause_threshold: float = Field(default=0.7, description="Pause threshold in seconds (0.1-3.0)")
    output_format: str = Field(default="txt", description="Output format: txt, srt, vtt, or json")


class TranscribeResponse(BaseModel):
    """Schema for transcription response."""
    job_id: str = Field(description="Unique job identifier")
    status: str = Field(description="Job status: processing, completed, failed")
    download_url: Optional[str] = Field(default=None, description="URL to download transcript")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class StatusResponse(BaseModel):
    """Schema for job status response."""
    job_id: str = Field(description="Unique job identifier")
    status: str = Field(description="Job status: processing, completed, failed")
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# Job tracking (in-memory for now, can be replaced with database)
class JobTracker:
    """Simple in-memory job tracker."""

    def __init__(self):
        self.jobs = {}

    def create_job(self, job_id: str) -> None:
        """Create a new job."""
        self.jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'error': None,
            'output_file': None,
            'output_format': 'txt'
        }

    def update_job(self, job_id: str, status: str, progress: float = None, error: str = None) -> None:
        """Update job status."""
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = status
            if progress is not None:
                self.jobs[job_id]['progress'] = progress
            if error:
                self.jobs[job_id]['error'] = error

    def set_output(self, job_id: str, output_file: str, output_format: str) -> None:
        """Set output file path."""
        if job_id in self.jobs:
            self.jobs[job_id]['output_file'] = output_file
            self.jobs[job_id]['output_format'] = output_format

    def get_job(self, job_id: str) -> dict:
        """Get job info."""
        return self.jobs.get(job_id)

    def complete_job(self, job_id: str) -> None:
        """Mark job as completed."""
        self.update_job(job_id, 'completed', 100)


# Initialize FastAPI app and job tracker
app = FastAPI(
    title="Audio Transcription API",
    description="REST API for audio transcription with multiple output formats",
    version="1.0.0"
)

job_tracker = JobTracker()
temp_dir = tempfile.gettempdir()


@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    mode: str = Form(default="accuracy"),
    pause_threshold: float = Form(default=0.7),
    output_format: str = Form(default="txt")
) -> TranscribeResponse:
    """
    Upload and transcribe audio file.

    - **file**: Audio file (MP3, WAV, M4A, MP4, WebM)
    - **mode**: Processing mode (fast or accuracy)
    - **pause_threshold**: Pause detection threshold (0.1-3.0 seconds)
    - **output_format**: Output format (txt, srt, vtt, json)

    Returns job_id and download_url
    """
    try:
        # Validate input
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if pause_threshold < 0.1 or pause_threshold > 3.0:
            raise HTTPException(status_code=400, detail="pause_threshold must be between 0.1 and 3.0")

        if output_format not in ['txt', 'srt', 'vtt', 'json']:
            raise HTTPException(status_code=400, detail="output_format must be txt, srt, vtt, or json")

        # Create job
        job_id = str(uuid.uuid4())
        job_tracker.create_job(job_id)

        # Save uploaded file
        upload_path = os.path.join(temp_dir, f"{job_id}_input.mp3")
        async with aiofiles.open(upload_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Determine output filename
        extension = {
            'txt': '.txt',
            'srt': '.srt',
            'vtt': '.vtt',
            'json': '.json'
        }[output_format]

        output_path = os.path.join(temp_dir, f"{job_id}_transcript{extension}")

        # Process (simplified - in production would be async/background task)
        try:
            job_tracker.update_job(job_id, 'processing', 25)

            # Audio processing
            audio_processor = AudioProcessor()
            wav_file = audio_processor.process(upload_path)
            job_tracker.update_job(job_id, 'processing', 50)

            # Transcription
            transcription_service = TranscriptionService(
                model="tiny" if mode == "fast" else "small"
            )
            result = transcription_service.transcribe(wav_file)
            job_tracker.update_job(job_id, 'processing', 75)

            # Chunking
            chunking_service = ChunkingService(pause_threshold=pause_threshold)
            chunks = chunking_service.chunk(result['words'])

            # Formatting
            formatter = FormatterService()
            if output_format == 'txt':
                formatter.save_transcript(chunks, output_path)
            elif output_format == 'srt':
                formatter.save_srt(chunks, output_path)
            elif output_format == 'vtt':
                formatter.save_vtt(chunks, output_path)
            elif output_format == 'json':
                formatter.save_transcript_json(result['words'], chunks, output_path)

            # Cleanup temp files
            os.remove(upload_path)
            os.remove(wav_file)

            # Mark complete
            job_tracker.set_output(job_id, output_path, output_format)
            job_tracker.complete_job(job_id)

            return TranscribeResponse(
                job_id=job_id,
                status="completed",
                download_url=f"/api/download/{job_id}"
            )

        except Exception as e:
            job_tracker.update_job(job_id, 'failed', error=str(e))
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str) -> StatusResponse:
    """
    Check transcription job status.

    - **job_id**: Job identifier from /api/transcribe

    Returns job status and progress
    """
    job = job_tracker.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return StatusResponse(
        job_id=job_id,
        status=job['status'],
        progress=job.get('progress'),
        error=job.get('error')
    )


@app.get("/api/download/{job_id}")
async def download_transcript(job_id: str):
    """
    Download completed transcript.

    - **job_id**: Job identifier from /api/transcribe

    Returns transcript file
    """
    job = job_tracker.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Job status is {job['status']}, not completed")

    output_file = job['output_file']
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")

    # Determine media type based on format
    media_type = {
        'txt': 'text/plain',
        'srt': 'text/plain',
        'vtt': 'text/vtt',
        'json': 'application/json'
    }.get(job['output_format'], 'text/plain')

    return FileResponse(
        output_file,
        media_type=media_type,
        filename=f"transcript.{job['output_format']}"
    )


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "message": "Audio Transcription API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "transcribe": "POST /api/transcribe",
            "status": "GET /api/status/{job_id}",
            "download": "GET /api/download/{job_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
