"""
API endpoints for Student Progress and Achievements
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from db import student_progress as db_progress
from db import achievements as db_achievements
from db import submissions as db_submissions
from db import profiles as db_profiles
from nlp import recommender

logger = logging.getLogger(__name__)

router = APIRouter()

class StudentProgressResponse(BaseModel):
    student_id: str
    vocabulary_level: str
    total_words_written: int
    submission_count: int
    current_streak: int
    total_points: int
    last_submission_date: Optional[str] = None

class AchievementResponse(BaseModel):
    id: str
    achievement_type: str
    earned_at: str

@router.get("/{student_id}/progress", response_model=StudentProgressResponse)
async def get_student_progress(student_id: str):
    """Get student progress"""
    try:
        progress = await db_progress.get_or_create_progress(student_id)
        return StudentProgressResponse(**progress)
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}/achievements")
async def get_student_achievements(student_id: str):
    """Get all achievements for a student"""
    try:
        achievements = await db_achievements.get_student_achievements(student_id)
        return {"achievements": achievements}
    except Exception as e:
        logger.error(f"Error fetching achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}/recommendations")
async def get_student_recommendations(student_id: str):
    """Get recommended words for a student based on their latest profile"""
    try:
        # Get latest profile
        profiles = await db_profiles.get_student_profiles(student_id)
        if not profiles:
            return {"recommended_words": []}
        
        latest_profile = profiles[0]  # Already sorted by created_at desc
        
        # Get recommendations
        recommender_instance = recommender.WordRecommender()
        recommendations = await recommender_instance.recommend_words(
            profile={
                'word_scores': latest_profile.get('word_scores', {}),
                'resonance_data': latest_profile.get('resonance_data', {})
            },
            count=7
        )
        
        return {
            "recommended_words": recommendations,
            "vocabulary_level": latest_profile.get('resonance_data', {}).get('vocabulary_level', 'beginner')
        }
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}/submissions")
async def get_student_submissions(student_id: str, limit: int = 50):
    """Get submission history for a student"""
    try:
        submissions = await db_submissions.get_student_submissions(student_id, limit)
        return {"submissions": submissions}
    except Exception as e:
        logger.error(f"Error fetching submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

