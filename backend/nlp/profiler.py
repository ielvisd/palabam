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
        
        # Generate resonance data
        resonance_data = {
            'vocabulary_level': vocabulary_level,
            'total_words': len(words_data),
            'unique_words': len(word_scores),
            'relic_distribution': self._calculate_relic_distribution(word_scores),
            'themes': self._extract_themes(doc),
            'complexity_score': self._calculate_complexity_score(word_scores)
        }
        
        return {
            'word_scores': word_scores,
            'resonance_data': resonance_data,
            'vocabulary_level': vocabulary_level
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
        """Calculate overall vocabulary level"""
        if not word_scores:
            return 'beginner'
        
        avg_difficulty = sum(
            score['difficulty_score'] 
            for score in word_scores.values()
        ) / len(word_scores)
        
        if avg_difficulty < 30:
            return 'beginner'
        elif avg_difficulty < 50:
            return 'intermediate'
        elif avg_difficulty < 70:
            return 'advanced'
        else:
            return 'expert'
    
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
        
        # Store profile in Supabase
        from db import profiles as db_profiles
        
        if request.student_id:
            profile_id = await db_profiles.create_profile(
                student_id=request.student_id,
                resonance_data=analysis['resonance_data'],
                word_scores=analysis['word_scores']
            )
        else:
            # If no student_id provided, create a temporary profile
            # In production, this should require authentication
            profile_id = "temp-id"
            logger.warning("No student_id provided, using temporary profile ID")
        
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

