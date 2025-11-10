# Download Guide for Real Datasets

This guide helps you obtain and integrate real COCA and Lexile datasets into Palabam.

## Quick Start

### Option 1: Use Generated Datasets (Easiest)
The project includes a script that generates datasets automatically:
```bash
cd backend
python3 scripts/generate_datasets.py
```
This creates working datasets using the `wordfreq` library.

### Option 2: Download Real Datasets (Best Quality)

## COCA (Corpus of Contemporary American English)

### Free Sources

1. **Word Frequency Info** (Recommended)
   - URL: https://www.wordfrequency.info/
   - Provides word frequency lists based on COCA
   - Free word lists available
   - Download format: CSV or TXT

2. **English Corpora N-grams** (Free)
   - URL: https://www.ngrams.info/free.asp
   - Free n-gram data from COCA
   - Includes word frequency information
   - Download format: Various

3. **Manual Download Steps**:
   ```bash
   # 1. Download word frequency list from wordfrequency.info
   # 2. Save as: backend/data/coca_raw.csv
   # 3. Process using our script:
   python3 scripts/process_coca_data.py backend/data/coca_raw.csv
   ```

### Official COCA (May Require License)

1. **English-Corpora.org**
   - URL: https://www.english-corpora.org/coca/
   - Full COCA corpus (1 billion words)
   - Word frequency lists for top 60,000 lemmas
   - May require registration or purchase

2. **CorpusData.org**
   - URL: https://www.corpusdata.org/coca2020.asp
   - Full-text COCA data
   - Multiple formats available

## Lexile Framework

### Free Sources

1. **Lexile Hub WordLists** (Recommended)
   - URL: https://hub.lexile.com/wordlists/
   - Word lists by grade level (K-12)
   - Free to download
   - Format: Excel, CSV, or PDF

2. **Download Steps**:
   ```bash
   # 1. Visit Lexile Hub and download word lists
   # 2. Convert grade levels to Lexile scores:
   #    - K-2: 100-400
   #    - 3-5: 400-700
   #    - 6-8: 700-1000
   #    - 9-12: 1000-1600
   # 3. Create JSON: {"word": lexile_score, ...}
   # 4. Save as: backend/data/lexile_scores.json
   ```

### Alternative: Generate from Frequency

If you have COCA frequency data, you can generate Lexile-like scores:
```python
# The generate_datasets.py script already does this
python3 scripts/generate_datasets.py
```

## Processing Downloaded Files

### COCA Data Processing

If you download a COCA file in CSV/TXT format:

```bash
# Process CSV file
python3 scripts/process_coca_data.py path/to/coca_data.csv

# Process TXT file
python3 scripts/process_coca_data.py path/to/coca_data.txt -o backend/data/coca_frequency.json
```

### Lexile Data Processing

1. Download Lexile word lists (Excel/CSV format)
2. Convert grade levels to Lexile scores
3. Create JSON file manually or with a script:

```python
import json
import csv

# Example: Convert Lexile CSV to JSON
lexile_data = {}
with open('lexile_wordlist.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        word = row['word'].lower()
        grade = int(row['grade'])
        # Convert grade to Lexile (approximate)
        lexile = 100 + (grade * 100)  # Adjust formula as needed
        lexile_data[word] = lexile

with open('backend/data/lexile_scores.json', 'w') as f:
    json.dump(lexile_data, f, indent=2)
```

## GitHub Sources (Free, Open-Source)

### Word Frequency Lists

1. **FrequencyWords Repository**
   - URL: https://github.com/hermitdave/FrequencyWords
   - Multiple languages including English
   - Free and open-source
   - Format: TXT

2. **Download Script**:
   ```bash
   # Our download script tries GitHub sources automatically
   python3 scripts/download_datasets.py
   ```

## Google Books Ngram (Very Large)

- URL: https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
- Size: >100GB for full dataset
- Format: TSV
- Note: Very large, requires significant processing

## File Format Requirements

### COCA Frequency Format
```json
{
  "the": 1000000,
  "resilient": 5000,
  "perspicacious": 50
}
```

### Lexile Scores Format
```json
{
  "the": 200,
  "resilient": 800,
  "perspicacious": 1200
}
```

Both files:
- Use lowercase words as keys
- Use integers as values
- Are valid JSON

## Verification

After downloading/processing, verify your datasets:

```python
import json

# Check COCA data
with open('backend/data/coca_frequency.json', 'r') as f:
    coca = json.load(f)
    print(f"COCA: {len(coca)} words")
    print(f"Sample: {list(coca.items())[:5]}")

# Check Lexile data
with open('backend/data/lexile_scores.json', 'r') as f:
    lexile = json.load(f)
    print(f"Lexile: {len(lexile)} words")
    print(f"Sample: {list(lexile.items())[:5]}")
```

## Troubleshooting

### Issue: File format not recognized
- Solution: Use `process_coca_data.py` script which handles multiple formats

### Issue: Dataset too large
- Solution: Filter to most common words (top 10,000-50,000)

### Issue: Missing words
- Solution: Combine multiple sources or use wordfreq as fallback

## Next Steps

1. Download datasets from recommended sources
2. Process using provided scripts
3. Replace generated datasets in `backend/data/`
4. Test the profiler to ensure datasets load correctly

The system will automatically use the new datasets once they're in place!

