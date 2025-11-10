#!/usr/bin/env python3
"""
Dataset Generation Script
Generates COCA-like word frequency and Lexile-like difficulty scores
using free, open-source data sources.

This script:
1. Uses wordfreq library to get word frequency data
2. Generates Lexile-like scores from frequency
3. Exports to JSON files in the data/ directory

To use official COCA/Lexile datasets:
- Replace the generated JSON files with official datasets
- Ensure format matches: {"word": frequency/score, ...}
"""

import json
import sys
from pathlib import Path
import logging

# Add parent directory to path to import dataset_loader
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import wordfreq
    WORDFREQ_AVAILABLE = True
except ImportError:
    WORDFREQ_AVAILABLE = False
    print("Warning: wordfreq not installed. Install with: pip install wordfreq")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common vocabulary words to generate data for
# In production, this would be expanded or loaded from a word list
COMMON_WORDS = [
    # Basic words
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    
    # Common verbs
    'go', 'get', 'make', 'know', 'think', 'take', 'see', 'come', 'want', 'use',
    'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'need', 'feel', 'become',
    
    # Common nouns
    'time', 'year', 'people', 'way', 'day', 'man', 'thing', 'woman', 'life', 'child',
    'world', 'school', 'state', 'family', 'student', 'group', 'country', 'problem', 'hand', 'part',
    
    # Common adjectives
    'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old',
    'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important',
    
    # Educational vocabulary (middle school level)
    'resilient', 'perseverance', 'determined', 'curious', 'adventure', 'challenge',
    'accomplish', 'discover', 'analyze', 'evaluate', 'synthesize', 'comprehend',
    'elaborate', 'illustrate', 'demonstrate', 'investigate', 'examine', 'interpret',
    'persuade', 'narrate', 'describe', 'explain', 'compare', 'contrast',
    
    # Advanced vocabulary
    'perspicacious', 'ubiquitous', 'ephemeral', 'serendipity', 'eloquent', 'meticulous',
    'enigmatic', 'paradoxical', 'sophisticated', 'comprehensive', 'substantial', 'profound'
]

def get_word_frequency(word: str) -> float:
    """
    Get word frequency using wordfreq library
    Returns frequency per million words
    Falls back to estimated frequency if wordfreq not available
    """
    if WORDFREQ_AVAILABLE:
        try:
            # Get frequency in English
            freq = wordfreq.word_frequency(word, 'en')
            # Convert to frequency per million
            return freq * 1_000_000
        except Exception as e:
            logger.warning(f"Could not get frequency for '{word}': {e}")
    
    # Fallback: estimate frequency based on word characteristics
    return estimate_frequency(word)

def frequency_to_lexile(frequency: float) -> int:
    """
    Convert word frequency to Lexile-like score
    Lower frequency = higher Lexile (harder word)
    Higher frequency = lower Lexile (easier word)
    
    Lexile range: 0-1600 (typical range)
    """
    if frequency == 0:
        return 1200  # Unknown words get high Lexile (hard)
    
    # Use logarithmic scale
    import math
    
    # Very common words (frequency > 10000 per million)
    if frequency > 10000:
        return 100 + int(math.log10(frequency / 10000) * 50)
    
    # Common words (frequency 1000-10000)
    elif frequency > 1000:
        return 200 + int((frequency - 1000) / 9000 * 200)
    
    # Moderate words (frequency 100-1000)
    elif frequency > 100:
        return 400 + int((frequency - 100) / 900 * 300)
    
    # Uncommon words (frequency 10-100)
    elif frequency > 10:
        return 700 + int((frequency - 10) / 90 * 300)
    
    # Rare words (frequency 1-10)
    elif frequency > 1:
        return 1000 + int((frequency - 1) / 9 * 400)
    
    # Very rare words (frequency < 1)
    else:
        return 1400 + int(frequency * 200)

