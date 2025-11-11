"""
API endpoints for Submissions
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from db import submissions as db_submissions
from db.supabase_client import get_supabase_client
from nlp import profiler, recommender
from nlp.transcript_parser import TranscriptParser
from utils.file_parser import extract_text_from_file

logger = logging.getLogger(__name__)

router = APIRouter()

async def _ensure_student_exists(student_id: str):
    """Ensure student exists in database, create if anonymous"""
    try:
        supabase = get_supabase_client()
        
        # Check if student exists
        result = supabase.table("students").select("id").eq("id", student_id).execute()
        
        if result.data:
            return  # Student exists
        
        # Student doesn't exist - create if it's a UUID (could be anonymous)
        # Check if it's a valid UUID format (anonymous students now use UUIDs)
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        is_anonymous = uuid_pattern.match(student_id) and not result.data
        
        if is_anonymous:
            # For anonymous students, we need a user_id that exists in auth.users
            # Use a system user ID for all anonymous students
            # This should be created in the database migrations or manually
            SYSTEM_ANON_USER_ID = "00000000-0000-0000-0000-000000000000"
            
            try:
                # First, ensure the system user exists in users table
                user_check = supabase.table("users").select("id").eq("id", SYSTEM_ANON_USER_ID).execute()
                if not user_check.data:
                    # Try to create system user (may fail if auth.users doesn't have it)
                    try:
                        supabase.table("users").insert({
                            "id": SYSTEM_ANON_USER_ID,
                            "email": "anonymous@palabam.local",
                            "role": "student"
                        }).execute()
                    except Exception as user_err:
                        logger.warning(f"Could not create system user: {user_err}")
                        # Continue anyway - might work if user exists in auth.users
                
                # Create anonymous student with system user_id
                student_data = {
                    "id": student_id,
                    "user_id": SYSTEM_ANON_USER_ID,
                    "name": "Anonymous Student"
                }
                insert_result = supabase.table("students").insert(student_data).execute()
                
                # Verify the student was actually created
                if not insert_result.data:
                    raise Exception("Student insert returned no data")
                
                # Double-check by querying
                verify_result = supabase.table("students").select("id").eq("id", student_id).execute()
                if not verify_result.data:
                    raise Exception(f"Student {student_id} was not created successfully")
                
                logger.info(f"Created anonymous student {student_id}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Could not create anonymous student {student_id}: {error_msg}")
                
                # Check if it's a foreign key constraint error
                if "foreign key" in error_msg.lower() or "violates foreign key" in error_msg.lower():
                    raise HTTPException(
                        status_code=400,
                        detail="Please sign up or join a class to submit stories. Anonymous access requires database setup."
                    )
                else:
                    # Re-raise as HTTPException with full error details for debugging
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error creating student: {error_msg}"
                    )
        else:
            # Not a valid UUID format or not found - check if it's the old format
            if not uuid_pattern.match(student_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid student ID format. Expected UUID, got: {student_id}"
                )
            # Valid UUID but student doesn't exist and not anonymous - error
            raise HTTPException(
                status_code=404,
                detail=f"Student {student_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ensuring student exists: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking student: {str(e)}"
        )

class CreateSubmissionRequest(BaseModel):
    student_id: str
    type: str  # 'story-spark', 'upload', 'teacher-upload'
    content: str
    source: str  # 'voice', 'text', 'file'
    student_speaker_name: Optional[str] = None  # Name of the speaker to analyze (for multi-speaker transcripts)

class SubmissionResponse(BaseModel):
    id: str
    student_id: str
    type: str
    source: str
    word_count: int
    profile_id: Optional[str] = None
    recommended_words: Optional[List[Dict[str, Any]]] = None  # Full recommendation objects
    vocabulary_level: Optional[str] = None
    word_categories: Optional[Dict[str, Any]] = None  # Uses Well, Needs Practice, To Master
    created_at: str

class DetectSpeakersRequest(BaseModel):
    transcript: str

class SpeakerInfo(BaseModel):
    name: str
    text: str
    word_count: int
    preview: str  # First 100 characters

class DetectSpeakersResponse(BaseModel):
    format_detected: str
    speakers: List[SpeakerInfo]

@router.post("/", response_model=SubmissionResponse)
async def create_submission(request: CreateSubmissionRequest):
    """Create a new submission and analyze it"""
    try:
        # Validate input
        if not request.content or len(request.content.strip()) < 25:
            raise HTTPException(
                status_code=400,
                detail="Content must be at least 25 words long. Please provide more text!"
            )
        
        if not request.student_id:
            raise HTTPException(
                status_code=400,
                detail="Student ID is required"
            )
        
        # Ensure student exists (for anonymous students)
        await _ensure_student_exists(request.student_id)
        
        # Verify student exists before proceeding (double-check)
        supabase = get_supabase_client()
        student_check = supabase.table("students").select("id").eq("id", request.student_id).execute()
        if not student_check.data:
            logger.error(f"Student {request.student_id} does not exist after _ensure_student_exists")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create or verify student {request.student_id}. Please try again."
            )
        
        # Parse transcript if multi-speaker, extract student text
        content_to_analyze = request.content
        if request.student_speaker_name:
            # Multi-speaker transcript - extract only student's text
            parser = TranscriptParser()
            parsed_result = parser.parse(request.content)
            content_to_analyze = parser.extract_student_text(parsed_result, request.student_speaker_name)
            
            if not content_to_analyze or len(content_to_analyze.strip()) < 25:
                raise HTTPException(
                    status_code=400,
                    detail=f"Selected speaker '{request.student_speaker_name}' has insufficient text (minimum 25 words required)"
                )
        
        # Count words
        word_count = len(content_to_analyze.split())
        
        if word_count < 25:
            raise HTTPException(
                status_code=400,
                detail=f"Content must be at least 25 words. You have {word_count} words."
            )
        
        # Create submission (store original content, but analyze extracted text)
        submission_id = await db_submissions.create_submission(
            student_id=request.student_id,
            submission_type=request.type,
            content=request.content,  # Store original full transcript
            source=request.source,
            word_count=word_count
        )
        
        # Analyze the submission (using extracted student text)
        profiler_instance = profiler.StoryProfiler()
        analysis = profiler_instance.analyze_transcript(content_to_analyze)
        
        # Create profile
        from db import profiles as db_profiles
        profile_id = await db_profiles.create_profile(
            student_id=request.student_id,
            resonance_data=analysis['resonance_data'],
            word_scores=analysis['word_scores']
        )
        
        # Link submission to profile
        await db_submissions.update_submission_profile(submission_id, profile_id)
        
        # Get recommendations with personalization
        recommender_instance = recommender.WordRecommender()
        recommendations = await recommender_instance.recommend_words(
            profile={
                'word_scores': analysis['word_scores'],
                'resonance_data': analysis['resonance_data']
            },
            count=7
        )
        # Return full recommendation objects with rationale
        # Each recommendation now includes: word, definition, example, difficulty_score, 
        # relic_type, rationale (why it was recommended), personalization_score
        recommended_words = recommendations
        
        # Store recommendations in database
        from db import recommendations as db_recommendations
        await db_recommendations.create_recommendations_batch(
            student_id=request.student_id,
            profile_id=profile_id,
            recommendations=recommendations
        )
        
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
            created_at=submission_data['created_at'] if submission_data else "",
            word_categories=analysis.get('word_categories', {})  # Include word categories
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

@router.post("/detect-speakers", response_model=DetectSpeakersResponse)
async def detect_speakers(request: DetectSpeakersRequest):
    """Detect speakers in a transcript and return their information"""
    try:
        if not request.transcript or not request.transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcript cannot be empty"
            )
        
        # Check word count
        word_count = len(request.transcript.strip().split())
        if word_count < 25:
            raise HTTPException(
                status_code=400,
                detail=f"Transcript must be at least 25 words long. You have {word_count} words."
            )
        
        # Parse transcript
        parser = TranscriptParser()
        parsed_result = parser.parse(request.transcript)
        
        # Format response with previews
        speakers_info = []
        for speaker in parsed_result.get('speakers', []):
            text = speaker.get('text', '')
            preview = text[:100] + '...' if len(text) > 100 else text
            
            speakers_info.append(SpeakerInfo(
                name=speaker.get('name', 'Unknown'),
                text=text,
                word_count=speaker.get('word_count', 0),
                preview=preview
            ))
        
        return DetectSpeakersResponse(
            format_detected=parsed_result.get('format_detected', 'plain'),
            speakers=speakers_info
        )
    except Exception as e:
        logger.error(f"Error detecting speakers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-text")
async def extract_text_from_uploaded_file(
    file: UploadFile = File(...)
):
    """Extract text from an uploaded file without creating a submission"""
    try:
        # Validate file type
        filename = file.filename or ""
        allowed_extensions = ['.txt', '.md', '.pdf', '.docx']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Extract text using file parser
        try:
            text_content = extract_text_from_file(content, filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from file: {str(e)}"
            )
        
        if not text_content or not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="File appears to be empty or contains no extractable text"
            )
        
        word_count = len(text_content.split())
        
        return {
            "text": text_content,
            "filename": filename,
            "word_count": word_count,
            "char_count": len(text_content)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file_for_student(
    student_id: str,
    file: UploadFile = File(...)
):
    """Upload a file (essay/document) for a student"""
    try:
        # Validate file type
        filename = file.filename or ""
        allowed_extensions = ['.txt', '.md', '.pdf', '.docx']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Extract text using file parser
        try:
            text_content = extract_text_from_file(content, filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from file: {str(e)}"
            )
        
        if not text_content or len(text_content.strip()) < 25:
            word_count = len(text_content.split()) if text_content else 0
            raise HTTPException(
                status_code=400,
                detail=f"File content must be at least 25 words. You have {word_count} words."
            )
        
        # Create submission
        word_count = len(text_content.split())
        submission_id = await db_submissions.create_submission(
            student_id=student_id,
            submission_type="upload",
            content=text_content,
            source="file",
            word_count=word_count
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
        # Return full recommendation objects (not just words)
        recommended_words = recommendations
        
        # Store recommendations in database
        from db import recommendations as db_recommendations
        await db_recommendations.create_recommendations_batch(
            student_id=student_id,
            profile_id=profile_id,
            recommendations=recommendations
        )
        
        return {
            "submission_id": submission_id,
            "profile_id": profile_id,
            "recommended_words": recommended_words,
            "vocabulary_level": analysis['vocabulary_level']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

