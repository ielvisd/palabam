"""
API endpoints for Classes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from db import classes as db_classes

logger = logging.getLogger(__name__)

router = APIRouter()

class CreateClassRequest(BaseModel):
    teacher_id: str
    name: str

class CreateClassResponse(BaseModel):
    id: str
    teacher_id: str
    name: str
    code: str
    created_at: str

class JoinClassRequest(BaseModel):
    code: str
    student_id: str
    student_name: str  # For creating student if doesn't exist

class JoinClassResponse(BaseModel):
    success: bool
    class_id: str
    class_name: str
    message: str

@router.post("/", response_model=CreateClassResponse)
async def create_class(request: CreateClassRequest):
    """Create a new class and generate a unique code"""
    try:
        class_data = await db_classes.create_class(
            teacher_id=request.teacher_id,
            name=request.name
        )
        return CreateClassResponse(**class_data)
    except Exception as e:
        logger.error(f"Error creating class: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/code/{code}")
async def get_class_by_code(code: str):
    """Get class information by code (for validation)"""
    try:
        class_data = await db_classes.get_class_by_code(code.upper())
        if not class_data:
            raise HTTPException(status_code=404, detail="Class not found")
        return class_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching class: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join", response_model=JoinClassResponse)
async def join_class(request: JoinClassRequest):
    """Student joins a class using a code"""
    try:
        # Get class by code
        class_data = await db_classes.get_class_by_code(request.code.upper())
        if not class_data:
            raise HTTPException(status_code=404, detail="Invalid class code")
        
        # TODO: Create student if doesn't exist (simplified for now)
        # In production, this would handle student creation/authentication
        
        # Join class
        success = await db_classes.join_class(class_data["id"], request.student_id)
        
        if success:
            return JoinClassResponse(
                success=True,
                class_id=class_data["id"],
                class_name=class_data["name"],
                message="Successfully joined class"
            )
        else:
            return JoinClassResponse(
                success=False,
                class_id=class_data["id"],
                class_name=class_data["name"],
                message="Already a member of this class"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining class: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/{teacher_id}")
async def get_teacher_classes(teacher_id: str):
    """Get all classes for a teacher"""
    try:
        classes = await db_classes.get_teacher_classes(teacher_id)
        return {"classes": classes}
    except Exception as e:
        logger.error(f"Error fetching teacher classes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}")
async def get_student_classes(student_id: str):
    """Get all classes a student is enrolled in"""
    try:
        classes = await db_classes.get_student_classes(student_id)
        return {"classes": classes}
    except Exception as e:
        logger.error(f"Error fetching student classes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{class_id}/students")
async def get_class_students(class_id: str):
    """Get all students in a class"""
    try:
        students = await db_classes.get_class_students(class_id)
        return {"students": students}
    except Exception as e:
        logger.error(f"Error fetching class students: {e}")
        raise HTTPException(status_code=500, detail=str(e))

