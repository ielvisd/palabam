"""
Database operations for Student Progress
"""
from typing import Dict, Any, Optional
from datetime import datetime, date
import logging
from uuid import uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def get_or_create_progress(student_id: str) -> Dict[str, Any]:
    """Get student progress or create if doesn't exist"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("student_progress").select("*").eq("student_id", student_id).maybe_single().execute()
        
        if result.data:
            return result.data
        else:
            # Create new progress record
            progress_data = {
                "id": str(uuid4()),
                "student_id": student_id,
                "vocabulary_level": "beginner",
                "total_words_written": 0,
                "submission_count": 0,
                "current_streak": 0,
                "total_points": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("student_progress").insert(progress_data).execute()
            return result.data[0] if result.data else progress_data
            
    except Exception as e:
        logger.error(f"Error getting/creating progress for student {student_id}: {e}")
        raise

async def get_progress(student_id: str) -> Optional[Dict[str, Any]]:
    """Get student progress"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("student_progress").select("*").eq("student_id", student_id).single().execute()
        return result.data if result.data else None
    except Exception as e:
        logger.debug(f"Progress not found for student {student_id}: {e}")
        return None

async def update_progress(
    student_id: str,
    vocabulary_level: Optional[str] = None,
    total_words_written: Optional[int] = None,
    submission_count: Optional[int] = None,
    current_streak: Optional[int] = None,
    last_submission_date: Optional[str] = None,
    total_points: Optional[int] = None
) -> bool:
    """Update student progress"""
    try:
        supabase = get_supabase_client()
        
        update_data = {
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if vocabulary_level is not None:
            update_data["vocabulary_level"] = vocabulary_level
        if total_words_written is not None:
            update_data["total_words_written"] = total_words_written
        if submission_count is not None:
            update_data["submission_count"] = submission_count
        if current_streak is not None:
            update_data["current_streak"] = current_streak
        if last_submission_date is not None:
            update_data["last_submission_date"] = last_submission_date
        if total_points is not None:
            update_data["total_points"] = total_points
        
        result = supabase.table("student_progress").update(update_data).eq("student_id", student_id).execute()
        
        if result.data:
            logger.info(f"Updated progress for student {student_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error updating progress for student {student_id}: {e}")
        return False

async def update_vocabulary_level(student_id: str, level: str) -> bool:
    """Update student's vocabulary level based on profile analysis"""
    return await update_progress(student_id, vocabulary_level=level)

async def add_points(student_id: str, points: int) -> bool:
    """Add points to student's total"""
    try:
        progress = await get_or_create_progress(student_id)
        current_points = progress.get("total_points", 0)
        return await update_progress(student_id, total_points=current_points + points)
    except Exception as e:
        logger.error(f"Error adding points: {e}")
        return False

