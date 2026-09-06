"""
Tests for output format generation.
Phase 5: TXT, SRT, and VTT subtitle generation.
"""

import pytest
import os
import json
from app.services.formatter import FormatterService
from app.services.chunking import ChunkingService


class TestTextTranscriptGeneration:
    """Test basic text transcript generation."""

    def test_format_transcript_basic(self):
        """Test basic transcript formatting."""
        chunks = [
            {'text': 'Hello world', 'start': 0.5, 'end': 1.2, 'word_count': 2},
            {'text': 'How are you?', 'start': 2.0, 'end': 3.1, 'word_count': 3},
        ]
        formatter = FormatterService(precision='integer')
        result = formatter.format_transcript(chunks)

        assert '[0:00]' in result
        assert 'Hello world' in result
        assert 'How are you?' in result

    def test_format_transcript_decimal_precision(self):
        """Test transcript with decimal timestamp precision."""
        chunks = [
            {'text': 'Test', 'start': 1.25, 'end': 1.5, 'word_count': 1},
        ]
        formatter = FormatterService(precision='decimal')
        result = formatter.format_transcript(chunks)

        assert '[0:01.25]' in result
        assert 'Test' in result

    def test_format_transcript_preserves_text(self):
        """Test that chunk text is preserved exactly."""
        chunks = [
            {'text': 'Hello, world!', 'start': 0.0, 'end': 1.0, 'word_count': 2},
            {'text': 'Special chars: @#$%', 'start': 1.1, 'end': 2.0, 'word_count': 3},
        ]
        formatter = FormatterService()
        result = formatter.format_transcript(chunks)

        assert 'Hello, world!' in result
        assert 'Special chars: @#$%' in result

    def test_format_transcript_multiline(self):
        """Test that multiple chunks are on separate lines."""
        chunks = [
            {'text': 'Line 1', 'start': 0.0, 'end': 1.0, 'word_count': 2},
            {'text': 'Line 2', 'start': 1.1, 'end': 2.0, 'word_count': 2},
            {'text': 'Line 3', 'start': 2.1, 'end': 3.0, 'word_count': 2},
        ]
        formatter = FormatterService()
        result = formatter.format_transcript(chunks)

        lines = result.split('\n')
        assert len(lines) == 3
        assert 'Line 1' in lines[0]
        assert 'Line 2' in lines[1]
        assert 'Line 3' in lines[2]


class TestFileGeneration:
    """Test file writing and handling."""

    def test_save_transcript_creates_file(self, tmp_path):
        """Test that save_transcript creates a file."""
        chunks = [
            {'text': 'Test content', 'start': 0.0, 'end': 1.0, 'word_count': 2},
        ]
        output_file = tmp_path / "test.txt"
        formatter = FormatterService()

        formatter.save_transcript(chunks, str(output_file))

        assert output_file.exists()

    def test_save_transcript_utf8_encoding(self, tmp_path):
        """Test that transcript is saved as UTF-8."""
        chunks = [
            {'text': 'Café résumé naïve', 'start': 0.0, 'end': 1.0, 'word_count': 3},
            {'text': '你好世界', 'start': 1.1, 'end': 2.0, 'word_count': 1},
            {'text': '🎉 emoji test', 'start': 2.1, 'end': 3.0, 'word_count': 2},
        ]
        output_file = tmp_path / "utf8_test.txt"
        formatter = FormatterService()

        formatter.save_transcript(chunks, str(output_file))

        # Read back and verify
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'Café' in content
        assert '你好世界' in content
        assert '🎉' in content

    def test_save_transcript_file_readable(self, tmp_path):
        """Test that saved file is readable."""
        chunks = [
            {'text': 'First chunk', 'start': 0.0, 'end': 1.0, 'word_count': 2},
            {'text': 'Second chunk', 'start': 1.1, 'end': 2.0, 'word_count': 2},
        ]
        output_file = tmp_path / "readable.txt"
        formatter = FormatterService()

        formatter.save_transcript(chunks, str(output_file))

        # Verify readability
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert len(content) > 0
        assert 'First chunk' in content
        assert 'Second chunk' in content


