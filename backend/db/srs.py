"""
Database operations for Spaced Repetition System (SRS)
"""
from typing import Dict, Any, Optional, List
from datetime import date, datetime
import logging
from uuid import uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def get_srs_progress(
    student_id: str,
    word_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get SRS progress for a student and word
    
    Args:
        student_id: UUID of the student
        word_id: UUID of the word (optional, if None returns all for student)
        
    Returns:
        SRS progress record(s)
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("srs_progress").select("*").eq("student_id", student_id)
        
        if word_id:
            query = query.eq("word_id", word_id).maybe_single()
            result = query.execute()
            return result.data if result.data else None
        else:
            result = query.execute()
            return result.data if result.data else []
            
    except Exception as e:
        logger.error(f"Error fetching SRS progress: {e}")
        return None if word_id else []

async def create_srs_progress(
    student_id: str,
    word_id: str,
    ease_factor: float = 2.5,
    interval: int = 1,
    repetitions: int = 0,
    due_date: Optional[date] = None
) -> str:
    """
    Create new SRS progress record
    
    Returns:
        SRS progress ID
    """
    try:
        supabase = get_supabase_client()
        
        if due_date is None:
            due_date = date.today()
        
        srs_data = {
            "id": str(uuid4()),
            "student_id": student_id,
            "word_id": word_id,
            "ease_factor": ease_factor,
            "interval": interval,
            "repetitions": repetitions,
            "due_date": due_date.isoformat(),
            "last_reviewed": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("srs_progress").insert(srs_data).execute()
        
        if result.data:
            srs_id = result.data[0]["id"]
            logger.info(f"Created SRS progress {srs_id} for student {student_id}, word {word_id}")
            return srs_id
        else:
            raise Exception("Failed to create SRS progress: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating SRS progress: {e}")
        raise

async def update_srs_progress(
    student_id: str,
    word_id: str,
    ease_factor: float,
    interval: int,
    repetitions: int,
    due_date: date,
    last_reviewed: Optional[datetime] = None
) -> bool:
    """
    Update existing SRS progress record
    """
    try:
        supabase = get_supabase_client()
        
        if last_reviewed is None:
            last_reviewed = datetime.utcnow()
        
        update_data = {
            "ease_factor": ease_factor,
            "interval": interval,
            "repetitions": repetitions,
            "due_date": due_date.isoformat(),
            "last_reviewed": last_reviewed.isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("srs_progress").update(update_data).eq("student_id", student_id).eq("word_id", word_id).execute()
        
        if result.data:
            logger.info(f"Updated SRS progress for student {student_id}, word {word_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error updating SRS progress: {e}")
        return False

async def get_due_words_for_student(
    student_id: str,
    today: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Get all SRS records for a student, including word data
    Returns records with word information joined
    """
    try:
        supabase = get_supabase_client()
        
        if today is None:
            today = date.today()
        
        # Get SRS progress with word data
        result = supabase.table("srs_progress").select(
            "*, words(*)"
        ).eq("student_id", student_id).execute()
        
        if not result.data:
            return []
        
        # Filter and format results
        records = []
        for record in result.data:
            # Convert due_date string to date for comparison
            due_date_str = record.get("due_date")
            if due_date_str:
                due_date = date.fromisoformat(due_date_str)
                record["due_date_obj"] = due_date
                records.append(record)
        
        return records
        
    except Exception as e:
        logger.error(f"Error fetching due words: {e}")
        return []

async def upsert_srs_progress(
    student_id: str,
    word_id: str,
    ease_factor: float,
    interval: int,
    repetitions: int,
    due_date: date,
    last_reviewed: Optional[datetime] = None
) -> bool:
    """
    Upsert (insert or update) SRS progress
    """
    try:
        # Check if record exists
        existing = await get_srs_progress(student_id, word_id)
        
        if existing:
            # Update existing
            return await update_srs_progress(
                student_id=student_id,
                word_id=word_id,
                ease_factor=ease_factor,
                interval=interval,
                repetitions=repetitions,
                due_date=due_date,
                last_reviewed=last_reviewed
            )
        else:
            # Create new
            await create_srs_progress(
                student_id=student_id,
                word_id=word_id,
                ease_factor=ease_factor,
                interval=interval,
                repetitions=repetitions,
                due_date=due_date
            )
            return True
            
    except Exception as e:
        logger.error(f"Error upserting SRS progress: {e}")
        return False

