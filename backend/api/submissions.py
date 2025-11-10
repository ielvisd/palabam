"""
API endpoints for Submissions
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import logging

from db import submissions as db_submissions
from nlp import profiler, recommender

logger = logging.getLogger(__name__)

router = APIRouter()

class CreateSubmissionRequest(BaseModel):
    student_id: str
    type: str  # 'story-spark', 'upload', 'teacher-upload'
    content: str
    source: str  # 'voice', 'text', 'file'

class SubmissionResponse(BaseModel):
    id: str
    student_id: str
    type: str
    source: str
    word_count: int
    profile_id: Optional[str] = None
    recommended_words: Optional[List[str]] = None
    vocabulary_level: Optional[str] = None
    created_at: str

@router.post("/", response_model=SubmissionResponse)
async def create_submission(request: CreateSubmissionRequest):
    """Create a new submission and analyze it"""
    try:
        # Count words
        word_count = len(request.content.split())
        
        # Create submission
        submission_id = await db_submissions.create_submission(
            student_id=request.student_id,
            submission_type=request.type,
            content=request.content,
            source=request.source,
            word_count=word_count
        )
        
        # Analyze the submission
        profiler_instance = profiler.StoryProfiler()
        analysis = profiler_instance.analyze_transcript(request.content)
        
        # Create profile
        from db import profiles as db_profiles
        profile_id = await db_profiles.create_profile(
            student_id=request.student_id,
            resonance_data=analysis['resonance_data'],
            word_scores=analysis['word_scores']
        )
        
        # Link submission to profile
        await db_submissions.update_submission_profile(submission_id, profile_id)
        
        # Get recommendations
        recommender_instance = recommender.WordRecommender()
        recommendations = await recommender_instance.recommend_words(
            profile={
                'word_scores': analysis['word_scores'],
                'resonance_data': analysis['resonance_data']
            },
            count=7
        )
        recommended_words = [r['word'] for r in recommendations]
        
        # Update student vocabulary level
        from db import student_progress as db_progress
        from db import achievements as db_achievements
        
        await db_progress.update_vocabulary_level(
            request.student_id,
            analysis['vocabulary_level']
        )
        
        # Award points (10 points per submission + 5 per 100 words)
        points = 10 + (word_count // 100) * 5
        await db_progress.add_points(request.student_id, points)
        
        # Check for new achievements
        await db_achievements.check_and_award_achievements(request.student_id)
        
        # Get submission data
        submission_data = await db_submissions.get_submission(submission_id)
        
        return SubmissionResponse(
            id=submission_id,
            student_id=request.student_id,
            type=request.type,
            source=request.source,
            word_count=word_count,
            profile_id=profile_id,
            recommended_words=recommended_words,
            vocabulary_level=analysis['vocabulary_level'],
            created_at=submission_data['created_at'] if submission_data else ""
        )
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}")
async def get_student_submissions(student_id: str, limit: int = 50):
    """Get all submissions for a student"""
    try:
        submissions = await db_submissions.get_student_submissions(student_id, limit)
        return {"submissions": submissions}
    except Exception as e:
        logger.error(f"Error fetching submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file_for_student(
    student_id: str,
    file: UploadFile = File(...)
):
    """Upload a file (essay/document) for a student"""
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Create submission
        submission_id = await db_submissions.create_submission(
            student_id=student_id,
            submission_type="upload",
            content=text_content,
            source="file",
            word_count=len(text_content.split())
        )
        
        # Analyze (same as create_submission)
        profiler_instance = profiler.StoryProfiler()
        analysis = profiler_instance.analyze_transcript(text_content)
        
        from db import profiles as db_profiles
        profile_id = await db_profiles.create_profile(
            student_id=student_id,
            resonance_data=analysis['resonance_data'],
            word_scores=analysis['word_scores']
        )
        
        await db_submissions.update_submission_profile(submission_id, profile_id)
        
        recommender_instance = recommender.WordRecommender()
        recommendations = await recommender_instance.recommend_words(
            profile={
                'word_scores': analysis['word_scores'],
                'resonance_data': analysis['resonance_data']
            },
            count=7
        )
        recommended_words = [r['word'] for r in recommendations]
        
        return {
            "submission_id": submission_id,
            "profile_id": profile_id,
            "recommended_words": recommended_words,
            "vocabulary_level": analysis['vocabulary_level']
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