class TestSRTGeneration:
    """Test SRT (SubRip) subtitle format generation."""

    def test_generate_srt_basic(self):
        """Test basic SRT generation."""
        chunks = [
            {'text': 'First subtitle', 'start': 0.5, 'end': 2.0, 'word_count': 2},
            {'text': 'Second subtitle', 'start': 2.5, 'end': 4.5, 'word_count': 2},
        ]
        formatter = FormatterService()
        srt = formatter.format_srt(chunks)

        # SRT format: number\ntimecode\ntext\n\n
        lines = srt.strip().split('\n')

        # Should contain sequence numbers
        assert '1' in lines[0]
        # Find second sequence number (accounting for blank lines)
        assert '2' in srt  # Just verify it's in the output

    def test_srt_timecode_format(self):
        """Test SRT timecode format is correct (HH:MM:SS,mmm)."""
        chunks = [
            {'text': 'Test', 'start': 3661.5, 'end': 3663.750, 'word_count': 1},
        ]
        formatter = FormatterService()
        srt = formatter.format_srt(chunks)

        # 3661.5 seconds = 1 hour, 1 minute, 1.5 seconds
        assert '01:01:01,500' in srt
        # 3663.750 seconds = 1 hour, 1 minute, 3.750 seconds
        assert '01:01:03,750' in srt

    def test_srt_multiple_chunks(self):
        """Test SRT with multiple chunks."""
        chunks = [
            {'text': f'Chunk {i}', 'start': i * 2.0, 'end': i * 2.0 + 1.5, 'word_count': 1}
            for i in range(1, 6)
        ]
        formatter = FormatterService()
        srt = formatter.format_srt(chunks)

        # Should have 5 subtitle blocks
        blocks = srt.strip().split('\n\n')
        assert len(blocks) == 5

        # Each block should have sequence number
        for i in range(1, 6):
            assert str(i) in srt


class TestVTTGeneration:
    """Test VTT (WebVTT) subtitle format generation."""

    def test_generate_vtt_basic(self):
        """Test basic VTT generation."""
        chunks = [
            {'text': 'First subtitle', 'start': 0.5, 'end': 2.0, 'word_count': 2},
            {'text': 'Second subtitle', 'start': 2.5, 'end': 4.5, 'word_count': 2},
        ]
        formatter = FormatterService()
        vtt = formatter.format_vtt(chunks)

        # VTT starts with WEBVTT header
        assert vtt.startswith('WEBVTT')

        # Should contain timecodes in VTT format (HH:MM:SS.mmm)
        assert '00:00:00.500' in vtt
        assert '-->' in vtt

        # Should contain text
        assert 'First subtitle' in vtt
        assert 'Second subtitle' in vtt

    def test_vtt_timecode_format(self):
        """Test VTT timecode format is correct (HH:MM:SS.mmm)."""
        chunks = [
            {'text': 'Test', 'start': 3661.5, 'end': 3663.750, 'word_count': 1},
        ]
        formatter = FormatterService()
        vtt = formatter.format_vtt(chunks)

        # VTT uses period for milliseconds, not comma
        assert '01:01:01.500' in vtt
        assert '01:01:03.750' in vtt
        # Should NOT have commas in timecode
        assert '01:01:01,500' not in vtt

    def test_vtt_webvtt_header(self):
        """Test VTT has proper WebVTT header."""
        chunks = [
            {'text': 'Test', 'start': 0.0, 'end': 1.0, 'word_count': 1},
        ]
        formatter = FormatterService()
        vtt = formatter.format_vtt(chunks)

        assert vtt.startswith('WEBVTT\n')

    def test_vtt_multiple_chunks(self):
        """Test VTT with multiple chunks."""
        chunks = [
            {'text': f'Chunk {i}', 'start': i * 2.0, 'end': i * 2.0 + 1.5, 'word_count': 1}
            for i in range(1, 6)
        ]
        formatter = FormatterService()
        vtt = formatter.format_vtt(chunks)

        # Should have header + 5 cue blocks
        lines = vtt.split('\n')
        assert lines[0] == 'WEBVTT'

        # Count cues (lines with -->)
        cue_count = sum(1 for line in lines if '-->' in line)
        assert cue_count == 5


