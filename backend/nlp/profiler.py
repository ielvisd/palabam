"""
Story Spark Profiler
Analyzes student transcripts to generate relic resonance profiles
"""
import spacy
import nltk
from typing import Dict, List, Any, Optional
import logging
from collections import Counter
import re

from .dataset_loader import get_dataset_loader

logger = logging.getLogger(__name__)

# Initialize spaCy model (will be loaded on first use)
_nlp_model: Optional[Any] = None

def get_nlp_model():
    """Lazy load spaCy model"""
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
            raise
    return _nlp_model

class StoryProfiler:
    """Profiles student stories to generate vocabulary recommendations"""
    
    def __init__(self):
        self.dataset_loader = get_dataset_loader()
        self.nlp = get_nlp_model()
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    
    def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a transcript and generate a relic resonance profile
        
        Args:
            transcript: Student's voice or text input
            
        Returns:
            Dictionary containing:
            - word_scores: Dict of word -> difficulty_score
            - resonance_data: Profile metadata
            - vocabulary_level: Overall assessment
        """
        # Clean and preprocess
        transcript = self._clean_text(transcript)
        
        if not transcript or len(transcript.strip()) < 10:
            raise ValueError("Transcript too short for analysis")
        
        # Tokenize and analyze with spaCy
        doc = self.nlp(transcript)
        
        # Extract words and their properties
        words_data = self._extract_words(doc)
        
        # Score words using COCA/Lexile datasets
        word_scores = {}
        for word_info in words_data:
            word = word_info['word']
            difficulty, relic_type = self.dataset_loader.calculate_difficulty_score(word)
            
            word_scores[word] = {
                'difficulty_score': difficulty,
                'relic_type': relic_type,
                'frequency': self.dataset_loader.get_word_frequency(word),
                'pos': word_info.get('pos', 'UNKNOWN'),
                'count': word_info.get('count', 1)
            }
        
        # Calculate overall vocabulary level
        vocabulary_level = self._calculate_vocabulary_level(word_scores)
        
        # Calculate vocabulary richness metrics
        lexical_diversity = self._calculate_lexical_diversity(word_scores)
        sophistication_score = self._calculate_sophistication_score(word_scores)
        
        # Categorize words by usage quality
        word_categories = self._categorize_words(word_scores, vocabulary_level)
        
        # Generate resonance data
        resonance_data = {
            'vocabulary_level': vocabulary_level,
            'total_words': len(words_data),
            'unique_words': len(word_scores),
            'relic_distribution': self._calculate_relic_distribution(word_scores),
            'themes': self._extract_themes(doc),
            'complexity_score': self._calculate_complexity_score(word_scores),
            'lexical_diversity': lexical_diversity,
            'sophistication_score': sophistication_score,
            'pos_distribution': self._calculate_pos_distribution(word_scores),
            'word_categories': word_categories
        }
        
        return {
            'word_scores': word_scores,
            'resonance_data': resonance_data,
            'vocabulary_level': vocabulary_level,
            'word_categories': word_categories
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\'"]', '', text)
        return text.strip()
    
    def _extract_words(self, doc) -> List[Dict[str, Any]]:
        """Extract meaningful words from spaCy doc"""
        words = []
        word_counts = Counter()
        
        for token in doc:
            # Skip punctuation, spaces, and stop words for analysis
            if token.is_alpha and not token.is_stop and len(token.text) > 2:
                word_lower = token.lemma_.lower()
                word_counts[word_lower] += 1
                
                words.append({
                    'word': word_lower,
                    'original': token.text,
                    'pos': token.pos_,
                    'lemma': token.lemma_,
                    'count': word_counts[word_lower]
                })
        
        # Deduplicate while preserving count
        seen = set()
        unique_words = []
        for word_info in words:
            word = word_info['word']
            if word not in seen:
                seen.add(word)
                unique_words.append(word_info)
        
        return unique_words
    
    def _calculate_vocabulary_level(self, word_scores: Dict[str, Any]) -> str:
        """
        Calculate overall vocabulary level as grade level (K-12)
        Uses percentile-based scoring to focus on sophisticated words rather than
        being skewed by common words (the, and, is, etc.)
        """
        if not word_scores:
            return 'K-1'
        
        # Extract all difficulty scores
        difficulties = [
            score['difficulty_score'] 
            for score in word_scores.values()
        ]
        
        if not difficulties:
            return 'K-1'
        
        # Filter out very common words (difficulty < 20) to avoid skewing
        # These are words like "the", "and", "is" that appear in all writing
        filtered_difficulties = [d for d in difficulties if d >= 20]
        
        # If we filtered out too many (less than 10% of words), use all words
        # but use percentile-based approach
        if len(filtered_difficulties) < len(difficulties) * 0.1:
            filtered_difficulties = difficulties
        
        # Sort difficulties to calculate percentiles
        sorted_difficulties = sorted(filtered_difficulties)
        
        # Use 75th percentile (top quartile) to focus on sophisticated vocabulary
        # This represents the level of the most advanced words the student uses
        percentile_75_index = int(len(sorted_difficulties) * 0.75)
        if percentile_75_index >= len(sorted_difficulties):
            percentile_75_index = len(sorted_difficulties) - 1
        
        # Calculate average of top 25% most difficult words
        top_quartile = sorted_difficulties[percentile_75_index:]
        if top_quartile:
            representative_difficulty = sum(top_quartile) / len(top_quartile)
        else:
            # Fallback to median if no top quartile
            median_index = len(sorted_difficulties) // 2
            representative_difficulty = sorted_difficulties[median_index] if sorted_difficulties else 30
        
        # Map difficulty score to grade level
        # K-1: 5-15, 2-3: 15-25, 4-5: 25-35, 6-7: 35-45, 8-9: 45-55, 10-11: 55-65, 12+: 65-75
        if representative_difficulty < 15:
            return 'K-1'
        elif representative_difficulty < 25:
            return '2-3'
        elif representative_difficulty < 35:
            return '4-5'
        elif representative_difficulty < 45:
            return '6-7'
        elif representative_difficulty < 55:
            return '8-9'
        elif representative_difficulty < 65:
            return '10-11'
        else:
            return '12+'
    
    def difficulty_to_grade_level(self, difficulty: float) -> str:
        """Convert difficulty score to grade level"""
        if difficulty < 15:
            return 'K-1'
        elif difficulty < 25:
            return '2-3'
        elif difficulty < 35:
            return '4-5'
        elif difficulty < 45:
            return '6-7'
        elif difficulty < 55:
            return '8-9'
        elif difficulty < 65:
            return '10-11'
        else:
            return '12+'
    
    def grade_level_to_difficulty_range(self, grade_level: str) -> tuple:
        """Convert grade level to difficulty score range"""
        grade_ranges = {
            'K-1': (5, 15),
            '2-3': (15, 25),
            '4-5': (25, 35),
            '6-7': (35, 45),
            '8-9': (45, 55),
            '10-11': (55, 65),
            '12+': (65, 75)
        }
        return grade_ranges.get(grade_level, (25, 35))  # Default to 4-5 grade
    
    def get_next_grade_levels(self, current_grade: str) -> List[str]:
        """Get the next 1-2 grade levels for ZPD recommendations"""
        grade_sequence = ['K-1', '2-3', '4-5', '6-7', '8-9', '10-11', '12+']
        try:
            current_index = grade_sequence.index(current_grade)
            # Get next 1-2 grade levels (max at 12+)
            next_grades = []
            if current_index < len(grade_sequence) - 1:
                next_grades.append(grade_sequence[current_index + 1])
            if current_index < len(grade_sequence) - 2:
                next_grades.append(grade_sequence[current_index + 2])
            return next_grades if next_grades else [current_grade]  # If at 12+, stay at 12+
        except ValueError:
            # If grade not found, default to recommending 4-5 and 6-7
            return ['4-5', '6-7']
    
    def _calculate_relic_distribution(self, word_scores: Dict[str, Any]) -> Dict[str, int]:
        """Calculate distribution of relic types"""
        distribution = {'whisper': 0, 'echo': 0, 'resonance': 0, 'thunder': 0}
        
        for score in word_scores.values():
            relic_type = score.get('relic_type', 'echo')
            distribution[relic_type] = distribution.get(relic_type, 0) + 1
        
        return distribution
    
    def _extract_themes(self, doc) -> List[str]:
        """Extract themes from the transcript using NLP"""
        themes = []
        
        # Extract named entities
        entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'EVENT', 'WORK_OF_ART']]
        
        # Extract common topics from keywords
        keywords = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                keywords.append(token.lemma_.lower())
        
        # Count keyword frequency
        keyword_counts = Counter(keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(5)]
        
        themes.extend(top_keywords[:3])  # Top 3 themes
        
        return themes
    
    def _calculate_complexity_score(self, word_scores: Dict[str, Any]) -> float:
        """Calculate overall complexity score (0-1)"""
        if not word_scores:
            return 0.0
        
        avg_difficulty = sum(
            score['difficulty_score'] 
            for score in word_scores.values()
        ) / len(word_scores)
        
        # Normalize to 0-1
        return min(1.0, avg_difficulty / 100.0)
    
    def _calculate_lexical_diversity(self, word_scores: Dict[str, Any]) -> float:
        """Calculate lexical diversity (unique words / total words)"""
        if not word_scores:
            return 0.0
        
        total_occurrences = sum(score.get('count', 1) for score in word_scores.values())
        unique_words = len(word_scores)
        
        if total_occurrences == 0:
            return 0.0
        
        return unique_words / total_occurrences
    
    def _calculate_sophistication_score(self, word_scores: Dict[str, Any]) -> float:
        """Calculate vocabulary sophistication (proportion of advanced words)"""
        if not word_scores:
            return 0.0
        
        advanced_count = sum(
            1 for score in word_scores.values()
            if score.get('difficulty_score', 50) >= 60
        )
        
        return advanced_count / len(word_scores)
    
    def _calculate_pos_distribution(self, word_scores: Dict[str, Any]) -> Dict[str, int]:
        """Calculate part of speech distribution"""
        pos_dist = {}
        for score in word_scores.values():
            pos = score.get('pos', 'UNKNOWN')
            pos_dist[pos] = pos_dist.get(pos, 0) + 1
        return pos_dist
    
    def _categorize_words(
        self, 
        word_scores: Dict[str, Any], 
        vocabulary_level: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize words into:
        - uses_well: Words at or above student's grade level used correctly
        - needs_practice: Words below level or used incorrectly (gaps)
        - to_master: Words slightly above level for growth
        
        Args:
            word_scores: Dictionary of word -> score data
            vocabulary_level: Student's overall vocabulary level (e.g., '6-7')
            
        Returns:
            Dictionary with categorized word lists
        """
        if not word_scores:
            return {
                'uses_well': [],
                'needs_practice': [],
                'to_master': []
            }
        
        # Get difficulty range for student's grade level
        student_min, student_max = self.grade_level_to_difficulty_range(vocabulary_level)
        student_avg = (student_min + student_max) / 2
        
        # Get next grade level range for "to_master"
        next_grades = self.get_next_grade_levels(vocabulary_level)
        if next_grades:
            next_min, next_max = self.grade_level_to_difficulty_range(next_grades[0])
        else:
            # If at 12+, use a higher range
            next_min, next_max = (65, 75)
        
        uses_well = []
        needs_practice = []
        to_master = []
        
        for word, score_data in word_scores.items():
            difficulty = score_data.get('difficulty_score', 50)
            frequency = score_data.get('frequency', 0)
            
            word_info = {
                'word': word,
                'difficulty_score': difficulty,
                'grade_level': self.difficulty_to_grade_level(difficulty),
                'relic_type': score_data.get('relic_type', 'echo'),
                'frequency': frequency,
                'pos': score_data.get('pos', 'UNKNOWN'),
                'count': score_data.get('count', 1)
            }
            
            # Categorize based on difficulty relative to student level
            if difficulty >= student_min:
                # Word is at or above student's level - they use it well
                uses_well.append(word_info)
            elif difficulty < student_min - 10:
                # Word is significantly below student's level - gap/needs practice
                # But only if it's a common word they should know
                if frequency > 1000:  # Common word they should know
                    needs_practice.append(word_info)
                else:
                    # Rare word below level - might be intentional simple word
                    pass
            else:
                # Word is slightly below level - could be a gap
                if frequency > 500:  # Common enough they should know it
                    needs_practice.append(word_info)
            
            # Words to master: in the next grade level range
            if next_min <= difficulty <= next_max:
                # Don't duplicate - if already in uses_well, don't add to to_master
                if difficulty < student_min or word_info not in uses_well:
                    to_master.append(word_info)
        
        # Sort each category by difficulty (descending for uses_well, ascending for others)
        uses_well.sort(key=lambda x: x['difficulty_score'], reverse=True)
        needs_practice.sort(key=lambda x: x['difficulty_score'])
        to_master.sort(key=lambda x: x['difficulty_score'])
        
        return {
            'uses_well': uses_well[:20],  # Top 20 words used well
            'needs_practice': needs_practice[:15],  # Top 15 gaps
            'to_master': to_master[:10]  # Top 10 growth words
        }

