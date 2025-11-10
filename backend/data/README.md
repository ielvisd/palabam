# Dataset Directory

This directory contains COCA-like word frequency and Lexile-like difficulty scores for word difficulty scoring.

## Expected Files

1. **coca_frequency.json**: Word frequency data (COCA-like)
   - Format: `{"word": frequency_count, ...}`
   - Example: `{"the": 1000000, "resilient": 5000, ...}`
   - Frequency is per million words

2. **lexile_scores.json**: Word difficulty scores (Lexile-like)
   - Format: `{"word": lexile_score, ...}`
   - Example: `{"the": 200, "resilient": 800, ...}`
   - Note: Lower Lexile scores = easier words (range: 0-1600)

## Generating Datasets

### Quick Start (Using wordfreq library - Recommended for Development)

1. **Install dependencies**:
```bash
cd backend
pip install wordfreq
```

2. **Run the generation script**:
```bash
python scripts/generate_datasets.py
```

This will:
- Generate word frequency data using the `wordfreq` library (free, open-source)
- Create Lexile-like scores from frequency data
- Save both datasets as JSON files in this directory

### What the Script Does

- Uses `wordfreq` Python library for word frequency (free alternative to COCA)
- Generates Lexile-like scores by converting frequency to difficulty
- Includes common vocabulary words plus educational terms
- Exports to JSON format matching our schema

## Using Official Datasets

### COCA (Corpus of Contemporary American English)

**Official Source:**
- Website: https://www.english-corpora.org/coca/
- May require licensing/purchase for full dataset
- Word frequency lists available

**To Use Official COCA Data:**
1. Obtain COCA word frequency data
2. Convert to JSON format: `{"word": frequency, ...}`
3. Replace `coca_frequency.json` with your file
4. The system will automatically load it

### Lexile Framework

**Official Source:**
- Lexile Hub: https://hub.lexile.com/
- WordLists available: https://hub.lexile.com/wordlists/
- May require licensing for commercial use

**To Use Official Lexile Data:**
1. Obtain Lexile word-level scores
2. Convert to JSON format: `{"word": lexile_score, ...}`
3. Replace `lexile_scores.json` with your file
4. The system will automatically load it

## Alternative Free Sources

### Word Frequency
- **wordfreq** (Python library): Already integrated
- **Google Books Ngram**: https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
- **Wiktionary word frequency**: Various open-source lists

### Difficulty Scores
- **CEFR levels**: Common European Framework levels (A1-C2)
- **Dale-Chall readability**: Word lists by difficulty
- **Academic Word List**: For educational vocabulary

## Placeholder System

If no datasets are found, the system will:
- Use word length and patterns to estimate difficulty
- Provide basic functionality for development
- Can be seamlessly replaced when datasets are loaded

## Loading Custom Datasets

You can load datasets programmatically:

```python
from nlp.dataset_loader import get_dataset_loader

loader = get_dataset_loader()
loader.load_dataset_file("path/to/coca_data.json", dataset_type="coca")
loader.load_dataset_file("path/to/lexile_data.json", dataset_type="lexile")
```

## File Format

Both files use the same JSON format:
```json
{
  "the": 1000000,
  "resilient": 5000,
  "perspicacious": 50
}
```

- Keys: lowercase words
- Values: frequency count (COCA) or Lexile score (0-1600)

