#!/usr/bin/env python3
"""
Process COCA Data Script
Converts downloaded COCA data files to our JSON format.

Supports multiple COCA data formats:
- CSV files (word, frequency)
- TXT files (word frequency)
- TSV files
"""

import json
import csv
import sys
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / 'data'

def process_coca_csv(csv_path: Path, output_path: Path) -> bool:
    """Process COCA CSV file"""
    if not csv_path.exists():
        logger.error(f"File not found: {csv_path}")
        return False
    
    word_freq = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Try to detect header
            first_row = next(reader)
            start_row = 0
            
            # Check if first row is header
            try:
                int(first_row[1])  # Try to convert second column to int
                # Not a header, rewind
                f.seek(0)
                reader = csv.reader(f)
            except (ValueError, IndexError):
                # Is a header, skip it
                start_row = 1
                logger.info("Detected CSV header, skipping...")
            
            for row in reader:
                if len(row) >= 2:
                    word = row[0].strip().lower()
                    try:
                        # Try different frequency columns
                        freq = None
                        for col_idx in [1, 2, 3]:
                            try:
                                freq = int(float(row[col_idx]))
                                break
                            except (ValueError, IndexError):
                                continue
                        
                        if freq is not None and freq > 0:
                            word_freq[word] = freq
                    except Exception as e:
                        logger.debug(f"Skipping row: {e}")
                        continue
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(word_freq, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed {len(word_freq)} words from CSV")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process CSV: {e}")
        return False

def process_coca_txt(txt_path: Path, output_path: Path) -> bool:
    """Process COCA TXT file (word frequency format)"""
    if not txt_path.exists():
        logger.error(f"File not found: {txt_path}")
        return False
    
    word_freq = {}
    
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Try different formats:
                # "word frequency"
                # "word\tfrequency"
                # "word, frequency"
                # "frequency word"
                
                # Split by whitespace or tab
                parts = re.split(r'[\s\t,]+', line)
                
                if len(parts) >= 2:
                    # Try word first, then frequency
                    try:
                        word = parts[0].lower().strip()
                        freq = int(float(parts[1]))
                        word_freq[word] = freq
                    except (ValueError, IndexError):
                        # Try frequency first, then word
                        try:
                            freq = int(float(parts[0]))
                            word = parts[1].lower().strip()
                            word_freq[word] = freq
                        except (ValueError, IndexError):
                            continue
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(word_freq, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed {len(word_freq)} words from TXT")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process TXT: {e}")
        return False

def main():
    """Main function to process COCA data files"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process COCA data files to JSON format'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to COCA data file (CSV, TXT, or TSV)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=str(DATA_DIR / 'coca_frequency.json'),
        help='Output JSON file path'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)
    
    # Detect file type and process
    suffix = input_path.suffix.lower()
    
    if suffix == '.csv' or suffix == '.tsv':
        success = process_coca_csv(input_path, output_path)
    elif suffix == '.txt':
        success = process_coca_txt(input_path, output_path)
    else:
        logger.error(f"Unsupported file type: {suffix}")
        logger.info("Supported formats: .csv, .tsv, .txt")
        sys.exit(1)
    
    if success:
        logger.info(f"Successfully processed {input_path}")
        logger.info(f"Output saved to: {output_path}")
    else:
        logger.error("Failed to process file")
        sys.exit(1)

if __name__ == '__main__':
    main()

