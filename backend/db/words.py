"""
Database operations for Vocabulary Words
"""
from typing import Dict, Any, Optional, List
import logging

from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

async def get_word(word: str) -> Optional[Dict[str, Any]]:
    """Get a word by its text"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("words").select("*").eq("word", word.lower()).single().execute()
        return result.data if result.data else None
    except Exception as e:
        logger.debug(f"Word '{word}' not found in database: {e}")
        return None

async def create_word(
    word: str,
    definition: str,
    example: Optional[str] = None,
    relic_type: str = "echo",
    difficulty_score: int = 50,
    coca_frequency: Optional[int] = None,
    lexile_score: Optional[int] = None
) -> str:
    """
    Create a new word in the database
    
    Returns:
        Word ID (UUID as string)
    """
    try:
        supabase = get_supabase_client()
        
        # Check if word already exists
        existing = await get_word(word)
        if existing:
            return existing["id"]
        
        from uuid import uuid4
        
        word_data = {
            "id": str(uuid4()),
            "word": word.lower(),
            "definition": definition,
            "example": example,
            "relic_type": relic_type,
            "difficulty_score": difficulty_score,
            "coca_frequency": coca_frequency,
            "lexile_score": lexile_score
        }
        
        result = supabase.table("words").insert(word_data).execute()
        
        if result.data:
            word_id = result.data[0]["id"]
            logger.info(f"Created word '{word}' with ID {word_id}")
            return word_id
        else:
            raise Exception("Failed to create word: No data returned")
            
    except Exception as e:
        logger.error(f"Error creating word '{word}': {e}")
        raise

async def get_words_by_ids(word_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple words by their IDs"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("words").select("*").in_("id", word_ids).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching words: {e}")
        return []

async def search_words(
    search_term: Optional[str] = None,
    relic_type: Optional[str] = None,
    min_difficulty: Optional[int] = None,
    max_difficulty: Optional[int] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Search for words with filters"""
    try:
        supabase = get_supabase_client()
        query = supabase.table("words").select("*")
        
        if search_term:
            query = query.ilike("word", f"%{search_term}%")
        if relic_type:
            query = query.eq("relic_type", relic_type)
        if min_difficulty is not None:
            query = query.gte("difficulty_score", min_difficulty)
        if max_difficulty is not None:
            query = query.lte("difficulty_score", max_difficulty)
        
        result = query.limit(limit).execute()
        return result.data if result.data else []
        
    except Exception as e:
        logger.error(f"Error searching words: {e}")
        return []

