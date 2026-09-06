# Phase 2: Word-Level Timestamps

## Objective
Expose word-level timestamp data for debugging and validation.

## Tasks

### 1. Debug Output Format
- [ ] Extend `transcribe.py` to display all word timestamps
- [ ] Add `--verbose` flag to show detailed timing info
- [ ] Create visualization of word timing in terminal

### 2. Timestamp Validation
- [ ] Compare pause calculations against manual inspection
- [ ] Verify timestamps align with audio playback
- [ ] Test with different audio speeds and accents

### 3. Export Format
- [ ] Add `--output-format json` option
- [ ] Generate JSON with full word timing data
- [ ] Create sample output file

## Example Output
```
Word-Level Timestamps:
───────────────────────────────────────
You          0.20 - 0.42   (0.22s)
wake         0.43 - 0.70   (0.27s)
up           0.71 - 0.88   (0.17s)
to           0.89 - 0.97   (0.08s)
an           0.98 - 1.07   (0.09s)
alarm        1.08 - 1.44   (0.36s)
[pause:      1.44 - 2.10   (0.66s) ← exceeds threshold!]
You          2.10 - 2.36   (0.26s)
```

## Dependencies
- Phase 1 (✓ complete)

## Success Criteria
- Word timestamps displayed accurately
- Pause durations calculated correctly
- Manual audio spot-check validates timing
