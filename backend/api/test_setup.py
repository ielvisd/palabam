"""
Test Setup Endpoint
Creates test data for API testing (development only)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
from db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()

class TestSetupResponse(BaseModel):
    success: bool
    teacher_id: str
    student_id: str
    message: str

@router.post("/setup", response_model=TestSetupResponse)
async def setup_test_data():
    """
    Create test teacher and student for API testing
    WARNING: This bypasses normal auth flow - for testing only!
    """
    try:
        supabase = get_supabase_client()
        
        # Use known UUIDs for test data
        teacher_id = "22222222-2222-2222-2222-222222222222"
        student_id = "44444444-4444-4444-4444-444444444444"
        
        # Try to create test teacher (will fail if foreign key constraint, but that's OK)
        # We'll just try to use existing or create if possible
        try:
            # Check if teacher exists
            teacher_check = supabase.table("teachers").select("id").eq("id", teacher_id).execute()
            if not teacher_check.data:
                # Try to create (will likely fail due to foreign key, but worth trying)
                try:
                    supabase.table("teachers").insert({
                        "id": teacher_id,
                        "user_id": teacher_id,  # Self-reference for testing
                        "name": "Test Teacher"
                    }).execute()
                except Exception as e:
                    logger.warning(f"Could not create test teacher: {e}")
                    # Continue anyway - test might work if teacher already exists from manual setup
        except Exception as e:
            logger.warning(f"Error checking teacher: {e}")
        
        # Same for student
        try:
            student_check = supabase.table("students").select("id").eq("id", student_id).execute()
            if not student_check.data:
                try:
                    supabase.table("students").insert({
                        "id": student_id,
                        "user_id": student_id,
                        "name": "Test Student"
                    }).execute()
                except Exception as e:
                    logger.warning(f"Could not create test student: {e}")
        except Exception as e:
            logger.warning(f"Error checking student: {e}")
        
        return TestSetupResponse(
            success=True,
            teacher_id=teacher_id,
            student_id=student_id,
            message="Test data setup attempted. Note: Foreign key constraints may prevent creation. Use Supabase Auth to create proper users."
        )
        
    except Exception as e:
        logger.error(f"Error in test setup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


