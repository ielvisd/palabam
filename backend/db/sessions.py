"""
Database operations for Sessions
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from uuid import uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def create_session(
    student_id: str,
    words_practiced: Optional[List[str]] = None
) -> str:
    """
    Create a new session
    
    Returns:
        Session ID
    """
    try:
        supabase = get_supabase_client()
        
        session_data = {
            "id": str(uuid4()),
            "student_id": student_id,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "activities_completed": [],
            "words_practiced": words_practiced or [],
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("sessions").insert(session_data).execute()
        
        if result.data:
            session_id = result.data[0]["id"]
            logger.info(f"Created session {session_id} for student {student_id}")
            return session_id
        else:
            raise Exception("Failed to create session: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise

async def update_session(
    session_id: str,
    completed: bool = False,
    activities_completed: Optional[List[Dict[str, Any]]] = None,
    words_practiced: Optional[List[str]] = None
) -> bool:
    """Update a session"""
    try:
        supabase = get_supabase_client()
        
        update_data = {}
        
        if completed:
            update_data["completed_at"] = datetime.utcnow().isoformat()
        if activities_completed is not None:
            update_data["activities_completed"] = activities_completed
        if words_practiced is not None:
            update_data["words_practiced"] = words_practiced
        
        result = supabase.table("sessions").update(update_data).eq("id", session_id).execute()
        
        if result.data:
            logger.info(f"Updated session {session_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        return False

async def get_student_sessions(
    student_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get sessions for a student"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("sessions").select("*").eq("student_id", student_id).order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return []

