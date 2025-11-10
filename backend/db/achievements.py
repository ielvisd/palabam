"""
Database operations for Achievements
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from uuid import uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

ACHIEVEMENT_TYPES = [
    'first_story',
    'consistent_writer',
    'word_explorer',
    'vocabulary_master',
    'creative_thinker',
    'streak_7',
    'streak_30',
    'words_1000',
    'words_5000'
]

async def check_and_award_achievements(student_id: str) -> List[Dict[str, Any]]:
    """
    Check student progress and award new achievements
    
    Returns:
        List of newly awarded achievements
    """
    try:
        from .student_progress import get_progress
        
        progress = await get_progress(student_id)
        if not progress:
            return []
        
        newly_awarded = []
        
        # Check various achievement conditions
        submission_count = progress.get("submission_count", 0)
        total_words = progress.get("total_words_written", 0)
        current_streak = progress.get("current_streak", 0)
        vocabulary_level = progress.get("vocabulary_level", "beginner")
        
        # First story
        if submission_count >= 1:
            achievement = await award_achievement(student_id, "first_story")
            if achievement:
                newly_awarded.append(achievement)
        
        # Streak achievements
        if current_streak >= 7:
            achievement = await award_achievement(student_id, "streak_7")
            if achievement:
                newly_awarded.append(achievement)
        
        if current_streak >= 30:
            achievement = await award_achievement(student_id, "streak_30")
            if achievement:
                newly_awarded.append(achievement)
        
        # Word count achievements
        if total_words >= 1000:
            achievement = await award_achievement(student_id, "words_1000")
            if achievement:
                newly_awarded.append(achievement)
        
        if total_words >= 5000:
            achievement = await award_achievement(student_id, "words_5000")
            if achievement:
                newly_awarded.append(achievement)
        
        # Vocabulary level achievement
        if vocabulary_level == "advanced":
            achievement = await award_achievement(student_id, "vocabulary_master")
            if achievement:
                newly_awarded.append(achievement)
        
        # Consistent writer (7-day streak)
        if current_streak >= 7:
            achievement = await award_achievement(student_id, "consistent_writer")
            if achievement:
                newly_awarded.append(achievement)
        
        return newly_awarded
        
    except Exception as e:
        logger.error(f"Error checking achievements for student {student_id}: {e}")
        return []

async def award_achievement(student_id: str, achievement_type: str) -> Optional[Dict[str, Any]]:
    """
    Award an achievement to a student (if not already awarded)
    
    Returns:
        Achievement data if newly awarded, None if already exists
    """
    try:
        supabase = get_supabase_client()
        
        # Check if already awarded
        existing = supabase.table("achievements").select("*").eq("student_id", student_id).eq("achievement_type", achievement_type).execute()
        if existing.data:
            return None  # Already awarded
        
        # Award new achievement
        achievement_data = {
            "id": str(uuid4()),
            "student_id": student_id,
            "achievement_type": achievement_type,
            "earned_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("achievements").insert(achievement_data).execute()
        
        if result.data:
            logger.info(f"Awarded {achievement_type} to student {student_id}")
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Error awarding achievement: {e}")
        return None

async def get_student_achievements(student_id: str) -> List[Dict[str, Any]]:
    """Get all achievements for a student"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("achievements").select("*").eq("student_id", student_id).order("earned_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching achievements for student {student_id}: {e}")
        return []

async def has_achievement(student_id: str, achievement_type: str) -> bool:
    """Check if student has a specific achievement"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("achievements").select("id").eq("student_id", student_id).eq("achievement_type", achievement_type).execute()
        return bool(result.data)
    except Exception as e:
        logger.error(f"Error checking achievement: {e}")
        return False

