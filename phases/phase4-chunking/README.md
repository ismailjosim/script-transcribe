# Phase 4: Chunking Algorithm

## Objective

Implement and refine the three-signal chunking algorithm.

## Tasks

### 1. Core Signals

- [x] Signal 1: Pause threshold
- [x] Signal 2: Punctuation boundaries (., ?, !)
- [x] Signal 3: Maximum chunk length

### 2. Testing

- [ ] Test with various audio samples
- [ ] Validate punctuation detection
- [ ] Test max length enforcement

### 3. Optimization

- [ ] Fine-tune pause threshold default
- [ ] Adjust max chunk words
- [ ] Handle edge cases (commas, quotes, etc.)

## Algorithm

```
for each word:
    if current chunk is empty:
        add word
        continue

    pause = current_word.start - previous_word.end
    punctuation_break = previous_word ends with ".", "?", "!"
    too_long = current_chunk contains max_words

    if pause >= pause_threshold:
        finish current chunk
        start new chunk
    elif punctuation_break:
        finish current chunk
        start new chunk
    elif too_long:
        finish current chunk
        start new chunk
    else:
        add word to current chunk
```

## Success Criteria

- Three signals working together
- Produces natural-reading chunks
- Handles all punctuation cases
- Edge cases validated
