"""
Tests for chunking service.
"""

from app.services.chunking import ChunkingService


def test_chunking_basic():
    """Test basic chunking with pause threshold."""
    words = [
        {'text': 'Hello', 'start': 0.0, 'end': 0.5},
        {'text': 'world', 'start': 0.6, 'end': 1.0},
        {'text': 'This', 'start': 2.0, 'end': 2.4},  # 1.0 second pause
        {'text': 'is', 'start': 2.5, 'end': 2.7},
        {'text': 'test', 'start': 2.8, 'end': 3.2},
    ]

    service = ChunkingService(pause_threshold=0.7)
    chunks = service.chunk(words)

    assert len(chunks) == 2
    assert chunks[0]['text'] == 'Hello world'
    assert chunks[1]['text'] == 'This is test'


def test_chunking_punctuation():
    """Test chunking with punctuation boundaries."""
    words = [
        {'text': 'Hello.', 'start': 0.0, 'end': 0.5},
        {'text': 'World', 'start': 0.6, 'end': 1.0},
    ]

    service = ChunkingService(pause_threshold=0.7)
    chunks = service.chunk(words)

    assert len(chunks) == 2
    assert chunks[0]['text'] == 'Hello.'
    assert chunks[1]['text'] == 'World'


def test_chunking_max_length():
    """Test chunking with maximum word length."""
    words = [
        {'text': f'word{i}', 'start': float(i), 'end': float(i) + 0.4}
        for i in range(20)
    ]

    service = ChunkingService(max_chunk_words=5)
    chunks = service.chunk(words)

    assert len(chunks) == 4
    assert all(chunk['word_count'] <= 5 for chunk in chunks)


def test_chunking_empty():
    """Test chunking with empty word list."""
    service = ChunkingService()
    chunks = service.chunk([])
    assert len(chunks) == 0