def generate_coca_dataset(output_path: Path, words: list = None) -> dict:
    """
    Generate COCA-like word frequency dataset
    """
    if words is None:
        words = COMMON_WORDS
    
    logger.info(f"Generating COCA dataset for {len(words)} words...")
    
    coca_data = {}
    for word in words:
        frequency = get_word_frequency(word)
        if frequency > 0:
            # Round to integer for storage
            coca_data[word.lower()] = int(frequency)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(coca_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Generated COCA dataset with {len(coca_data)} words")
    logger.info(f"Saved to {output_path}")
    
    return coca_data

def generate_lexile_dataset(coca_data: dict, output_path: Path) -> dict:
    """
    Generate Lexile-like difficulty scores from frequency data
    """
    logger.info("Generating Lexile dataset from frequency data...")
    
    lexile_data = {}
    for word, frequency in coca_data.items():
        lexile_score = frequency_to_lexile(frequency)
        lexile_data[word] = lexile_score
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lexile_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Generated Lexile dataset with {len(lexile_data)} words")
    logger.info(f"Saved to {output_path}")
    
    return lexile_data

def estimate_frequency(word: str) -> float:
    """
    Estimate word frequency when wordfreq is not available
    Uses heuristics based on word length and common patterns
    """
    word_lower = word.lower()
    
    # Very common words (top 100)
    very_common = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
    }
    if word_lower in very_common:
        return 50000.0  # Very high frequency
    
    # Common words (top 1000)
    common = {
        'go', 'get', 'make', 'know', 'think', 'take', 'see', 'come', 'want', 'use',
        'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'need', 'feel', 'become',
        'time', 'year', 'people', 'way', 'day', 'man', 'thing', 'woman', 'life', 'child',
        'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old'
    }
    if word_lower in common:
        return 10000.0  # High frequency
    
    # Educational vocabulary (moderate frequency)
    educational = {
        'resilient', 'perseverance', 'determined', 'curious', 'adventure', 'challenge',
        'accomplish', 'discover', 'analyze', 'evaluate', 'synthesize', 'comprehend'
    }
    if word_lower in educational:
        return 500.0  # Moderate frequency
    
    # Advanced vocabulary (low frequency)
    advanced = {
        'perspicacious', 'ubiquitous', 'ephemeral', 'serendipity', 'eloquent', 'meticulous',
        'enigmatic', 'paradoxical', 'sophisticated', 'comprehensive', 'substantial', 'profound'
    }
    if word_lower in advanced:
        return 10.0  # Low frequency
    
    # Estimate based on word length
    length = len(word)
    if length <= 3:
        return 5000.0
    elif length <= 5:
        return 1000.0
    elif length <= 7:
        return 100.0
    elif length <= 9:
        return 50.0
    else:
        return 10.0

def expand_word_list(base_words: list) -> list:
    """
    Expand word list by adding variations and related words
    This is a simple expansion - in production, use a thesaurus API
    """
    expanded = set(base_words)
    
    # Add common variations
    variations = {
        'go': ['goes', 'going', 'went', 'gone'],
        'get': ['gets', 'getting', 'got', 'gotten'],
        'make': ['makes', 'making', 'made'],
        'know': ['knows', 'knowing', 'knew', 'known'],
        'think': ['thinks', 'thinking', 'thought'],
        'take': ['takes', 'taking', 'took', 'taken'],
        'see': ['sees', 'seeing', 'saw', 'seen'],
        'come': ['comes', 'coming', 'came'],
        'good': ['better', 'best', 'well'],
        'big': ['bigger', 'biggest', 'large', 'larger', 'largest'],
        'small': ['smaller', 'smallest', 'little'],
        'new': ['newer', 'newest'],
        'old': ['older', 'oldest', 'elder', 'eldest']
    }
    
    for word in base_words:
        if word in variations:
            expanded.update(variations[word])
    
    return sorted(list(expanded))

def main():
    """Main function to generate both datasets"""
    # Get data directory
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    coca_path = data_dir / 'coca_frequency.json'
    lexile_path = data_dir / 'lexile_scores.json'
    
    # Expand word list
    words = expand_word_list(COMMON_WORDS)
    logger.info(f"Processing {len(words)} words...")
    
    # Generate COCA dataset
    coca_data = generate_coca_dataset(coca_path, words)
    
    # Generate Lexile dataset from COCA data
    lexile_data = generate_lexile_dataset(coca_data, lexile_path)
    
    # Print summary
    print("\n" + "="*60)
    print("Dataset Generation Complete!")
    print("="*60)
    print(f"COCA dataset: {len(coca_data)} words")
    print(f"Lexile dataset: {len(lexile_data)} words")
    print(f"\nFiles created:")
    print(f"  - {coca_path}")
    print(f"  - {lexile_path}")
    print("\nTo use official COCA/Lexile datasets:")
    print("  1. Obtain datasets from official sources")
    print("  2. Convert to JSON format: {\"word\": frequency/score, ...}")
    print("  3. Replace the generated files with official datasets")
    print("="*60)

if __name__ == '__main__':
    main()

