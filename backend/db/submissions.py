"""
Database operations for Submissions
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from uuid import UUID, uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def create_submission(
    student_id: str,
    submission_type: str,
    content: str,
    source: str,
    profile_id: Optional[str] = None,
    word_count: int = 0
) -> str:
    """
    Create a new submission
    
    Args:
        student_id: UUID of the student
        submission_type: 'story-spark', 'upload', or 'teacher-upload'
        content: The transcript or writing sample content
        source: 'voice', 'text', or 'file'
        profile_id: Optional profile ID if already analyzed
        word_count: Number of words in the submission
        
    Returns:
        Submission ID (UUID as string)
    """
    try:
        supabase = get_supabase_client()
        
        submission_data = {
            "id": str(uuid4()),
            "student_id": student_id,
            "type": submission_type,
            "content": content,
            "source": source,
            "profile_id": profile_id,
            "word_count": word_count,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("submissions").insert(submission_data).execute()
        
        if result.data:
            submission_id = result.data[0]["id"]
            logger.info(f"Created submission {submission_id} for student {student_id}")
            
            # Update student progress
            await update_student_progress_from_submission(student_id, word_count)
            
            return submission_id
        else:
            raise Exception("Failed to create submission: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        raise

async def get_submission(submission_id: str) -> Optional[Dict[str, Any]]:
    """Get a submission by ID"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("submissions").select("*").eq("id", submission_id).single().execute()
        return result.data if result.data else None
    except Exception as e:
        logger.error(f"Error fetching submission {submission_id}: {e}")
        return None

async def get_student_submissions(student_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all submissions for a student"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("submissions").select("*").eq("student_id", student_id).order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching submissions for student {student_id}: {e}")
        return []

async def update_submission_profile(submission_id: str, profile_id: str) -> bool:
    """Link a submission to a profile after analysis"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("submissions").update({"profile_id": profile_id}).eq("id", submission_id).execute()
        return bool(result.data)
    except Exception as e:
        logger.error(f"Error updating submission profile: {e}")
        return False

async def update_student_progress_from_submission(student_id: str, word_count: int) -> None:
    """Update student progress when a new submission is created"""
    try:
        # Import here to avoid circular dependency
        from . import student_progress
        
        progress = await student_progress.get_or_create_progress(student_id)
        
        # Calculate new values
        new_word_count = progress.get("total_words_written", 0) + word_count
        new_submission_count = progress.get("submission_count", 0) + 1
        
        # Calculate streak
        last_date = progress.get("last_submission_date")
        today = datetime.utcnow().date()
        current_streak = progress.get("current_streak", 0)
        
        if last_date:
            from datetime import date
            if isinstance(last_date, str):
                try:
                    last_date_obj = datetime.fromisoformat(last_date.replace('Z', '+00:00')).date()
                except:
                    last_date_obj = datetime.strptime(last_date, '%Y-%m-%d').date()
            else:
                last_date_obj = last_date
            
            days_diff = (today - last_date_obj).days
            
            if days_diff == 1:
                # Consecutive day
                new_streak = current_streak + 1
            elif days_diff == 0:
                # Same day, don't increment streak
                new_streak = current_streak
            else:
                # Streak broken
                new_streak = 1
        else:
            # First submission
            new_streak = 1
        
        await student_progress.update_progress(
            student_id,
            total_words_written=new_word_count,
            submission_count=new_submission_count,
            current_streak=new_streak,
            last_submission_date=today.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error updating student progress: {e}")

