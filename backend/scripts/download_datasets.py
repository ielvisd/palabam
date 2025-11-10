#!/usr/bin/env python3
"""
Download Real Datasets Script
Downloads and processes word frequency and difficulty data from various free sources.

Sources:
1. Google Books Ngram (free, large dataset)
2. COCA word frequency lists (if available)
3. Lexile word lists (grade-based vocabulary)
4. Other free sources
"""

import json
import sys
import requests
import csv
from pathlib import Path
from typing import Dict, List
import logging
import gzip
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

def download_google_books_ngram(output_path: Path, max_words: int = 10000) -> Dict[str, int]:
    """
    Download Google Books Ngram word frequency data
    
    Note: Google Books Ngram data is very large. This function downloads
    a sample of the most common words from the 1-gram dataset.
    
    For full dataset, visit: https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
    """
    logger.info("Downloading Google Books Ngram data...")
    
    # Google Books Ngram 1-gram data URL (sample)
    # Full dataset is very large, so we'll use a curated list
    # For production, download from: https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
    
    # Alternative: Use a pre-processed word frequency list
    # Many GitHub repos have processed versions
    
    logger.warning("Google Books Ngram full dataset is very large (>100GB).")
    logger.info("Using wordfreq library as alternative (already integrated).")
    
    # Return empty dict - we'll use wordfreq instead
    return {}

def download_coca_wordlist(output_path: Path) -> Dict[str, int]:
    """
    Download COCA word frequency list
    
    COCA provides free word frequency lists for top 60,000 lemmas.
    Visit: https://www.english-corpora.org/coca/
    """
    logger.info("Attempting to download COCA word frequency list...")
    
    # COCA word lists are available but may require registration
    # Check: https://www.wordfrequency.info/
    
    logger.warning("COCA word lists may require registration or purchase.")
    logger.info("Alternative: Use wordfreq library or download from wordfrequency.info")
    
    # Instructions for manual download:
    print("\n" + "="*60)
    print("COCA Word Frequency List Download Instructions:")
    print("="*60)
    print("1. Visit: https://www.wordfrequency.info/")
    print("2. Or: https://www.english-corpora.org/coca/")
    print("3. Download the word frequency list (CSV or TXT format)")
    print("4. Convert to JSON format: {\"word\": frequency, ...}")
    print("5. Save as: backend/data/coca_frequency.json")
    print("="*60 + "\n")
    
    return {}

def download_lexile_wordlists(output_path: Path) -> Dict[str, int]:
    """
    Download Lexile word lists by grade
    
    Lexile provides word lists by grade level.
    Visit: https://hub.lexile.com/wordlists/
    """
    logger.info("Attempting to download Lexile word lists...")
    
    # Lexile word lists are available from the hub
    lexile_url = "https://hub.lexile.com/wordlists/"
    
    logger.warning("Lexile word lists require manual download from the hub.")
    logger.info(f"Visit: {lexile_url}")
    
    # Instructions for manual download:
    print("\n" + "="*60)
    print("Lexile Word Lists Download Instructions:")
    print("="*60)
    print("1. Visit: https://hub.lexile.com/wordlists/")
    print("2. Download word lists by grade level (K-12)")
    print("3. Convert to Lexile scores (lower grade = easier = lower Lexile)")
    print("4. Format: {\"word\": lexile_score, ...}")
    print("5. Save as: backend/data/lexile_scores.json")
    print("="*60 + "\n")
    
    return {}

def download_github_word_frequency(output_path: Path) -> Dict[str, int]:
    """
    Download word frequency data from GitHub repositories
    
    Many open-source projects provide word frequency lists.
    """
    logger.info("Searching for GitHub word frequency datasets...")
    
    # Popular GitHub repos with word frequency data:
    github_sources = [
        "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/en/en_50k.txt",
        # Add more sources as found
    ]
    
    word_freq = {}
    
    for url in github_sources:
        try:
            logger.info(f"Downloading from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse frequency word list (format: word frequency)
            for line in response.text.split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        word = parts[0].lower()
                        try:
                            freq = int(parts[1])
                            word_freq[word] = freq
                        except ValueError:
                            continue
            
            logger.info(f"Downloaded {len(word_freq)} words from GitHub")
            break  # Use first successful source
            
        except Exception as e:
            logger.warning(f"Failed to download from {url}: {e}")
            continue
    
    if word_freq:
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(word_freq, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(word_freq)} words to {output_path}")
    
    return word_freq

def convert_csv_to_json(csv_path: Path, json_path: Path, word_col: int = 0, freq_col: int = 1):
    """
    Convert CSV word frequency file to JSON format
    """
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return False
    
    word_freq = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header if present
            
            for row in reader:
                if len(row) > max(word_col, freq_col):
                    word = row[word_col].lower().strip()
                    try:
                        freq = int(float(row[freq_col]))
                        word_freq[word] = freq
                    except (ValueError, IndexError):
                        continue
        
        # Save as JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(word_freq, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Converted {len(word_freq)} words from CSV to JSON")
        return True
        
    except Exception as e:
        logger.error(f"Failed to convert CSV: {e}")
        return False

def main():
    """Main function to download datasets from various sources"""
    print("\n" + "="*60)
    print("Real Dataset Downloader")
    print("="*60)
    print("\nThis script attempts to download word frequency data from free sources.")
    print("For official COCA/Lexile datasets, manual download may be required.\n")
    
    # Try GitHub sources first (free, open-source)
    github_path = DATA_DIR / 'coca_frequency_github.json'
    github_data = download_github_word_frequency(github_path)
    
    if github_data:
        # Copy to main file
        main_path = DATA_DIR / 'coca_frequency.json'
        with open(main_path, 'w', encoding='utf-8') as f:
            json.dump(github_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Updated {main_path} with {len(github_data)} words")
    
    # Show instructions for manual downloads
    download_coca_wordlist(DATA_DIR / 'coca_frequency.json')
    download_lexile_wordlists(DATA_DIR / 'lexile_scores.json')
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. If GitHub download succeeded, datasets are ready to use")
    print("2. For better data, download official COCA/Lexile datasets manually")
    print("3. Use convert_csv_to_json() to process downloaded CSV files")
    print("4. Replace JSON files in backend/data/ with your datasets")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

