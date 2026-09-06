"""
Main entry point for the audio transcription backend.
Phase 1: Local transcription engine
Phase 2: Word-level timestamps with verbose output and format options
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.audio import AudioProcessor
from app.services.transcription import TranscriptionService
from app.services.chunking import ChunkingService
from app.services.formatter import FormatterService


def print_word_timestamps(words: list, pause_threshold: float = 0.7) -> None:
    """
    Display all word timestamps with pause calculations.

    Args:
        words: List of words with start/end timestamps.
        pause_threshold: Pause duration in seconds to highlight.
    """
    print("\nWord-Level Timestamps:")
    print("───────────────────────────────────────")

    for i, word in enumerate(words):
        duration = word['end'] - word['start']
        word_text = word['text'][:15].ljust(15)

        # Check for pause before this word
        if i > 0:
            pause = word['start'] - words[i-1]['end']
            if pause >= pause_threshold:
                prev_word = words[i-1]
                pause_text = f"[pause: {prev_word['end']:.2f} - {word['start']:.2f}   ({pause:.2f}s) ← EXCEEDS THRESHOLD!]"
                print(pause_text)

        print(f"{word_text} {word['start']:.2f} - {word['end']:.2f}   ({duration:.2f}s)")


def save_as_json(words: list, chunks: list, output_path: str) -> None:
    """
    Save transcript as JSON with detailed timing data.

    Args:
        words: List of words with timestamps.
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

    print(f"\n✓ JSON transcript saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Transcribe audio files with word-level timestamps'
    )
    parser.add_argument('audio_file', help='Path to audio file')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Display word-level timestamps with pause calculations'
    )
    parser.add_argument(
        '--output-format',
        choices=['txt', 'json'],
        default='txt',
        help='Output format for transcript (default: txt)'
    )
    parser.add_argument(
        '--pause-threshold',
        type=float,
        default=0.7,
        help='Pause duration in seconds to detect sentence breaks (default: 0.7)'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default=None,
        help='Custom output filename (default: transcript.txt or transcript.json)'
    )

    args = parser.parse_args()
    audio_file = args.audio_file

    if not os.path.exists(audio_file):
        print(f"Error: File not found: {audio_file}")
        sys.exit(1)

    print(f"Processing: {audio_file}")
    print("-" * 50)

    try:
        # Step 1: Process audio
        print("Step 1: Processing audio file...")
        audio_processor = AudioProcessor()
        wav_file = audio_processor.process(audio_file)
        print(f"✓ Audio processed: {wav_file}")

        # Step 2: Transcribe
        print("\nStep 2: Transcribing audio...")
        transcription_service = TranscriptionService()
        result = transcription_service.transcribe(wav_file)
        print(f"✓ Transcription complete")
        print(f"  Language: {result['language']}")
        print(f"  Words: {len(result['words'])}")

        # Step 3: Display verbose timestamps if requested
        if args.verbose:
            print_word_timestamps(result['words'], args.pause_threshold)

        # Step 4: Chunk the words
        print("\nStep 3: Chunking transcript...")
        chunking_service = ChunkingService(pause_threshold=args.pause_threshold)
        chunks = chunking_service.chunk(result['words'])
        print(f"✓ Chunking complete: {len(chunks)} chunks")

        # Step 5: Save output in requested format
        print("\nStep 4: Saving transcript...")

        if args.output_format == 'json':
            output_file = args.output_file or 'transcript.json'
            save_as_json(result['words'], chunks, output_file)
        else:
            output_file = args.output_file or 'transcript.txt'
            formatter = FormatterService()
            formatter.save_transcript(chunks, output_file)
            print(f"✓ Text transcript saved: {output_file}")

            # Display stats
            stats = formatter.get_transcript_stats(chunks)
            print(f"\nTranscript Statistics:")
            print(f"  Chunks: {stats['chunk_count']}")
            print(f"  Words: {stats['word_count']}")
            print(f"  Duration: {stats['duration']:.2f}s")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
