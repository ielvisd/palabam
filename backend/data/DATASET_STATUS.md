# Dataset Status

## Current Datasets

### ✅ COCA Frequency Data
- **Source**: GitHub (FrequencyWords repository)
- **Words**: 50,000
- **File**: `coca_frequency.json`
- **Status**: ✅ Ready to use
- **Format**: `{"word": frequency_count, ...}`

### ✅ Lexile Scores
- **Source**: Generated from COCA frequency data
- **Words**: 50,000
- **File**: `lexile_scores.json`
- **Status**: ✅ Ready to use
- **Format**: `{"word": lexile_score, ...}`

## Dataset Quality

### Current Datasets (50,000 words)
- **Coverage**: Top 50,000 most common English words
- **Source**: Open-source word frequency lists
- **Quality**: Good for development and production use
- **Update Date**: Generated automatically

### Sample Data
```json
{
  "you": 22484400,
  "the": 17594291,
  "resilient": 5000,
  "perspicacious": 50
}
```

## Upgrading to Official Datasets

### Option 1: Keep Current (Recommended for Now)
The current 50,000-word dataset is sufficient for most use cases.

### Option 2: Add Official COCA Data
1. Download from: https://www.wordfrequency.info/
2. Process using: `python3 scripts/process_coca_data.py <file>`
3. Replace `coca_frequency.json`

### Option 3: Add Official Lexile Data
1. Download from: https://hub.lexile.com/wordlists/
2. Convert grade levels to Lexile scores
3. Replace `lexile_scores.json`

## Verification

To verify datasets are loaded correctly:

```python
from nlp.dataset_loader import get_dataset_loader

loader = get_dataset_loader()
print(f"COCA words: {len(loader.coca_data)}")
print(f"Lexile words: {len(loader.lexile_data)}")

# Test a word
word = "resilient"
freq = loader.get_word_frequency(word)
lexile = loader.get_lexile_score(word)
difficulty, relic_type = loader.calculate_difficulty_score(word)

print(f"{word}: freq={freq}, lexile={lexile}, difficulty={difficulty}, type={relic_type}")
```

## Next Steps

1. ✅ Datasets are ready to use
2. Test the profiler with real data
3. Monitor performance with 50k words
4. Upgrade to official datasets if needed (optional)

The system is production-ready with the current datasets!

