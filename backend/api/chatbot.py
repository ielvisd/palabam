"""
Chatbot API for generating age-appropriate conversation transcripts
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

# Try to import OpenAI (optional dependency)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Chatbot generation will be unavailable.")

# Try to import Anthropic (optional dependency)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic package not installed. Claude generation will be unavailable.")


class GenerateConversationRequest(BaseModel):
    topic: str
    grade_level: str  # e.g., "6-7", "4-5"
    conversation_length: str = "medium"  # "short", "medium", "long"
    student_role: Optional[str] = None  # e.g., "student asking questions", "student explaining"
    provider: str = "openai"  # "openai" or "anthropic"


class GenerateConversationResponse(BaseModel):
    transcript: str
    format: str  # "labeled" or "plain"
    word_count: int
    provider_used: str


def _get_grade_level_context(grade_level: str) -> str:
    """Get context description for grade level"""
    grade_contexts = {
        'K-1': 'kindergarten to first grade (ages 5-7), simple sentences, basic vocabulary',
        '2-3': 'second to third grade (ages 7-9), developing vocabulary, simple explanations',
        '4-5': 'fourth to fifth grade (ages 9-11), expanding vocabulary, more complex ideas',
        '6-7': 'sixth to seventh grade (ages 11-13), middle school vocabulary, analytical thinking',
        '8-9': 'eighth to ninth grade (ages 13-15), high school vocabulary, abstract concepts',
        '10-11': 'tenth to eleventh grade (ages 15-17), advanced vocabulary, complex reasoning',
        '12+': 'twelfth grade and above (ages 17+), sophisticated vocabulary, nuanced expression'
    }
    return grade_contexts.get(grade_level, 'middle school level (ages 11-13)')


def _get_conversation_length_turns(length: str) -> int:
    """Convert length string to number of conversation turns"""
    length_map = {
        'short': 8,  # 4 exchanges
        'medium': 16,  # 8 exchanges
        'long': 24  # 12 exchanges
    }
    return length_map.get(length, 16)


def _generate_with_openai(
    topic: str,
    grade_level: str,
    num_turns: int,
    student_role: Optional[str]
) -> str:
    """Generate conversation using OpenAI"""
    if not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="OpenAI package not installed. Please install with: pip install openai"
        )
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured in environment variables"
        )
    
    client = openai.OpenAI(api_key=api_key)
    
    grade_context = _get_grade_level_context(grade_level)
    role_description = student_role or "a curious student asking questions and engaging in discussion"
    
    system_prompt = f"""You are a helpful teacher having a natural conversation with a {grade_level} grade student about {topic}.

The student is {role_description}. The conversation should:
- Use age-appropriate vocabulary for {grade_context}
- Be natural and engaging, like a real classroom conversation
- Include {num_turns} total turns (back-and-forth exchanges)
- Show the student using vocabulary appropriate for their grade level
- Format as: "Teacher: [text]" and "Student: [text]" on separate lines

Generate a realistic conversation transcript."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a conversation about {topic} for a {grade_level} grade student."}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        transcript = response.choices[0].message.content.strip()
        return transcript
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate conversation with OpenAI: {str(e)}"
        )


def _generate_with_anthropic(
    topic: str,
    grade_level: str,
    num_turns: int,
    student_role: Optional[str]
) -> str:
    """Generate conversation using Anthropic Claude"""
    if not ANTHROPIC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Anthropic package not installed. Please install with: pip install anthropic"
        )
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY not configured in environment variables"
        )
    
    client = anthropic.Anthropic(api_key=api_key)
    
    grade_context = _get_grade_level_context(grade_level)
    role_description = student_role or "a curious student asking questions and engaging in discussion"
    
    prompt = f"""You are a helpful teacher having a natural conversation with a {grade_level} grade student about {topic}.

The student is {role_description}. The conversation should:
- Use age-appropriate vocabulary for {grade_context}
- Be natural and engaging, like a real classroom conversation
- Include {num_turns} total turns (back-and-forth exchanges)
- Show the student using vocabulary appropriate for their grade level
- Format as: "Teacher: [text]" and "Student: [text]" on separate lines

Generate a realistic conversation transcript about {topic}."""

    try:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        transcript = message.content[0].text.strip()
        return transcript
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate conversation with Anthropic: {str(e)}"
        )


@router.post("/generate", response_model=GenerateConversationResponse)
async def generate_conversation(request: GenerateConversationRequest):
    """Generate an age-appropriate conversation transcript"""
    try:
        # Validate inputs
        if not request.topic or len(request.topic.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Topic must be at least 3 characters long"
            )
        
        valid_grades = ['K-1', '2-3', '4-5', '6-7', '8-9', '10-11', '12+']
        if request.grade_level not in valid_grades:
            raise HTTPException(
                status_code=400,
                detail=f"Grade level must be one of: {', '.join(valid_grades)}"
            )
        
        # Get number of turns
        num_turns = _get_conversation_length_turns(request.conversation_length)
        
        # Generate conversation
        if request.provider == "openai":
            transcript = _generate_with_openai(
                request.topic,
                request.grade_level,
                num_turns,
                request.student_role
            )
            provider_used = "openai"
        elif request.provider == "anthropic":
            transcript = _generate_with_anthropic(
                request.topic,
                request.grade_level,
                num_turns,
                request.student_role
            )
            provider_used = "anthropic"
        else:
            raise HTTPException(
                status_code=400,
                detail="Provider must be 'openai' or 'anthropic'"
            )
        
        # Determine format
        format_detected = "labeled" if ("Teacher:" in transcript or "Student:" in transcript) else "plain"
        
        # Count words
        word_count = len(transcript.split())
        
        return GenerateConversationResponse(
            transcript=transcript,
            format=format_detected,
            word_count=word_count,
            provider_used=provider_used
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate conversation: {str(e)}"
        )

