"""
Database operations for Recommendations
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from uuid import UUID, uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def create_recommendation(
    student_id: str,
    profile_id: str,
    word: str,
    definition: Optional[str] = None,
    example: Optional[str] = None,
    difficulty_score: Optional[int] = None,
    lexile_score: Optional[int] = None,
    coca_frequency: Optional[int] = None,
    relic_type: Optional[str] = None
) -> str:
    """
    Create a recommendation record in the database
    
    Args:
        student_id: UUID of the student
        profile_id: UUID of the profile this recommendation is based on
        word: The recommended word
        definition: Word definition (optional)
        example: Example sentence (optional)
        difficulty_score: Difficulty score 0-100 (optional)
        lexile_score: Lexile score (optional)
        coca_frequency: COCA frequency (optional)
        relic_type: Relic type (optional)
        
    Returns:
        Recommendation ID (UUID as string)
    """
    try:
        supabase = get_supabase_client()
        
        recommendation_data = {
            "id": str(uuid4()),
            "student_id": student_id,
            "profile_id": profile_id,
            "word": word,
            "status": "pending",
            "recommended_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if definition is not None:
            recommendation_data["definition"] = definition
        if example is not None:
            recommendation_data["example"] = example
        if difficulty_score is not None:
            recommendation_data["difficulty_score"] = difficulty_score
        if lexile_score is not None:
            recommendation_data["lexile_score"] = lexile_score
        if coca_frequency is not None:
            recommendation_data["coca_frequency"] = coca_frequency
        if relic_type is not None:
            recommendation_data["relic_type"] = relic_type
        
        result = supabase.table("recommendations").insert(recommendation_data).execute()
        
        if result.data:
            rec_id = result.data[0]["id"]
            logger.info(f"Created recommendation {rec_id} for student {student_id}, word: {word}")
            return rec_id
        else:
            raise Exception("Failed to create recommendation: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating recommendation: {e}")
        raise

async def create_recommendations_batch(
    student_id: str,
    profile_id: str,
    recommendations: List[Dict[str, Any]]
) -> List[str]:
    """
    Create multiple recommendation records in a batch
    
    Args:
        student_id: UUID of the student
        profile_id: UUID of the profile
        recommendations: List of recommendation dicts with word and metadata
        
    Returns:
        List of recommendation IDs
    """
    try:
        supabase = get_supabase_client()
        
        recommendation_data_list = []
        for rec in recommendations:
            rec_data = {
                "id": str(uuid4()),
                "student_id": student_id,
                "profile_id": profile_id,
                "word": rec.get("word", ""),
                "status": "pending",
                "recommended_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if "definition" in rec:
                rec_data["definition"] = rec["definition"]
            if "example" in rec:
                rec_data["example"] = rec["example"]
            if "difficulty_score" in rec:
                rec_data["difficulty_score"] = rec["difficulty_score"]
            if "lexile_score" in rec:
                rec_data["lexile_score"] = rec["lexile_score"]
            if "coca_frequency" in rec:
                rec_data["coca_frequency"] = rec["coca_frequency"]
            if "relic_type" in rec:
                rec_data["relic_type"] = rec["relic_type"]
            
            recommendation_data_list.append(rec_data)
        
        result = supabase.table("recommendations").insert(recommendation_data_list).execute()
        
        if result.data:
            rec_ids = [r["id"] for r in result.data]
            logger.info(f"Created {len(rec_ids)} recommendations for student {student_id}")
            return rec_ids
        else:
            raise Exception("Failed to create recommendations: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating recommendations batch: {e}")
        raise

async def get_student_recommendations(
    student_id: str,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get recommendations for a student
    
    Args:
        student_id: UUID of the student
        status: Filter by status (pending, mastered, reviewed, dismissed)
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("recommendations").select("*").eq("student_id", student_id)
        
        if status:
            query = query.eq("status", status)
        
        query = query.order("recommended_at", desc=True)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error fetching recommendations for student {student_id}: {e}")
        return []

async def get_profile_recommendations(profile_id: str) -> List[Dict[str, Any]]:
    """
    Get recommendations for a specific profile
    
    Args:
        profile_id: UUID of the profile
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("recommendations").select("*").eq("profile_id", profile_id).order("recommended_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching recommendations for profile {profile_id}: {e}")
        return []

async def update_recommendation_status(
    recommendation_id: str,
    status: str
) -> bool:
    """
    Update the status of a recommendation
    
    Args:
        recommendation_id: UUID of the recommendation
        status: New status (pending, mastered, reviewed, dismissed)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("recommendations").update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", recommendation_id).execute()
        
        return bool(result.data)
    except Exception as e:
        logger.error(f"Error updating recommendation {recommendation_id}: {e}")
        return False

