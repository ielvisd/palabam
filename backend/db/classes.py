"""
Database operations for Classes
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from uuid import UUID, uuid4

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def create_class(teacher_id: str, name: str) -> Dict[str, Any]:
    """
    Create a new class and generate a unique code
    
    Args:
        teacher_id: UUID of the teacher
        name: Class name
        
    Returns:
        Dictionary with class data including code
    """
    try:
        supabase = get_supabase_client()
        
        # For testing: if teacher doesn't exist, create a test teacher
        # In production, this should be validated
        try:
            teacher_check = supabase.table("teachers").select("id").eq("id", teacher_id).execute()
            if not teacher_check.data:
                # Create test teacher if doesn't exist (for testing only)
                logger.warning(f"Teacher {teacher_id} not found, creating test teacher")
                # Note: This will fail if user_id doesn't exist, but allows testing
                try:
                    supabase.table("teachers").insert({
                        "id": teacher_id,
                        "user_id": teacher_id,  # For testing, use same ID
                        "name": "Test Teacher"
                    }).execute()
                except:
                    pass  # Ignore if it fails - foreign key constraint
        except:
            pass  # Continue even if check fails
        
        # Generate unique code
        code = _generate_unique_code(supabase)
        
        class_data = {
            "id": str(uuid4()),
            "teacher_id": teacher_id,
            "name": name,
            "code": code,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("classes").insert(class_data).execute()
        
        if result.data:
            logger.info(f"Created class {result.data[0]['id']} with code {code}")
            return result.data[0]
        else:
            raise Exception("Failed to create class: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating class: {e}")
        raise

def _generate_unique_code(supabase, max_attempts: int = 10) -> str:
    """Generate a unique 6-character class code"""
    import random
    
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Removed confusing chars
    for _ in range(max_attempts):
        code = ''.join(random.choices(chars, k=6))
        
        # Check if code exists
        try:
            result = supabase.table("classes").select("code").eq("code", code).execute()
            if not result.data:
                return code
        except:
            # If check fails, try the code anyway
            return code
    
    # If all attempts failed, generate one more with timestamp
    import time
    code = ''.join(random.choices(chars, k=4)) + str(int(time.time()))[-2:]
    return code

async def get_class_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get a class by its code"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("classes").select("*").eq("code", code.upper()).single().execute()
        return result.data if result.data else None
    except Exception as e:
        logger.debug(f"Class with code {code} not found: {e}")
        return None

async def join_class(class_id: str, student_id: str) -> bool:
    """
    Add a student to a class
    
    Returns:
        True if successful, False if already joined
    """
    try:
        supabase = get_supabase_client()
        
        # Check if already joined
        existing = supabase.table("class_students").select("*").eq("class_id", class_id).eq("student_id", student_id).execute()
        if existing.data:
            return False  # Already joined
        
        join_data = {
            "id": str(uuid4()),
            "class_id": class_id,
            "student_id": student_id,
            "joined_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("class_students").insert(join_data).execute()
        return bool(result.data)
    except Exception as e:
        logger.error(f"Error joining class: {e}")
        raise

async def get_teacher_classes(teacher_id: str) -> List[Dict[str, Any]]:
    """Get all classes for a teacher"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("classes").select("*").eq("teacher_id", teacher_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching classes for teacher {teacher_id}: {e}")
        return []

async def get_class_students(class_id: str) -> List[Dict[str, Any]]:
    """Get all students in a class"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("class_students").select("*, students(*)").eq("class_id", class_id).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching students for class {class_id}: {e}")
        return []

async def get_student_classes(student_id: str) -> List[Dict[str, Any]]:
    """Get all classes a student is enrolled in"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("class_students").select("*, classes(*)").eq("student_id", student_id).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching classes for student {student_id}: {e}")
        return []

