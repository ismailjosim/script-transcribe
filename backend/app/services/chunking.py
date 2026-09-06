"""
Chunking service.
Groups words into natural chunks based on pause detection, punctuation, and length.
"""

from typing import List, Dict, Any


class ChunkingService:
    """Group words into chunks based on pauses, punctuation, and length."""

    def __init__(
        self,
        pause_threshold: float = 0.7,
        max_chunk_words: int = 15,
    ):
        """
        Initialize the chunking service.

        Args:
            pause_threshold: Pause duration in seconds to start new chunk.
            max_chunk_words: Maximum words per chunk.
        """
        self.pause_threshold = pause_threshold
        self.max_chunk_words = max_chunk_words

    def chunk(self, words: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group words into chunks based on pauses, punctuation, and length.

        Args:
            words: List of words with text, start, end timestamps.

        Returns:
            List of chunks with text, start, end, and words count.
        """
        if not words:
            return []

        chunks = []
        current_chunk = []

        for i, word in enumerate(words):
            # Start first chunk
            if not current_chunk:
                current_chunk.append(word)
                continue

            previous_word = words[i - 1]
            pause_duration = word['start'] - previous_word['end']

            # Check for signals to create new chunk
            should_break = False
            break_reason = None

            # Signal 1: Pause threshold
            if pause_duration >= self.pause_threshold:
                should_break = True
                break_reason = 'pause'

            # Signal 2: Punctuation boundary (., ?, !)
            elif previous_word['text'].rstrip().endswith(('.', '?', '!')):
                should_break = True
                break_reason = 'punctuation'

            # Signal 3: Maximum chunk length
            elif len(current_chunk) >= self.max_chunk_words:
                should_break = True
                break_reason = 'length'

            if should_break:
                # Finish current chunk
                chunks.append(self._create_chunk(current_chunk))
                current_chunk = [word]
            else:
                # Add word to current chunk
                current_chunk.append(word)

        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk))

        return chunks

    @staticmethod
    def _create_chunk(words: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a chunk from a list of words."""
        text = ' '.join(w['text'] for w in words)
        return {
            'text': text,
            'start': words[0]['start'],
            'end': words[-1]['end'],
            'word_count': len(words),
            'words': words,
        }

    def set_pause_threshold(self, threshold: float) -> None:
        """Update the pause threshold."""
        if not 0.1 <= threshold <= 3.0:
            raise ValueError("Pause threshold must be between 0.1 and 3.0 seconds")
        self.pause_threshold = threshold

    def set_max_chunk_words(self, max_words: int) -> None:
        """Update the maximum words per chunk."""
        if not 5 <= max_words <= 50:
            raise ValueError("Max chunk words must be between 5 and 50")
        self.max_chunk_words = max_words
