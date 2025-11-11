"""
API endpoints for User Management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()

class CreateUserRequest(BaseModel):
    user_id: str
    email: str
    role: str
    name: Optional[str] = None

@router.post("/ensure")
async def ensure_user_record(request: CreateUserRequest):
    """
    Ensure a user record exists in public.users table.
    This endpoint handles data inconsistencies where auth.users and public.users are out of sync.
    Uses service role to bypass RLS.
    """
    try:
        supabase = get_supabase_client()
        
        # Check if user record exists
        existing = supabase.table("users").select("id, email, role").eq("id", request.user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # User record exists - return it
            logger.info(f"User record already exists for {request.user_id}")
            return {
                "id": existing.data[0]["id"],
                "email": existing.data[0]["email"],
                "role": existing.data[0]["role"],
                "created": False
            }
        
        # Check if there's a record with the same email but different ID (data inconsistency)
        existing_by_email = supabase.table("users").select("id, email, role").eq("email", request.email).execute()
        
        if existing_by_email.data and len(existing_by_email.data) > 0:
            old_id = existing_by_email.data[0]["id"]
            if old_id != request.user_id:
                logger.warning(f"User record exists with different ID ({old_id} vs {request.user_id}) for email {request.email}")
                
                # Since we can't change the primary key, we need to update related records
                # Check if there's a teacher record pointing to the old user_id
                # If so, update it to point to the new user_id (request.user_id)
                try:
                    # Check for teacher record with old user_id
                    teacher_check = supabase.table("teachers").select("id, user_id").eq("user_id", old_id).execute()
                    if teacher_check.data and len(teacher_check.data) > 0:
                        # Update teacher record to use new user_id
                        logger.info(f"Updating {len(teacher_check.data)} teacher record(s) from old user_id {old_id} to new user_id {request.user_id}")
                        update_result = supabase.table("teachers").update({"user_id": request.user_id}).eq("user_id", old_id).execute()
                        logger.info(f"Teacher records updated: {update_result.data if update_result.data else 'no data returned'}")
                    
                    # Check for student record
                    student_check = supabase.table("students").select("id, user_id").eq("user_id", old_id).execute()
                    if student_check.data and len(student_check.data) > 0:
                        logger.info(f"Updating {len(student_check.data)} student record(s) from old user_id {old_id} to new user_id {request.user_id}")
                        update_result = supabase.table("students").update({"user_id": request.user_id}).eq("user_id", old_id).execute()
                        logger.info(f"Student records updated: {update_result.data if update_result.data else 'no data returned'}")
                    
                    # Check for parent record
                    parent_check = supabase.table("parents").select("id, user_id").eq("user_id", old_id).execute()
                    if parent_check.data and len(parent_check.data) > 0:
                        logger.info(f"Updating {len(parent_check.data)} parent record(s) from old user_id {old_id} to new user_id {request.user_id}")
                        update_result = supabase.table("parents").update({"user_id": request.user_id}).eq("user_id", old_id).execute()
                        logger.info(f"Parent records updated: {update_result.data if update_result.data else 'no data returned'}")
                    
                    # Now delete the old user record
                    logger.info(f"Deleting old user record with ID {old_id}")
                    delete_result = supabase.table("users").delete().eq("id", old_id).execute()
                    logger.info(f"Successfully deleted old user record: {delete_result.data if delete_result.data else 'no data returned'}")
                except Exception as update_error:
                    logger.error(f"Error updating related records: {update_error}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Failed to update related records: {str(update_error)}")
        
        # Try to create new user record with correct ID
        new_user = {
            "id": request.user_id,
            "email": request.email,
            "role": request.role
        }
        
        try:
            # Try insert
            result = supabase.table("users").insert(new_user).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created user record for {request.user_id} with role {request.role}")
                return {
                    "id": result.data[0]["id"],
                    "email": result.data[0]["email"],
                    "role": result.data[0]["role"],
                    "created": True
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create user record: No data returned")
        except Exception as insert_error:
            error_msg = str(insert_error)
            # If insert fails, check if it's because the record already exists with correct ID
            if "duplicate" in error_msg.lower() or "unique" in error_msg.lower() or "23505" in error_msg:
                # Check if record exists with correct ID
                existing = supabase.table("users").select("id, email, role").eq("id", request.user_id).execute()
                if existing.data and len(existing.data) > 0:
                    logger.info(f"User record already exists with correct ID {request.user_id}")
                    return {
                        "id": existing.data[0]["id"],
                        "email": existing.data[0]["email"],
                        "role": existing.data[0]["role"],
                        "created": False
                    }
                else:
                    # Record exists with different ID but same email - this should have been handled above
                    logger.error(f"User record conflict: email {request.email} exists but with different ID")
                    raise HTTPException(status_code=500, detail="Failed to create user record: email conflict not resolved")
            else:
                logger.error(f"Error inserting user record: {insert_error}")
                raise HTTPException(status_code=500, detail=f"Failed to create user record: {insert_error}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ensuring user record: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

