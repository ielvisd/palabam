"""
API endpoints for Parent operations
Allows parents to view their children's progress and data
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import logging

from db import student_progress as db_progress
from db import achievements as db_achievements
from db import submissions as db_submissions
from db import profiles as db_profiles
from db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()

class ChildInfo(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    student_id: str

class ParentChildrenResponse(BaseModel):
    children: List[ChildInfo]

class LinkStudentRequest(BaseModel):
    student_email: str

class LinkStudentResponse(BaseModel):
    success: bool
    message: str

@router.get("/me")
async def get_parent_profile(authorization: Optional[str] = Header(None)):
    """Get current parent's profile"""
    try:
        # Extract user ID from authorization header
        # In production, this should use proper JWT validation
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # For now, we'll get parent from Supabase client
        # In production, validate JWT token and extract user_id
        supabase = get_supabase_client()
        
        # This is a placeholder - in production, extract user_id from JWT
        # For now, we'll need to pass parent_id as a query param or use proper auth
        raise HTTPException(status_code=501, detail="Authentication not yet implemented in backend")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching parent profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/children")
async def get_parent_children(authorization: Optional[str] = Header(None)):
    """Get all children linked to the current parent"""
    try:
        # Extract user ID from authorization header
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # This endpoint should be called from frontend with proper auth
        # The frontend will handle auth and call Supabase directly
        # Backend endpoint is here for future use if needed
        raise HTTPException(status_code=501, detail="Use frontend Supabase client for now")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching parent children: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/children/link")
async def link_student_to_parent(
    request: LinkStudentRequest,
    authorization: Optional[str] = Header(None)
):
    """Link a student to the current parent via student email"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # This endpoint should be called from frontend with proper auth
        # The frontend will handle auth and call Supabase directly
        raise HTTPException(status_code=501, detail="Use frontend Supabase client for now")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking student: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/children/{student_id}/progress")
async def get_child_progress(
    student_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get a child's progress (parent access)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # Verify parent has access to this student via RLS
        # For now, RLS policies handle this, so we can just fetch progress
        progress = await db_progress.get_or_create_progress(student_id)
        return progress
    except Exception as e:
        logger.error(f"Error fetching child progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/children/{student_id}/submissions")
async def get_child_submissions(
    student_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get a child's submissions (parent access)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # RLS policies handle access control
        submissions = await db_submissions.get_student_submissions(student_id)
        return {"submissions": submissions}
    except Exception as e:
        logger.error(f"Error fetching child submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/children/{student_id}/achievements")
async def get_child_achievements(
    student_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get a child's achievements (parent access)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # RLS policies handle access control
        achievements = await db_achievements.get_student_achievements(student_id)
        return {"achievements": achievements}
    except Exception as e:
        logger.error(f"Error fetching child achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/children/{student_id}/sessions")
async def get_child_sessions(
    student_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get a child's sessions (parent access)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        
        # Fetch sessions from database
        supabase = get_supabase_client()
        result = supabase.table("sessions").select("*").eq("student_id", student_id).order("created_at", desc=True).execute()
        
        return {"sessions": result.data if result.data else []}
    except Exception as e:
        logger.error(f"Error fetching child sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

