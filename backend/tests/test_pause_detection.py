"""
Tests for pause detection and threshold configuration.
Phase 3: Comprehensive pause threshold testing.
"""

import pytest
from app.services.chunking import ChunkingService


class TestPauseDetection:
    """Test pause detection with various thresholds."""

    def test_pause_detection_threshold_0_3(self):
        """Test with 0.3s threshold - aggressive chunking."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.2},
            {'text': 'world', 'start': 0.5, 'end': 0.7},  # 0.3s pause
            {'text': 'today', 'start': 1.0, 'end': 1.2},  # 0.3s pause
        ]
        chunking = ChunkingService(pause_threshold=0.3)
        chunks = chunking.chunk(words)

        # With 0.3s threshold, each 0.3s pause creates new chunk
        assert len(chunks) == 3
        assert chunks[0]['text'] == 'Hello'
        assert chunks[1]['text'] == 'world'
        assert chunks[2]['text'] == 'today'

    def test_pause_detection_threshold_0_5(self):
        """Test with 0.5s threshold - moderate chunking."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.2},
            {'text': 'world', 'start': 0.5, 'end': 0.7},  # 0.3s pause - no chunk
            {'text': 'today', 'start': 1.2, 'end': 1.4},  # 0.5s pause - chunk!
        ]
        chunking = ChunkingService(pause_threshold=0.5)
        chunks = chunking.chunk(words)

        # With 0.5s threshold, only 0.5s+ pauses create chunks
        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Hello world'
        assert chunks[1]['text'] == 'today'

    def test_pause_detection_threshold_0_7(self):
        """Test with 0.7s threshold - default behavior."""
        words = [
            {'text': 'You', 'start': 0.20, 'end': 0.42},
            {'text': 'wake', 'start': 0.43, 'end': 0.70},
            {'text': 'up', 'start': 0.71, 'end': 0.88},
            {'text': 'to', 'start': 0.89, 'end': 0.97},
            {'text': 'an', 'start': 0.98, 'end': 1.07},
            {'text': 'alarm', 'start': 1.08, 'end': 1.44},
            {'text': 'You', 'start': 2.10, 'end': 2.36},  # 0.66s pause - no chunk
            {'text': 'get', 'start': 2.37, 'end': 2.65},
            {'text': 'up', 'start': 2.66, 'end': 2.83},
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # With 0.7s threshold, 0.66s pause doesn't trigger chunk
        assert len(chunks) == 1
        assert len(chunks[0]['words']) == 9

    def test_pause_detection_threshold_1_0(self):
        """Test with 1.0s threshold - conservative chunking."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.2},
            {'text': 'world', 'start': 0.5, 'end': 0.7},   # 0.3s pause - no chunk
            {'text': 'today', 'start': 1.2, 'end': 1.4},   # 0.5s pause - no chunk
            {'text': 'friend', 'start': 2.4, 'end': 2.6},  # 1.0s pause - chunk!
        ]
        chunking = ChunkingService(pause_threshold=1.0)
        chunks = chunking.chunk(words)

        # With 1.0s threshold, only >= 1.0s pauses create chunks
        assert len(chunks) == 2
        assert chunks[0]['text'] == 'Hello world today'
        assert chunks[1]['text'] == 'friend'

    def test_pause_calculation_accuracy(self):
        """Test that pause calculations are accurate."""
        words = [
            {'text': 'word1', 'start': 0.0, 'end': 0.5},
            {'text': 'word2', 'start': 1.2, 'end': 1.7},  # Pause: 1.2 - 0.5 = 0.7s
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # 0.7s pause equals threshold, should create new chunk
        assert len(chunks) == 2

        # Now test with 0.71s threshold (pause is < threshold)
        chunking = ChunkingService(pause_threshold=0.71)
        chunks = chunking.chunk(words)
        assert len(chunks) == 1

    def test_multiple_pauses_exceed_threshold(self):
        """Test speech with multiple pause boundaries."""
        words = [
            {'text': 'First', 'start': 0.0, 'end': 0.3},
            {'text': 'sentence.', 'start': 0.4, 'end': 0.7},
            {'text': 'Second', 'start': 1.5, 'end': 1.8},    # 0.8s pause
            {'text': 'sentence.', 'start': 1.9, 'end': 2.2},
            {'text': 'Third', 'start': 3.1, 'end': 3.4},     # 0.9s pause
            {'text': 'sentence.', 'start': 3.5, 'end': 3.8},
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # Should have 3 chunks due to two pauses >= 0.7s
        assert len(chunks) == 3
        assert 'First sentence' in chunks[0]['text']
        assert 'Second sentence' in chunks[1]['text']
        assert 'Third sentence' in chunks[2]['text']

    def test_fast_speaker_minimal_pauses(self):
        """Test edge case: very fast speaker with minimal pauses."""
        words = [
            {'text': 'The', 'start': 0.0, 'end': 0.1},
            {'text': 'quick', 'start': 0.12, 'end': 0.25},   # 0.02s pause
            {'text': 'brown', 'start': 0.27, 'end': 0.38},   # 0.02s pause
            {'text': 'fox', 'start': 0.40, 'end': 0.50},     # 0.02s pause
            {'text': 'jumps', 'start': 0.52, 'end': 0.65},   # 0.02s pause
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # No pauses >= 0.7s, should be one chunk
        assert len(chunks) == 1
        assert len(chunks[0]['words']) == 5

    def test_slow_speaker_long_pauses(self):
        """Test edge case: very slow speaker with many long pauses."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'there', 'start': 2.0, 'end': 2.5},     # 1.5s pause
            {'text': 'my', 'start': 4.0, 'end': 4.3},        # 1.5s pause
            {'text': 'friend', 'start': 5.8, 'end': 6.3},    # 1.5s pause
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # All pauses > 0.7s, should have 4 chunks
        assert len(chunks) == 4
        assert chunks[0]['text'] == 'Hello'
        assert chunks[1]['text'] == 'there'
        assert chunks[2]['text'] == 'my'
        assert chunks[3]['text'] == 'friend'

    def test_uneven_speech_pattern(self):
        """Test realistic speech with varied pause patterns."""
        words = [
            {'text': 'I', 'start': 0.0, 'end': 0.1},
            {'text': 'think', 'start': 0.12, 'end': 0.35},   # 0.02s - no pause
            {'text': 'therefore', 'start': 0.37, 'end': 0.65},  # 0.02s - no pause
            {'text': 'I', 'start': 0.67, 'end': 0.75},       # 0.02s - no pause
            {'text': 'am.', 'start': 0.77, 'end': 0.95},     # 0.02s - no pause
            {'text': 'The', 'start': 1.8, 'end': 1.95},      # 0.85s pause - CHUNK!
            {'text': 'answer', 'start': 1.97, 'end': 2.25},  # 0.02s - no pause
            {'text': 'is', 'start': 2.27, 'end': 2.40},      # 0.02s - no pause
            {'text': 'yes.', 'start': 2.42, 'end': 2.60},    # 0.02s - no pause
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # Should split at 0.85s pause
        assert len(chunks) == 2
        assert chunks[0]['word_count'] == 5
        assert chunks[1]['word_count'] == 4


class TestThresholdValidation:
    """Test threshold validation and error handling."""

    def test_threshold_too_low(self):
        """Test threshold below minimum (0.1s)."""
        with pytest.raises(ValueError, match="between 0.1 and 3.0"):
            chunking = ChunkingService(pause_threshold=0.05)
            chunking.set_pause_threshold(0.05)

    def test_threshold_too_high(self):
        """Test threshold above maximum (3.0s)."""
        with pytest.raises(ValueError, match="between 0.1 and 3.0"):
            chunking = ChunkingService()
            chunking.set_pause_threshold(3.5)

    def test_threshold_at_boundaries(self):
        """Test threshold at valid boundaries."""
        # Minimum valid
        chunking = ChunkingService(pause_threshold=0.1)
        assert chunking.pause_threshold == 0.1

        # Maximum valid
        chunking.set_pause_threshold(3.0)
        assert chunking.pause_threshold == 3.0

    def test_threshold_setter(self):
        """Test threshold can be updated after initialization."""
        chunking = ChunkingService(pause_threshold=0.7)
        assert chunking.pause_threshold == 0.7

        chunking.set_pause_threshold(0.5)
        assert chunking.pause_threshold == 0.5

        # Verify it affects chunking
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.2},
            {'text': 'world', 'start': 0.5, 'end': 0.7},  # 0.3s pause
        ]
        chunks = chunking.chunk(words)
        assert len(chunks) == 1  # 0.3s < 0.5s threshold, should be 1 chunk

        chunking.set_pause_threshold(0.2)
        chunks = chunking.chunk(words)
        assert len(chunks) == 2  # 0.3s >= 0.2s threshold, should split into 2 chunks