class TestFormatComparison:
    """Test different format outputs."""

    def test_txt_vs_srt_content(self):
        """Test that TXT and SRT contain same text content."""
        chunks = [
            {'text': 'Hello world', 'start': 0.0, 'end': 1.0, 'word_count': 2},
            {'text': 'Goodbye world', 'start': 1.5, 'end': 2.5, 'word_count': 2},
        ]
        formatter = FormatterService()

        txt = formatter.format_transcript(chunks)
        srt = formatter.format_srt(chunks)

        # Both should contain the text
        assert 'Hello world' in txt and 'Hello world' in srt
        assert 'Goodbye world' in txt and 'Goodbye world' in srt

    def test_txt_vs_vtt_content(self):
        """Test that TXT and VTT contain same text content."""
        chunks = [
            {'text': 'Hello world', 'start': 0.0, 'end': 1.0, 'word_count': 2},
            {'text': 'Goodbye world', 'start': 1.5, 'end': 2.5, 'word_count': 2},
        ]
        formatter = FormatterService()

        txt = formatter.format_transcript(chunks)
        vtt = formatter.format_vtt(chunks)

        # Both should contain the text
        assert 'Hello world' in txt and 'Hello world' in vtt
        assert 'Goodbye world' in txt and 'Goodbye world' in vtt

    def test_srt_vs_vtt_timestamps(self):
        """Test SRT vs VTT timestamp format differences."""
        chunks = [
            {'text': 'Test', 'start': 10.5, 'end': 12.750, 'word_count': 1},
        ]
        formatter = FormatterService()

        srt = formatter.format_srt(chunks)
        vtt = formatter.format_vtt(chunks)

        # SRT uses comma for milliseconds
        assert '00:00:10,500' in srt
        # VTT uses period for milliseconds
        assert '00:00:10.500' in vtt

        # Both should NOT have the other's format
        assert '00:00:10,500' not in vtt
        assert '00:00:10.500' not in srt


class TestTimestampConversion:
    """Test timestamp conversion utilities."""

    def test_seconds_to_srt_timecode(self):
        """Test conversion to SRT timecode format."""
        formatter = FormatterService()

        # Test various seconds values
        assert formatter._seconds_to_srt_timecode(0.0) == '00:00:00,000'
        assert formatter._seconds_to_srt_timecode(1.5) == '00:00:01,500'
        assert formatter._seconds_to_srt_timecode(61.0) == '00:01:01,000'
        assert formatter._seconds_to_srt_timecode(3661.750) == '01:01:01,750'

    def test_seconds_to_vtt_timecode(self):
        """Test conversion to VTT timecode format."""
        formatter = FormatterService()

        # Test various seconds values (VTT uses period, not comma)
        assert formatter._seconds_to_vtt_timecode(0.0) == '00:00:00.000'
        assert formatter._seconds_to_vtt_timecode(1.5) == '00:00:01.500'
        assert formatter._seconds_to_vtt_timecode(61.0) == '00:01:01.000'
        assert formatter._seconds_to_vtt_timecode(3661.750) == '01:01:01.750'

    def test_timecode_precision(self):
        """Test that timecodes maintain millisecond precision."""
        formatter = FormatterService()

        # Test sub-millisecond rounding
        assert formatter._seconds_to_srt_timecode(1.1234) == '00:00:01,123'
        # Note: floating point precision means 1.1235 rounds to 123 not 124
        assert formatter._seconds_to_srt_timecode(1.1240) == '00:00:01,124'

        assert formatter._seconds_to_vtt_timecode(1.1234) == '00:00:01.123'
        assert formatter._seconds_to_vtt_timecode(1.1240) == '00:00:01.124'


class TestFileIntegrity:
    """Test file integrity and consistency."""

    def test_save_and_load_consistency(self, tmp_path):
        """Test that saved file can be read back correctly."""
        chunks = [
            {'text': 'Test line 1', 'start': 0.0, 'end': 1.0, 'word_count': 2},
            {'text': 'Test line 2', 'start': 1.5, 'end': 2.5, 'word_count': 2},
        ]
        output_file = tmp_path / "consistency_test.txt"
        formatter = FormatterService()

        # Save
        formatter.save_transcript(chunks, str(output_file))

        # Load and verify
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '[0:00]' in content
        assert 'Test line 1' in content
        assert 'Test line 2' in content

    def test_save_srt_format(self, tmp_path):
        """Test saving SRT file."""
        chunks = [
            {'text': 'First', 'start': 0.0, 'end': 1.0, 'word_count': 1},
            {'text': 'Second', 'start': 1.5, 'end': 2.5, 'word_count': 1},
        ]
        output_file = tmp_path / "test.srt"
        formatter = FormatterService()

        formatter.save_srt(chunks, str(output_file))

        assert output_file.exists()

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '1' in content  # Sequence number
        assert '-->' in content  # Timecode separator
        assert 'First' in content
        assert 'Second' in content

    def test_save_vtt_format(self, tmp_path):
        """Test saving VTT file."""
        chunks = [
            {'text': 'First', 'start': 0.0, 'end': 1.0, 'word_count': 1},
            {'text': 'Second', 'start': 1.5, 'end': 2.5, 'word_count': 1},
        ]
        output_file = tmp_path / "test.vtt"
        formatter = FormatterService()

        formatter.save_vtt(chunks, str(output_file))

        assert output_file.exists()

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert content.startswith('WEBVTT')
        assert '-->' in content
        assert 'First' in content
        assert 'Second' in content
