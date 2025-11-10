"""
Dataset Loader for COCA/Lexile Corpora
Handles loading and querying word frequency/difficulty data
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DatasetLoader:
    """Base class for loading word difficulty datasets"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.coca_data: Dict[str, int] = {}
        self.lexile_data: Dict[str, int] = {}
        self._load_datasets()
    
    def _load_datasets(self):
        """Load COCA and Lexile datasets from files"""
        # COCA dataset (word frequency)
        coca_path = self.data_dir / "coca_frequency.json"
        if coca_path.exists():
            try:
                with open(coca_path, 'r', encoding='utf-8') as f:
                    self.coca_data = json.load(f)
                logger.info(f"Loaded {len(self.coca_data)} COCA word frequencies")
            except Exception as e:
                logger.warning(f"Failed to load COCA data: {e}")
        
        # Lexile dataset (word difficulty scores)
        lexile_path = self.data_dir / "lexile_scores.json"
        if lexile_path.exists():
            try:
                with open(lexile_path, 'r', encoding='utf-8') as f:
                    self.lexile_data = json.load(f)
                logger.info(f"Loaded {len(self.lexile_data)} Lexile word scores")
            except Exception as e:
                logger.warning(f"Failed to load Lexile data: {e}")
        
        # If datasets are empty, create placeholder structure
        if not self.coca_data and not self.lexile_data:
            logger.warning("No COCA/Lexile datasets found. Using placeholder system.")
            self._create_placeholder_data()
    
    def _create_placeholder_data(self):
        """Create placeholder data structure for development"""
        # This will be replaced when real datasets are available
        # For now, we'll use word length and common word lists as proxies
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'
        }
        
        # Initialize with common words having high frequency
        for word in common_words:
            self.coca_data[word.lower()] = 1000000
            self.lexile_data[word.lower()] = 200  # Lower Lexile = easier
    
    def get_word_frequency(self, word: str) -> int:
        """Get COCA frequency for a word"""
        return self.coca_data.get(word.lower(), 0)
    
    def get_lexile_score(self, word: str) -> Optional[int]:
        """Get Lexile difficulty score for a word (lower = easier)"""
        return self.lexile_data.get(word.lower())
    
    def calculate_difficulty_score(self, word: str) -> Tuple[int, str]:
        """
        Calculate difficulty score and relic type for a word
        Returns: (difficulty_score, relic_type)
        """
        word_lower = word.lower()
        
        # Get frequency and Lexile data
        frequency = self.get_word_frequency(word_lower)
        lexile = self.get_lexile_score(word_lower)
        
        # Calculate base difficulty (0-100 scale)
        # Higher frequency = easier (lower score)
        # Higher Lexile = harder (higher score)
        
        if lexile is not None:
            # Use Lexile score directly (typically 0-1600, we'll normalize)
            difficulty = min(100, max(0, int((lexile / 1600) * 100)))
        elif frequency > 0:
            # Use frequency as inverse difficulty
            # Log scale: log10(frequency) -> lower for common words
            import math
            if frequency >= 10000:
                difficulty = 10  # Very common
            elif frequency >= 1000:
                difficulty = 30
            elif frequency >= 100:
                difficulty = 50
            elif frequency >= 10:
                difficulty = 70
            else:
                difficulty = 90  # Rare words
        else:
            # Fallback: use word length and complexity
            difficulty = self._estimate_difficulty_from_word(word)
        
        # Map to relic type
        if difficulty < 25:
            relic_type = 'whisper'
        elif difficulty < 50:
            relic_type = 'echo'
        elif difficulty < 75:
            relic_type = 'resonance'
        else:
            relic_type = 'thunder'
        
        return difficulty, relic_type
    
    def _estimate_difficulty_from_word(self, word: str) -> int:
        """Estimate difficulty from word characteristics when no dataset data"""
        score = 50  # Base score
        
        # Longer words tend to be harder
        if len(word) > 10:
            score += 20
        elif len(word) > 7:
            score += 10
        
        # Words with uncommon letter combinations
        uncommon_patterns = ['x', 'z', 'q', 'ph', 'th', 'ch', 'sh']
        for pattern in uncommon_patterns:
            if pattern in word.lower():
                score += 5
        
        return min(100, score)
    
    def load_dataset_file(self, file_path: str, dataset_type: str = 'coca'):
        """
        Load dataset from a file
        Expected format: JSON with {word: frequency/score}
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if dataset_type == 'coca':
                self.coca_data.update(data)
                logger.info(f"Loaded {len(data)} COCA entries from {file_path}")
            elif dataset_type == 'lexile':
                self.lexile_data.update(data)
                logger.info(f"Loaded {len(data)} Lexile entries from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load dataset from {file_path}: {e}")
            raise

# Global instance
_dataset_loader: Optional[DatasetLoader] = None

def get_dataset_loader() -> DatasetLoader:
    """Get or create global dataset loader instance"""
    global _dataset_loader
    if _dataset_loader is None:
        _dataset_loader = DatasetLoader()
    return _dataset_loader