# FastAPI router
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ProfileRequest(BaseModel):
    transcript: str
    inputMode: str = "text"
    student_id: Optional[str] = None

class ProfileResponse(BaseModel):
    profile_id: str
    word_scores: Dict[str, Any]
    resonance_data: Dict[str, Any]
    vocabulary_level: str
    recommended_words: List[str]  # Will be populated by recommender

@router.post("/", response_model=ProfileResponse)
async def create_profile(request: ProfileRequest):
    """Create a relic resonance profile from a transcript"""
    try:
        profiler = StoryProfiler()
        analysis = profiler.analyze_transcript(request.transcript)
        
        # Get recommended words from recommender
        from . import recommender
        recommender_instance = recommender.WordRecommender()
        recommendations = await recommender_instance.recommend_words(
            profile={
                'word_scores': analysis['word_scores'],
                'resonance_data': analysis['resonance_data']
            },
            count=7
        )
        recommended_words = [r['word'] for r in recommendations]
        
        # Store profile in Supabase
        from db import profiles as db_profiles
        from db import recommendations as db_recommendations
        
        if request.student_id:
            profile_id = await db_profiles.create_profile(
                student_id=request.student_id,
                resonance_data=analysis['resonance_data'],
                word_scores=analysis['word_scores'],
                transcript=request.transcript,
                vocabulary_level=analysis['vocabulary_level'],
                recommended_words=recommended_words
            )
            
            # Store recommendations in database
            await db_recommendations.create_recommendations_batch(
                student_id=request.student_id,
                profile_id=profile_id,
                recommendations=recommendations
            )
        else:
            # If no student_id provided, create a temporary profile
            # In production, this should require authentication
            profile_id = "temp-id"
            logger.warning("No student_id provided, using temporary profile ID")
        
        return ProfileResponse(
            profile_id=profile_id,
            word_scores=analysis['word_scores'],
            resonance_data=analysis['resonance_data'],
            vocabulary_level=analysis['vocabulary_level'],
            recommended_words=recommended_words
        )
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

