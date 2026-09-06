# 🚀 Getting Started with Phase 2

**Current Status:** Phase 1 Complete ✓  
**Next Action:** Start Phase 2 - Word-Level Timestamps  
**Estimated Time:** 2-4 hours

## What You Have Now

Phase 1 provides a complete, working local transcription engine with:
- ✅ Audio processing and validation
- ✅ Whisper transcription with word-level timestamps
- ✅ Pause-aware chunking algorithm
- ✅ Output formatting
- ✅ Unit tests
- ✅ CLI entry point

## Phase 2: Word-Level Timestamps

### Goal
Make word-level timing data visible for debugging and validation.

### What to Implement

**1. Add `--verbose` flag to CLI**
```bash
python transcribe.py audio.mp3 --verbose
```

Should display:
```
Word-Level Timestamps:
───────────────────────────────────────
You              0.20 - 0.42   (0.22s)
wake             0.43 - 0.70   (0.27s)
up               0.71 - 0.88   (0.17s)
to               0.89 - 0.97   (0.08s)
an               0.98 - 1.07   (0.09s)
alarm            1.08 - 1.44   (0.36s)
[pause:          1.44 - 2.10   (0.66s) ← EXCEEDS THRESHOLD!]
You              2.10 - 2.36   (0.26s)
```

**2. Add `--output-format` option**
```bash
python transcribe.py audio.mp3 --output-format json
```

Output: `transcript.json` with full word timing data

**3. Validate Pause Calculations**
- Compare printed pause values against manual audio inspection
- Verify timestamps align with actual audio playback
- Test with different speakers and audio speeds

### Code Changes Needed

**Modify `backend/transcribe.py`:**
```python
import argparse

# Add argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('audio_file')
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--output-format', choices=['txt', 'json'], default='txt')
args = parser.parse_args()

# If verbose, display word timestamps before chunking
if args.verbose:
    print_word_timestamps(result['words'])

# Handle output format
if args.output_format == 'json':
    save_as_json(chunks, 'transcript.json')
else:
    save_as_txt(chunks, 'transcript.txt')
```

**Add helper functions:**
```python
def print_word_timestamps(words):
    """Display all word timestamps with pause calculations."""
    for i, word in enumerate(words):
        duration = word['end'] - word['start']
        
        if i > 0:
            pause = word['start'] - words[i-1]['end']
            if pause >= 0.7:  # threshold
                print(f"[pause: {words[i-1]['end']:.2f} - {word['start']:.2f}   ({pause:.2f}s) ← EXCEEDS THRESHOLD]")
        
        print(f"{word['text']:15} {word['start']:.2f} - {word['end']:.2f}   ({duration:.2f}s)")

def save_as_json(chunks, filename):
    """Save transcript as JSON with detailed timing."""
    import json
    data = {
        'chunks': chunks,
        'metadata': {
            'total_chunks': len(chunks),
            'total_words': sum(c['word_count'] for c in chunks),
            'duration': chunks[-1]['end'] if chunks else 0,
        }
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### Testing Phase 2

**1. Create test audio** (if you don't have one)
- Use an audio editor to create a simple test file
- Known content: "Hello. [1 second pause] World."
- Save as `test_audio.mp3`

**2. Run with verbose flag**
```bash
python transcribe.py test_audio.mp3 --verbose
```

**3. Spot-check against the audio**
- Open the audio file in an editor (Audacity is free)
- Manually verify the timestamps match
- Confirm pauses are calculated correctly

**4. Test JSON output**
```bash
python transcribe.py test_audio.mp3 --output-format json
cat transcript.json
```

**5. Run existing tests**
```bash
pytest tests/ -v
```

### Deliverables for Phase 2

- [ ] `--verbose` flag implemented
- [ ] Word timestamps displayed with pause calculations
- [ ] `--output-format json` working
- [ ] Manual audio verification completed
- [ ] Tests passing
- [ ] Documentation updated

### Success Criteria

✅ Word timestamps visible and accurate
✅ Pause calculations match manual inspection
✅ JSON output contains full timing data
✅ All tests still passing
✅ Ready for Phase 3 (configurable thresholds)

## Files to Modify

**`backend/transcribe.py`**
- Add argparse
- Add `--verbose` flag
- Add `--output-format` option
- Add print and JSON functions

**Optional: `backend/app/services/formatter.py`**
- Add JSON export capability

## Time Estimate

- **Implementation:** 1-2 hours
- **Testing & Validation:** 1-2 hours
- **Total:** 2-4 hours

## Tips

1. **Start Simple:** Get `--verbose` working first
2. **Test with Small Audio:** Use a short (< 30 seconds) test file
3. **Verify Manually:** Open the audio in Audacity and spot-check timestamps
4. **Use Print Debugging:** Add prints at key points to understand flow
5. **Keep Tests Green:** Run `pytest` frequently as you make changes

## Common Issues & Fixes

**Issue:** Timestamps seem off
- ✅ Solution: Open audio in Audacity and manually check
- ✅ Solution: Compare with known speaker

**Issue:** Pauses not detected correctly
- ✅ Solution: Display verbose output and inspect pause calculations
- ✅ Solution: This is why Phase 3 makes threshold configurable

**Issue:** JSON output missing data
- ✅ Solution: Ensure formatter exports full word list with timestamps

## After Phase 2

Once word timestamps are working and validated, you're ready for:

**Phase 3:** Make pause threshold configurable
```bash
python transcribe.py audio.mp3 --pause-threshold 0.5
```

This lets you test different thresholds and find the optimal default.

---

## Command Reference for Phase 2

```bash
# Basic transcription (Phase 1)
python transcribe.py audio.mp3

# With verbose timestamps (Phase 2 - NEW)
python transcribe.py audio.mp3 --verbose

# Export as JSON (Phase 2 - NEW)
python transcribe.py audio.mp3 --output-format json

# Coming in Phase 3: Configurable threshold
# python transcribe.py audio.mp3 --pause-threshold 0.5
```

---

**Ready to start?** Begin by modifying `backend/transcribe.py` to add argument parsing and the `--verbose` flag.