class TestPauseDetectionEdgeCases:
    """Test edge cases in pause detection."""

    def test_zero_pause(self):
        """Test words with no pause (consecutive timing)."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'world', 'start': 0.5, 'end': 1.0},  # 0s pause
        ]
        chunking = ChunkingService(pause_threshold=0.1)
        chunks = chunking.chunk(words)

        assert len(chunks) == 1
        assert chunks[0]['text'] == 'Hello world'

    def test_overlapping_words(self):
        """Test words with overlapping timestamps (unusual but possible)."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'world', 'start': 0.3, 'end': 0.8},  # Negative pause!
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        # Negative pause shouldn't trigger chunk
        assert len(chunks) == 1

    def test_very_small_pause(self):
        """Test sub-millisecond pauses."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
            {'text': 'world', 'start': 0.5001, 'end': 1.0},  # 0.0001s pause
        ]
        chunking = ChunkingService(pause_threshold=0.1)
        chunks = chunking.chunk(words)

        assert len(chunks) == 1
        assert chunks[0]['text'] == 'Hello world'

    def test_single_word(self):
        """Test with single word."""
        words = [
            {'text': 'Hello', 'start': 0.0, 'end': 0.5},
        ]
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        assert len(chunks) == 1
        assert chunks[0]['text'] == 'Hello'

    def test_empty_word_list(self):
        """Test with empty word list."""
        words = []
        chunking = ChunkingService(pause_threshold=0.7)
        chunks = chunking.chunk(words)

        assert len(chunks) == 0
