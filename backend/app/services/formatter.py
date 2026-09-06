"""
Output formatter service.
Converts chunks to the final transcript format (text and JSON).
"""

import json
from typing import List, Dict, Any
from app.utils.timestamps import seconds_to_timestamp


class FormatterService:
    """Format chunks into the final transcript output."""

    def __init__(self, precision: str = 'integer'):
        """
        Initialize the formatter.

        Args:
            precision: 'integer' for [M:SS], 'decimal' for [M:SS.SS].
        """
        self.precision = precision

    def format_transcript(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Convert chunks to formatted transcript text.

        Args:
            chunks: List of chunks with text, start, end timestamps.

        Returns:
            Formatted transcript as plain text.
        """
        lines = []
        for chunk in chunks:
            timestamp = seconds_to_timestamp(chunk['start'], self.precision)
            text = chunk['text'].strip()
            line = f"{timestamp} {text}"
            lines.append(line)

        return '\n'.join(lines)

    def save_transcript(
        self,
        chunks: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        Save transcript to file.

        Args:
            chunks: List of chunks with text, start, end timestamps.
            output_path: Path to save the transcript file.
        """
        content = self.format_transcript(chunks)

        # Write as UTF-8 plain text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_transcript_json(
        self,
        words: List[Dict[str, Any]],
        chunks: List[Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        Save transcript with full timing data as JSON.

        Args:
            words: List of words with start/end timestamps.
            chunks: List of chunks from the chunking service.
            output_path: Path to save the JSON file.
        """
        data = {
            'words': words,
            'chunks': chunks,
            'metadata': {
                'total_words': len(words),
                'total_chunks': len(chunks),
                'total_duration': words[-1]['end'] if words else 0,
                'chunk_word_count': sum(c['word_count'] for c in chunks),
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_transcript_stats(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the transcript.

        Args:
            chunks: List of chunks with text, start, end timestamps.

        Returns:
            Dictionary with word count, duration, etc.
        """
        total_words = sum(chunk['word_count'] for chunk in chunks)
        total_duration = chunks[-1]['end'] if chunks else 0

        return {
            'chunk_count': len(chunks),
            'word_count': total_words,
            'duration': total_duration,
        }
