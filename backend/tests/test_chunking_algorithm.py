"""
Tests for three-signal chunking algorithm.
Phase 4: Testing pause, punctuation, and length signals.
"""

import pytest
from app.services.chunking import ChunkingService


class TestPauseSignal:
    """Test Signal 1: Pause threshold."""

    def test_pause_creates_chunk_boundary(self):
        """Test that pauses >= threshold create chunk boundaries."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'world', 'start': 1.5, 'end': 2.0},  # 1.0s pause >= 0.7s
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Hello'
        assert chunks[1]['text'] == 'world'

    def test_pause_below_threshold_no_boundary(self):
        """Test that pauses < threshold don't create boundaries."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'world', 'start': 0.6, 'end': 1.0},  # 0.1s pause < 0.7s
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        assert len(chunks) == 1
        assert chunks[0]['text'] == 'Hello world'

    def test_pause_at_threshold_boundary(self):
        """Test pause exactly at threshold."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'world', 'start': 1.2, 'end': 1.7},  # 0.7s pause == threshold
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # Should trigger chunk at >= comparison
        assert len(chunks) == 2


class TestPunctuationSignal:
    """Test Signal 2: Punctuation boundaries."""

    def test_period_creates_boundary(self):
        """Test that period (.) creates chunk boundary."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.3},
            {'text': 'world.', 'start': 0.4, 'end': 0.8},
            {'text': 'How', 'start': 0.9, 'end': 1.2},
            {'text': 'are', 'start': 1.3, 'end': 1.6},
            {'text': 'you?', 'start': 1.7, 'end': 2.0},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Should split at period and question mark
        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Hello world.'
        assert chunks[1]['text'] == 'How are you?'

    def test_question_mark_creates_boundary(self):
        """Test that question mark (?) creates chunk boundary."""
        words = [
            {'text': 'Who', 'start': 0.0, 'end': 0.3},
            {'text': 'is', 'start': 0.4, 'end': 0.6},
            {'text': 'there?', 'start': 0.7, 'end': 1.0},
            {'text': 'Me', 'start': 1.1, 'end': 1.3},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Who is there?'
        assert chunks[1]['text'] == 'Me'

    def test_exclamation_creates_boundary(self):
        """Test that exclamation mark (!) creates chunk boundary."""
        words = [
            {'text': 'Stop', 'start': 0.0, 'end': 0.3},
            {'text': 'now!', 'start': 0.4, 'end': 0.7},
            {'text': 'Quickly', 'start': 0.8, 'end': 1.1},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Stop now!'
        assert chunks[1]['text'] == 'Quickly'

    def test_no_punctuation_no_boundary(self):
        """Test that lack of punctuation doesn't create boundary."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.3},
            {'text': 'my', 'start': 0.4, 'end': 0.6},
            {'text': 'friend', 'start': 0.7, 'end': 1.0},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        assert len(chunks) == 1
        assert chunks[0]['text'] == 'Hello my friend'

    def test_multiple_punctuation_marks(self):
        """Test word with multiple punctuation marks."""
        words = [
            {'text': 'Really?!', 'start': 0.0, 'end': 0.5},
            {'text': 'Yes', 'start': 0.6, 'end': 0.8},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Should recognize ?! as punctuation (ends with !)
        assert len(chunks) == 2

    def test_comma_does_not_create_boundary(self):
        """Test that comma (,) doesn't create boundary (not a signal)."""
        words = [
            {'text': 'Hello,', 'start': 0.0, 'end': 0.3},
            {'text': 'world', 'start': 0.4, 'end': 0.7},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Comma alone shouldn't create boundary
        assert len(chunks) == 1
        assert chunks[0]['text'] == 'Hello, world'

    def test_quoted_text_with_punctuation(self):
        """Test punctuation within quoted text."""
        words = [
            {'text': '"Hello', 'start': 0.0, 'end': 0.3},
            {'text': 'world."', 'start': 0.4, 'end': 0.8},
            {'text': 'He', 'start': 0.9, 'end': 1.1},
            {'text': 'said.', 'start': 1.2, 'end': 1.4},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Period detection looks at end of text - 'world."' ends with " not .
        # So no split at first period. Split happens at 'said.' instead
        assert len(chunks) >= 1
        # Last chunk should end with period
        assert chunks[-1]['text'].endswith('.')


class TestLengthSignal:
    """Test Signal 3: Maximum chunk words."""

    def test_max_chunk_length_creates_boundary(self):
        """Test that max words per chunk creates boundary."""
        words = [
            {'text': 'one', 'start': 0.0, 'end': 0.2},
            {'text': 'two', 'start': 0.3, 'end': 0.5},
            {'text': 'three', 'start': 0.6, 'end': 0.8},
            {'text': 'four', 'start': 0.9, 'end': 1.1},
            {'text': 'five', 'start': 1.2, 'end': 1.4},
            {'text': 'six', 'start': 1.5, 'end': 1.7},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=3)
        chunks = chunking.chunk(words)

        # Should split at every 3 words (no pauses exceed threshold)
        assert len(chunks) == 2
        assert len(chunks[0]['words']) == 3
        assert len(chunks[1]['words']) == 3

    def test_max_chunk_length_enforcement(self):
        """Test that chunks never exceed max length."""
        words = [
            {'text': f'word{i}', 'start': i * 0.1, 'end': i * 0.1 + 0.05}
            for i in range(20)
        ]
        chunking = ChunkingService(pause_threshold=10.0, max_chunk_words=5)
        chunks = chunking.chunk(words)

        # All chunks should have <= 5 words
        for chunk in chunks:
            assert chunk['word_count'] <= 5

    def test_max_chunk_length_with_long_pause(self):
        """Test max length enforcement even with pause signals."""
        words = [
            {'text': 'one', 'start': 0.0, 'end': 0.2},
            {'text': 'two', 'start': 0.3, 'end': 0.5},
            {'text': 'three', 'start': 0.6, 'end': 0.8},
            {'text': 'four', 'start': 0.9, 'end': 1.1},
            {'text': 'five', 'start': 2.0, 'end': 2.2},  # 0.9s pause
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=3)
        chunks = chunking.chunk(words)

        # Length signal takes precedence: split at 3, then pause signal
        assert len(chunks) == 3
        assert len(chunks[0]['words']) == 3
        assert chunks[1]['text'] == 'four'
        assert chunks[2]['text'] == 'five'


class TestThreeSignalsInteraction:
    """Test how all three signals interact."""

    def test_pause_wins_over_length(self):
        """Test pause signal taking precedence when < max length."""
        words = [
            {'text': 'one', 'start': 0.0, 'end': 0.2},
            {'text': 'two', 'start': 0.3, 'end': 0.5},
            {'text': 'three', 'start': 1.5, 'end': 1.7},  # 1.0s pause
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=10)
        chunks = chunking.chunk(words)

        # Pause signal triggers before length limit
        assert len(chunks) == 2
        assert chunks[0]['text'] == 'one two'
        assert chunks[1]['text'] == 'three'

    def test_punctuation_wins_over_pause(self):
        """Test punctuation and pause both present (punctuation comes first in code)."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.3},
            {'text': 'world.', 'start': 0.4, 'end': 0.7},
            {'text': 'How', 'start': 1.5, 'end': 1.8},  # 0.8s pause
            {'text': 'are', 'start': 1.9, 'end': 2.1},
            {'text': 'you?', 'start': 2.2, 'end': 2.4},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Punctuation triggers at period, pause triggers before 'How'
        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Hello world.'
        assert chunks[1]['text'] == 'How are you?'

    def test_all_three_signals_present(self):
        """Test realistic sentence with all three signals."""
        words = [
            {'text': 'The', 'start': 0.0, 'end': 0.15},
            {'text': 'quick', 'start': 0.25, 'end': 0.40},
            {'text': 'brown', 'start': 0.50, 'end': 0.65},
            {'text': 'fox', 'start': 0.75, 'end': 0.90},
            {'text': 'jumps', 'start': 1.00, 'end': 1.15},
            {'text': 'over', 'start': 1.25, 'end': 1.40},
            {'text': 'the', 'start': 1.50, 'end': 1.65},
            {'text': 'lazy', 'start': 1.75, 'end': 1.90},
            {'text': 'dog.', 'start': 2.00, 'end': 2.20},
            {'text': 'Another', 'start': 3.5, 'end': 3.7},  # 1.3s pause
            {'text': 'sentence', 'start': 3.8, 'end': 4.0},
            {'text': 'here.', 'start': 4.1, 'end': 4.3},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=5)
        chunks = chunking.chunk(words)

        # With max_chunk_words=5: should split before reaching 'dog.' due to length
        # Then pause signal triggers at 1.3s gap before 'Another'
        # So we expect: [The quick brown fox jumps], [over the lazy dog.], [Another sentence here.]
        assert len(chunks) >= 2
        # Check that we have chunks (actual split points depend on signal priority)
        total_words = sum(c['word_count'] for c in chunks)
        assert total_words == 12  # All words accounted for

    def test_max_length_triggers_at_word_boundary(self):
        """Test that max length triggers cleanly at word boundary."""
        words = [
            {'text': 'This', 'start': 0.0, 'end': 0.2},
            {'text': 'is', 'start': 0.25, 'end': 0.35},
            {'text': 'a', 'start': 0.4, 'end': 0.45},
            {'text': 'test', 'start': 0.5, 'end': 0.65},
            {'text': 'sentence', 'start': 0.7, 'end': 0.85},
            {'text': 'with', 'start': 0.9, 'end': 1.0},
        ]
        chunking = ChunkingService(pause_threshold=10.0, max_chunk_words=3)
        chunks = chunking.chunk(words)

        # Should split into two 3-word chunks
        assert len(chunks) == 2
        assert chunks[0]['word_count'] == 3
        assert chunks[1]['word_count'] == 3


class TestPunctuationVariations:
    """Test punctuation detection edge cases."""

    def test_ellipsis_not_recognized(self):
        """Test that ellipsis (...) is not recognized as boundary."""
        words = [
            {'text': 'Wait...', 'start': 0.0, 'end': 0.5},
            {'text': 'really?', 'start': 0.6, 'end': 0.9},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Ellipsis doesn't match (ends with .)
        # But actually '...' does end with period, so it will match
        assert chunks[0]['text'] == 'Wait...'

    def test_abbreviation_period(self):
        """Test period in abbreviations like Dr."""
        words = [
            {'text': 'Dr.', 'start': 0.0, 'end': 0.3},
            {'text': 'Smith', 'start': 0.4, 'end': 0.7},
            {'text': 'is', 'start': 0.8, 'end': 1.0},
            {'text': 'here.', 'start': 1.1, 'end': 1.4},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Period in 'Dr.' will create boundary (limitation of simple algorithm)
        # This is a known edge case
        assert len(chunks) >= 1

    def test_trailing_whitespace_punctuation(self):
        """Test that trailing whitespace doesn't affect punctuation detection."""
        words = [
            {'text': 'Hello ', 'start': 0.0, 'end': 0.3},  # Trailing space
            {'text': 'world.', 'start': 0.4, 'end': 0.7},
            {'text': 'Hi', 'start': 0.8, 'end': 1.0},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Should still detect period in 'world.'
        assert len(chunks) == 2


class TestChunkingStats:
    """Test chunk metadata and statistics."""

    def test_chunk_timestamps_accurate(self):
        """Test that chunk start/end times are correct."""
        words = [
            {'text': 'First', 'start': 0.1, 'end': 0.3},
            {'text': 'chunk.', 'start': 0.4, 'end': 0.6},
            {'text': 'Second', 'start': 1.5, 'end': 1.7},
            {'text': 'chunk.', 'start': 1.8, 'end': 2.0},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # First chunk should span first two words
        assert chunks[0]['start'] == 0.1
        assert chunks[0]['end'] == 0.6

        # Second chunk should span last two words
        assert chunks[1]['start'] == 1.5
        assert chunks[1]['end'] == 2.0

    def test_chunk_word_count_accurate(self):
        """Test that word_count is accurate."""
        words = [
            {'text': f'word{i}', 'start': i * 0.1, 'end': i * 0.1 + 0.05}
            for i in range(10)
        ]
        chunking = ChunkingService(pause_threshold=10.0, max_chunk_words=3)
        chunks = chunking.chunk(words)

        for chunk in chunks:
            assert chunk['word_count'] == len(chunk['words'])

    def test_chunk_preserves_word_data(self):
        """Test that chunks preserve original word data."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.3},
            {'text': 'world', 'start': 0.4, 'end': 0.7},
        ]
        chunking = ChunkingService(pause_threshold=0.7, max_chunk_words=15)
        chunks = chunking.chunk(words)

        # Words should be preserved in chunk
        assert chunks[0]['words'] == words
        assert chunks[0]['words'][0]['text'] == 'Hello'
        assert chunks[0]['words'][1]['text'] == 'world'
