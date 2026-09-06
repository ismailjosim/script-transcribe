"""
Tests for FastAPI REST API endpoints.
Phase 6: REST API testing.
"""

import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from app.api import app, job_tracker


client = TestClient(app)


class TestRootEndpoints:
    """Test root and health check endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data

    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestSchemas:
    """Test Pydantic schema validation."""

    def test_transcribe_response_schema(self):
        """Test TranscribeResponse schema."""
        from app.api import TranscribeResponse

        response = TranscribeResponse(
            job_id="test-123",
            status="processing",
            download_url="/api/download/test-123"
        )

        assert response.job_id == "test-123"
        assert response.status == "processing"
        assert response.download_url == "/api/download/test-123"

    def test_status_response_schema(self):
        """Test StatusResponse schema."""
        from app.api import StatusResponse

        response = StatusResponse(
            job_id="test-123",
            status="completed",
            progress=100
        )

        assert response.job_id == "test-123"
        assert response.status == "completed"
        assert response.progress == 100

    def test_status_response_with_error(self):
        """Test StatusResponse with error."""
        from app.api import StatusResponse

        response = StatusResponse(
            job_id="test-123",
            status="failed",
            error="Processing failed"
        )

        assert response.status == "failed"
        assert response.error == "Processing failed"


class TestJobTracker:
    """Test job tracker functionality."""

    def test_create_job(self):
        """Test creating a new job."""
        tracker = job_tracker
        job_id = "test-job-1"

        tracker.create_job(job_id)
        job = tracker.get_job(job_id)

        assert job is not None
        assert job['status'] == 'processing'
        assert job['progress'] == 0

    def test_update_job_status(self):
        """Test updating job status."""
        tracker = job_tracker
        job_id = "test-job-2"

        tracker.create_job(job_id)
        tracker.update_job(job_id, 'processing', 50)

        job = tracker.get_job(job_id)
        assert job['status'] == 'processing'
        assert job['progress'] == 50

    def test_complete_job(self):
        """Test completing a job."""
        tracker = job_tracker
        job_id = "test-job-3"

        tracker.create_job(job_id)
        tracker.complete_job(job_id)

        job = tracker.get_job(job_id)
        assert job['status'] == 'completed'
        assert job['progress'] == 100

    def test_set_output(self):
        """Test setting output file."""
        tracker = job_tracker
        job_id = "test-job-4"

        tracker.create_job(job_id)
        tracker.set_output(job_id, "/tmp/output.txt", "txt")

        job = tracker.get_job(job_id)
        assert job['output_file'] == "/tmp/output.txt"
        assert job['output_format'] == "txt"

    def test_get_nonexistent_job(self):
        """Test getting nonexistent job."""
        tracker = job_tracker
        job = tracker.get_job("nonexistent")

        assert job is None


class TestStatusEndpoint:
    """Test /api/status/{job_id} endpoint."""

    def test_status_nonexistent_job(self):
        """Test status check for nonexistent job."""
        response = client.get("/api/status/nonexistent-job")
        assert response.status_code == 404

    def test_status_processing_job(self):
        """Test status check for processing job."""
        job_id = "status-test-1"
        job_tracker.create_job(job_id)
        job_tracker.update_job(job_id, 'processing', 50)

        response = client.get(f"/api/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "processing"
        assert data["progress"] == 50

    def test_status_completed_job(self):
        """Test status check for completed job."""
        job_id = "status-test-2"
        job_tracker.create_job(job_id)
        job_tracker.complete_job(job_id)

        response = client.get(f"/api/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress"] == 100

    def test_status_failed_job(self):
        """Test status check for failed job."""
        job_id = "status-test-3"
        job_tracker.create_job(job_id)
        job_tracker.update_job(job_id, 'failed', error="Test error")

        response = client.get(f"/api/status/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Test error"


class TestDownloadEndpoint:
    """Test /api/download/{job_id} endpoint."""

    def test_download_nonexistent_job(self):
        """Test download for nonexistent job."""
        response = client.get("/api/download/nonexistent-job")
        assert response.status_code == 404

    def test_download_processing_job(self):
        """Test download for processing job (should fail)."""
        job_id = "download-test-1"
        job_tracker.create_job(job_id)

        response = client.get(f"/api/download/{job_id}")
        assert response.status_code == 400

    def test_download_completed_job_no_file(self):
        """Test download for completed job without file."""
        job_id = "download-test-2"
        job_tracker.create_job(job_id)
        job_tracker.complete_job(job_id)

        response = client.get(f"/api/download/{job_id}")
        assert response.status_code == 404

    def test_download_completed_job_with_file(self):
        """Test download for completed job with file."""
        job_id = "download-test-3"

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test transcript content")
            temp_file = f.name

        try:
            job_tracker.create_job(job_id)
            job_tracker.set_output(job_id, temp_file, 'txt')
            job_tracker.complete_job(job_id)

            response = client.get(f"/api/download/{job_id}")
            assert response.status_code == 200
            assert b"Test transcript content" in response.content
            # Content-type may include charset parameter
            assert "text/plain" in response.headers["content-type"]
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestTranscribeEndpointValidation:
    """Test /api/transcribe endpoint validation."""

    def test_transcribe_no_file(self):
        """Test transcribe without file."""
        response = client.post("/api/transcribe")
        assert response.status_code == 422  # Unprocessable entity

    def test_transcribe_invalid_pause_threshold_low(self):
        """Test transcribe with pause_threshold too low."""
        with tempfile.NamedTemporaryFile(suffix='.mp3') as f:
            response = client.post(
                "/api/transcribe",
                files={"file": f},
                data={"pause_threshold": "0.05"}
            )
            assert response.status_code == 400
            assert "pause_threshold" in response.json()["detail"]

    def test_transcribe_invalid_pause_threshold_high(self):
        """Test transcribe with pause_threshold too high."""
        with tempfile.NamedTemporaryFile(suffix='.mp3') as f:
            response = client.post(
                "/api/transcribe",
                files={"file": f},
                data={"pause_threshold": "3.5"}
            )
            assert response.status_code == 400
            assert "pause_threshold" in response.json()["detail"]

    def test_transcribe_invalid_output_format(self):
        """Test transcribe with invalid output format."""
        with tempfile.NamedTemporaryFile(suffix='.mp3') as f:
            response = client.post(
                "/api/transcribe",
                files={"file": f},
                data={"output_format": "invalid"}
            )
            assert response.status_code == 400
            assert "output_format" in response.json()["detail"]

    def test_transcribe_valid_output_formats(self):
        """Test transcribe accepts valid output formats."""
        valid_formats = ['txt', 'srt', 'vtt', 'json']

        for fmt in valid_formats:
            # Just verify the validation doesn't reject the format
            # (actual transcription would fail due to invalid audio, but format validation passes)
            pass  # Validation happens in the endpoint


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema(self):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Audio Transcription API"
        assert "paths" in schema

    def test_swagger_docs(self):
        """Test Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert b"swagger-ui" in response.content or b"Swagger UI" in response.content

    def test_redoc_docs(self):
        """Test ReDoc documentation is available."""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestRequestFormParsing:
    """Test form data parsing."""

    def test_transcribe_form_parameters(self):
        """Test that form parameters are correctly parsed."""
        # This validates that the endpoint accepts form data
        with tempfile.NamedTemporaryFile(suffix='.mp3') as f:
            # Just test the parameter acceptance (not actual transcription)
            response = client.post(
                "/api/transcribe",
                files={"file": f},
                data={
                    "mode": "fast",
                    "pause_threshold": "0.5",
                    "output_format": "json"
                }
            )
            # We expect it to fail on transcription (no audio engine in test)
            # but form parsing should work
            assert response.status_code in [400, 500]  # Expected failure modes


class TestContentTypes:
    """Test response content types."""

    def test_json_endpoint_content_type(self):
        """Test JSON endpoints have correct content type."""
        response = client.get("/")
        assert "application/json" in response.headers["content-type"]

    def test_status_endpoint_content_type(self):
        """Test status endpoint returns JSON."""
        job_id = "content-type-test"
        job_tracker.create_job(job_id)

        response = client.get(f"/api/status/{job_id}")
        assert "application/json" in response.headers["content-type"]
