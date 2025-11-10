# Scripts Directory

Utility scripts for the Palabam backend.

## generate_datasets.py

Generates word frequency and difficulty score datasets using free, open-source data.

### Usage

```bash
# Make sure wordfreq is installed
pip install wordfreq

# Run the script
python scripts/generate_datasets.py
```

### What It Does

1. Uses `wordfreq` library to get word frequency data
2. Converts frequency to Lexile-like difficulty scores
3. Exports to JSON files in `data/` directory:
   - `coca_frequency.json`
   - `lexile_scores.json`

### Customization

Edit the `COMMON_WORDS` list in the script to add more words, or modify the `expand_word_list()` function to include more variations.

### Output

The script generates JSON files that can be:
- Used immediately for development
- Replaced with official COCA/Lexile datasets when available
- Extended with additional vocabulary words

