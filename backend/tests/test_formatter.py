"""
Tests for formatter service.
"""

from app.services.formatter import FormatterService


def test_format_transcript():
    """Test formatting chunks into transcript."""
    chunks = [
        {
            'text': 'You wake up to an alarm.',
            'start': 0.0,
            'end': 1.5,
            'word_count': 5,
        },
        {
            'text': 'You check the time.',
            'start': 1.6,
            'end': 3.0,
            'word_count': 4,
        },
    ]

    service = FormatterService()
    transcript = service.format_transcript(chunks)

    lines = transcript.split('\n')
    assert len(lines) == 2
    assert lines[0].startswith('[0:00]')
    assert 'You wake up to an alarm.' in lines[0]
    assert lines[1].startswith('[0:01]')
    assert 'You check the time.' in lines[1]


def test_get_transcript_stats():
    """Test transcript statistics."""
    chunks = [
        {
            'text': 'Hello world',
            'start': 0.0,
            'end': 1.0,
            'word_count': 2,
        },
        {
            'text': 'This is test',
            'start': 2.0,
            'end': 3.5,
            'word_count': 3,
        },
    ]

    service = FormatterService()
    stats = service.get_transcript_stats(chunks)

    assert stats['chunk_count'] == 2
    assert stats['word_count'] == 5
    assert stats['duration'] == 3.5
