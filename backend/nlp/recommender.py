"""
Relic Resonance Recommender
Suggests ZPD-balanced words (70-80% learnability) based on student profiles
"""
from typing import Dict, List, Any, Optional
import logging
from .dataset_loader import get_dataset_loader

logger = logging.getLogger(__name__)

class WordRecommender:
    """Recommends vocabulary words based on student profiles"""
    
    def __init__(self):
        self.dataset_loader = get_dataset_loader()
    
    async def recommend_words(
        self,
        profile: Dict[str, Any],
        count: int = 7,
        zpd_range: tuple = (0.70, 0.80)
    ) -> List[Dict[str, Any]]:
        """
        Recommend words in the Zone of Proximal Development (ZPD)
        
        Args:
            profile: Student's relic resonance profile
            count: Number of words to recommend (default 5-7)
            zpd_range: Target learnability range (default 70-80%)
            
        Returns:
            List of recommended words with metadata
        """
        word_scores = profile.get('word_scores', {})
        resonance_data = profile.get('resonance_data', {})
        
        # Calculate current vocabulary level
        current_level = self._calculate_current_level(word_scores, resonance_data)
        
        # Find words in ZPD (slightly above current level)
        zpd_words = await self._find_zpd_words(current_level, zpd_range, count)
        
        # Filter out words already in profile
        existing_words = set(word_scores.keys())
        zpd_words = [w for w in zpd_words if w['word'] not in existing_words]
        
        # Sort by relevance and return top recommendations
        recommendations = sorted(
            zpd_words,
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )[:count]
        
        return recommendations
    
    def _calculate_current_level(self, word_scores: Dict[str, Any], resonance_data: Dict[str, Any]) -> float:
        """Calculate student's current vocabulary level (0-100)"""
        if not word_scores:
            return 30.0  # Beginner default
        
        # Average difficulty of words used
        avg_difficulty = sum(
            score.get('difficulty_score', 50)
            for score in word_scores.values()
        ) / len(word_scores)
        
        # Adjust based on complexity score
        complexity = resonance_data.get('complexity_score', 0.5)
        adjusted_level = avg_difficulty * (0.7 + 0.3 * complexity)
        
        return min(100.0, adjusted_level)
    
    async def _find_zpd_words(
        self,
        current_level: float,
        zpd_range: tuple,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Find words in the ZPD range
        ZPD = words that are 70-80% learnable (slightly above current level)
        """
        target_min = current_level + (100 - current_level) * zpd_range[0]
        target_max = current_level + (100 - current_level) * zpd_range[1]
        
        # Get word pool from database
        sample_words = await self._get_word_pool()
        
        recommendations = []
        
        for word_data in sample_words:
            difficulty = word_data.get('difficulty_score', 50)
            
            # Check if word is in ZPD range
            if target_min <= difficulty <= target_max:
                # Calculate relevance score
                relevance = self._calculate_relevance(difficulty, current_level, target_min, target_max)
                
                recommendations.append({
                    'word': word_data['word'],
                    'difficulty_score': difficulty,
                    'relic_type': word_data.get('relic_type', 'echo'),
                    'definition': word_data.get('definition', ''),
                    'example': word_data.get('example', ''),
                    'relevance_score': relevance
                })
        
        return recommendations
    
    def _calculate_relevance(
        self,
        difficulty: float,
        current_level: float,
        target_min: float,
        target_max: float
    ) -> float:
        """Calculate how relevant a word is to the student's ZPD"""
        # Words closer to the middle of ZPD range are more relevant
        zpd_center = (target_min + target_max) / 2
        distance_from_center = abs(difficulty - zpd_center)
        zpd_width = target_max - target_min
        
        # Normalize relevance (closer to center = higher relevance)
        relevance = 1.0 - (distance_from_center / (zpd_width / 2))
        return max(0.0, min(1.0, relevance))
    
    async def _get_word_pool(self) -> List[Dict[str, Any]]:
        """
        Get pool of words to recommend from database
        """
        try:
            from db import words as db_words
            
            # Search for words in ZPD range (30-80 difficulty)
            word_pool = await db_words.search_words(
                min_difficulty=30,
                max_difficulty=80,
                limit=100
            )
            
            if word_pool:
                return word_pool
            
            # Fallback to sample words if database is empty
            logger.warning("Word pool from database is empty, using fallback")
            return self._get_fallback_word_pool()
            
        except Exception as e:
            logger.warning(f"Error fetching word pool from database: {e}, using fallback")
            return self._get_fallback_word_pool()
    
    def _get_fallback_word_pool(self) -> List[Dict[str, Any]]:
        """Fallback word pool if database is unavailable"""
        return [
            {
                'word': 'resilient',
                'difficulty_score': 65,
                'relic_type': 'resonance',
                'definition': 'able to recover quickly from difficulties',
                'example': 'She was resilient after the setback.'
            },
            {
                'word': 'perseverance',
                'difficulty_score': 75,
                'relic_type': 'thunder',
                'definition': 'persistence in doing something despite difficulty',
                'example': 'His perseverance paid off in the end.'
            },
            {
                'word': 'curious',
                'difficulty_score': 35,
                'relic_type': 'echo',
                'definition': 'eager to know or learn something',
                'example': 'The curious child asked many questions.'
            },
            {
                'word': 'adventure',
                'difficulty_score': 40,
                'relic_type': 'echo',
                'definition': 'an exciting or dangerous experience',
                'example': 'We went on an adventure in the forest.'
            },
            {
                'word': 'challenge',
                'difficulty_score': 45,
                'relic_type': 'echo',
                'definition': 'a task or situation that tests ability',
                'example': 'The math problem was a real challenge.'
            },
            {
                'word': 'accomplish',
                'difficulty_score': 55,
                'relic_type': 'resonance',
                'definition': 'to achieve or complete successfully',
                'example': 'She worked hard to accomplish her goals.'
            },
            {
                'word': 'discover',
                'difficulty_score': 50,
                'relic_type': 'resonance',
                'definition': 'to find something for the first time',
                'example': 'Scientists discover new things every day.'
            }
        ]
    
    def evolve_word(self, current_word: str, mastery_level: float) -> Optional[Dict[str, Any]]:
        """
        Suggest next word evolution based on mastery
        Dynamic pacing: Mastery → evolution (e.g., "big" → "enormous")
        """
        if mastery_level < 0.8:  # Not yet mastered
            return None
        
        # Find more advanced synonym or related word
        # This would use a thesaurus or word relationship database
        evolution_map = {
            'big': {'word': 'enormous', 'difficulty_score': 45},
            'happy': {'word': 'ecstatic', 'difficulty_score': 60},
            'sad': {'word': 'melancholy', 'difficulty_score': 70},
            'good': {'word': 'excellent', 'difficulty_score': 50},
            'bad': {'word': 'terrible', 'difficulty_score': 50}
        }
        
        if current_word.lower() in evolution_map:
            return evolution_map[current_word.lower()]
        
        return None

# FastAPI router
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RecommendRequest(BaseModel):
    profile: Dict[str, Any]
    count: int = 7
    zpd_range: tuple = (0.70, 0.80)

class RecommendResponse(BaseModel):
    recommended_words: List[Dict[str, Any]]

@router.post("/", response_model=RecommendResponse)
async def recommend_words(request: RecommendRequest):
    """Get word recommendations based on profile"""
    try:
        recommender = WordRecommender()
        recommendations = await recommender.recommend_words(
            request.profile,
            count=request.count,
            zpd_range=request.zpd_range
        )
        
        return RecommendResponse(recommended_words=recommendations)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

