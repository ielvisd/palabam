"""
Invites API endpoints for teacher-student invites
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import string

from db.supabase_client import get_supabase_client

router = APIRouter()


class InviteEmailRequest(BaseModel):
    class_id: str
    email: str
    teacher_id: str


class InviteGenerateRequest(BaseModel):
    class_id: str
    teacher_id: str


class InviteAcceptRequest(BaseModel):
    email: str
    name: str


def generate_invite_code(length: int = 8) -> str:
    """Generate a random invite code"""
    chars = string.ascii_uppercase + string.digits
    # Remove confusing characters
    chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(chars) for _ in range(length))


@router.post("/email")
async def send_invite_email(
    request: InviteEmailRequest,
    supabase=Depends(get_supabase_client)
):
    """
    Send student invite via email
    Creates an invite record and sends email (email sending to be implemented)
    """
    try:
        teacher_id = request.teacher_id
        
        # Verify class belongs to teacher
        class_result = supabase.table("classes").select("id, name").eq("id", request.class_id).eq("teacher_id", teacher_id).single().execute()
        if not class_result.data:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Generate invite code
        code = generate_invite_code()
        
        # Check if code already exists (unlikely but possible)
        while True:
            existing = supabase.table("invites").select("id").eq("code", code).execute()
            if not existing.data:
                break
            code = generate_invite_code()
        
        # Create invite record
        invite_data = {
            "class_id": request.class_id,
            "code": code,
            "teacher_id": teacher_id,
            "email": request.email,
            "status": "pending"
        }
        
        invite_result = supabase.table("invites").insert(invite_data).execute()
        
        if not invite_result.data:
            raise HTTPException(status_code=500, detail="Failed to create invite")
        
        # TODO: Send email with invite link
        # For now, return the invite link
        # Use environment variable or default to localhost for development
        import os
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
        invite_link = f"{base_url}/invite/{code}"
        
        return {
            "success": True,
            "invite_id": invite_result.data[0]["id"],
            "code": code,
            "link": invite_link,
            "message": "Invite created. Email sending to be implemented."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending invite email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_invite_link(
    request: InviteGenerateRequest,
    supabase=Depends(get_supabase_client)
):
    """
    Generate shareable invite link for a class
    """
    try:
        teacher_id = request.teacher_id
        
        # Verify class belongs to teacher
        class_result = supabase.table("classes").select("id, name").eq("id", request.class_id).eq("teacher_id", teacher_id).single().execute()
        if not class_result.data:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check if there's already a pending/reusable invite for this class
        existing_invite = supabase.table("invites").select("*").eq("class_id", request.class_id).eq("email", None).eq("status", "pending").order("created_at", desc=True).limit(1).execute()
        
        if existing_invite.data:
            # Return existing invite
            code = existing_invite.data[0]["code"]
            # Use environment variable or default to localhost for development
            import os
            base_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
            invite_link = f"{base_url}/invite/{code}"
            return {
                "success": True,
                "code": code,
                "link": invite_link,
                "existing": True
            }
        
        # Generate new invite code
        code = generate_invite_code()
        
        # Check if code already exists
        while True:
            existing = supabase.table("invites").select("id").eq("code", code).execute()
            if not existing.data:
                break
            code = generate_invite_code()
        
        # Create invite record (no email, so it's a shareable link)
        invite_data = {
            "class_id": request.class_id,
            "code": code,
            "teacher_id": teacher_id,
            "email": None,
            "status": "pending"
        }
        
        invite_result = supabase.table("invites").insert(invite_data).execute()
        
        if not invite_result.data:
            raise HTTPException(status_code=500, detail="Failed to create invite")
        
        # Use environment variable or default to localhost for development
        import os
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
        invite_link = f"{base_url}/invite/{code}"
        
        return {
            "success": True,
            "code": code,
            "link": invite_link,
            "existing": False
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating invite link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}")
async def get_invite(
    code: str,
    supabase=Depends(get_supabase_client)
):
    """
    Validate invite code and get class info
    Public endpoint - no auth required
    """
    try:
        invite_result = supabase.table("invites").select(
            "id, class_id, status, expires_at, classes(name), teachers(name)"
        ).eq("code", code).single().execute()
        
        if not invite_result.data:
            return {
                "valid": False,
                "message": "Invite code not found"
            }
        
        invite = invite_result.data
        
        # Check if expired
        if invite.get("expires_at"):
            expires_at = datetime.fromisoformat(invite["expires_at"].replace("Z", "+00:00"))
            if datetime.now(expires_at.tzinfo) > expires_at:
                return {
                    "valid": False,
                    "message": "Invite has expired"
                }
        
        # Check status
        if invite["status"] != "pending":
            return {
                "valid": False,
                "message": f"Invite is {invite['status']}"
            }
        
        return {
            "valid": True,
            "class_id": invite["class_id"],
            "class_name": invite["classes"]["name"] if invite.get("classes") else "Unknown Class",
            "teacher_name": invite["teachers"]["name"] if invite.get("teachers") else "Unknown Teacher"
        }
    except Exception as e:
        print(f"Error validating invite: {e}")
        return {
            "valid": False,
            "message": "Error validating invite"
        }


@router.get("")
async def get_invites(
    teacher_id: str,
    supabase=Depends(get_supabase_client)
):
    """
    Get all invites for teacher's classes
    """
    try:
        
        # Get all invites for teacher's classes
        invites_result = supabase.table("invites").select(
            "id, code, class_id, email, status, created_at, expires_at, classes(name)"
        ).eq("teacher_id", teacher_id).order("created_at", desc=True).execute()
        
        return {
            "invites": invites_result.data or []
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting invites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{code}/accept")
async def accept_invite(
    code: str,
    request: InviteAcceptRequest,
    supabase=Depends(get_supabase_client)
):
    """
    Accept invite and create student account
    This is called after the student verifies their email via magic link
    """
    try:
        # Validate invite code
        invite_result = supabase.table("invites").select(
            "id, class_id, status, expires_at"
        ).eq("code", code).single().execute()
        
        if not invite_result.data:
            raise HTTPException(status_code=404, detail="Invite not found")
        
        invite = invite_result.data
        
        # Check if expired
        if invite.get("expires_at"):
            expires_at = datetime.fromisoformat(invite["expires_at"].replace("Z", "+00:00"))
            if datetime.now(expires_at.tzinfo) > expires_at:
                raise HTTPException(status_code=400, detail="Invite has expired")
        
        # Check status
        if invite["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Invite is {invite['status']}")
        
        # Get student by email (student should already be created via auth callback)
        user_result = supabase.table("users").select("id").eq("email", request.email).eq("role", "student").single().execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="Student not found. Please complete signup first.")
        
        user_id = user_result.data["id"]
        
        # Get student record (should exist from auth callback)
        student_result = supabase.table("students").select("id").eq("user_id", user_id).single().execute()
        if not student_result.data:
            raise HTTPException(status_code=404, detail="Student record not found")
        
        student_id = student_result.data["id"]
        
        # Add student to class
        class_student_data = {
            "class_id": invite["class_id"],
            "student_id": student_id
        }
        
        # Check if already in class
        existing = supabase.table("class_students").select("id").eq("class_id", invite["class_id"]).eq("student_id", student_id).execute()
        
        if not existing.data:
            supabase.table("class_students").insert(class_student_data).execute()
        
        # Update invite status
        supabase.table("invites").update({"status": "accepted"}).eq("id", invite["id"]).execute()
        
        return {
            "success": True,
            "message": "Invite accepted and student added to class"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error accepting invite: {e}")
        raise HTTPException(status_code=500, detail=str(e))

