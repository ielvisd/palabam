"""
Database operations for Relic Resonance Profiles
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from uuid import UUID, uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def create_profile(
    student_id: str,
    resonance_data: Dict[str, Any],
    word_scores: Dict[str, Any],
    transcript: Optional[str] = None,
    vocabulary_level: Optional[str] = None,
    recommended_words: Optional[list] = None
) -> str:
    """
    Create a new relic resonance profile in the database
    
    Args:
        student_id: UUID of the student
        resonance_data: Profile resonance metadata
        word_scores: Word difficulty scores
        transcript: Original transcript text (optional)
        vocabulary_level: Overall vocabulary level (optional)
        recommended_words: List of recommended words (optional)
        
    Returns:
        Profile ID (UUID as string)
    """
    try:
        supabase = get_supabase_client()
        
        profile_data = {
            "id": str(uuid4()),
            "student_id": student_id,
            "resonance_data": resonance_data,
            "word_scores": word_scores,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if transcript is not None:
            profile_data["transcript"] = transcript
        if vocabulary_level is not None:
            profile_data["vocabulary_level"] = vocabulary_level
        if recommended_words is not None:
            profile_data["recommended_words"] = recommended_words
        
        result = supabase.table("profiles").insert(profile_data).execute()
        
        if result.data:
            profile_id = result.data[0]["id"]
            logger.info(f"Created profile {profile_id} for student {student_id}")
            return profile_id
        else:
            raise Exception("Failed to create profile: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise

async def get_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    """Get a profile by ID"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("profiles").select("*").eq("id", profile_id).single().execute()
        return result.data if result.data else None
    except Exception as e:
        logger.error(f"Error fetching profile {profile_id}: {e}")
        return None

async def get_student_profiles(student_id: str) -> list[Dict[str, Any]]:
    """Get all profiles for a student"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("profiles").select("*").eq("student_id", student_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching profiles for student {student_id}: {e}")
        return []

async def update_profile(
    profile_id: str,
    resonance_data: Optional[Dict[str, Any]] = None,
    word_scores: Optional[Dict[str, Any]] = None
) -> bool:
    """Update an existing profile"""
    try:
        supabase = get_supabase_client()
        
        update_data = {
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if resonance_data is not None:
            update_data["resonance_data"] = resonance_data
        if word_scores is not None:
            update_data["word_scores"] = word_scores
        
        result = supabase.table("profiles").update(update_data).eq("id", profile_id).execute()
        
        if result.data:
            logger.info(f"Updated profile {profile_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {e}")
        return False

