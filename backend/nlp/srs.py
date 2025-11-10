"""
Spaced Repetition System (SRS)
Implements SM-2 algorithm for vocabulary retention
"""
from datetime import date, timedelta, datetime
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SRSData:
    """SRS data structure for a word"""
    ease_factor: float = 2.5
    interval: int = 1  # days
    repetitions: int = 0
    due_date: date = None
    last_reviewed: Optional[date] = None
    
    def __post_init__(self):
        if self.due_date is None:
            self.due_date = date.today()

class SM2Algorithm:
    """
    SuperMemo 2 Algorithm Implementation
    Based on: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
    """
    
    @staticmethod
    def calculate_next_review(
        current_data: SRSData,
        quality: int  # 0-5 scale (0=complete blackout, 5=perfect response)
    ) -> SRSData:
        """
        Calculate next review date and update SRS parameters
        
        Quality scale:
        0 - Complete blackout
        1 - Incorrect response, but correct one remembered
        2 - Incorrect response, correct one easy to recall
        3 - Correct response with serious difficulty
        4 - Correct response after hesitation
        5 - Perfect response
        
        Args:
            current_data: Current SRS data for the word
            quality: Quality of recall (0-5)
            
        Returns:
            Updated SRS data
        """
        # Clamp quality to valid range
        quality = max(0, min(5, quality))
        
        # Update ease factor
        if quality < 3:
            # Failed recall - reset repetitions but keep ease factor
            new_ease_factor = current_data.ease_factor
            new_repetitions = 0
            new_interval = 1
        else:
            # Successful recall
            new_ease_factor = current_data.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            new_ease_factor = max(1.3, new_ease_factor)  # Minimum ease factor
            
            if current_data.repetitions == 0:
                new_interval = 1
            elif current_data.repetitions == 1:
                new_interval = 6
            else:
                new_interval = int(current_data.interval * new_ease_factor)
            
            new_repetitions = current_data.repetitions + 1
        
        # Calculate due date
        new_due_date = date.today() + timedelta(days=new_interval)
        
        return SRSData(
            ease_factor=new_ease_factor,
            interval=new_interval,
            repetitions=new_repetitions,
            due_date=new_due_date,
            last_reviewed=date.today()
        )
    
    @staticmethod
    def get_due_words(
        srs_records: List[Dict[str, Any]],
        new_word_count: int = 4,
        review_count: int = 8
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get words due for review and new words to introduce
        
        Args:
            srs_records: List of SRS records from database
            new_word_count: Number of new words to include
            review_count: Number of review words to include
            
        Returns:
            Dictionary with 'new' and 'review' lists
        """
        today = date.today()
        
        # Separate new words (no SRS data) and words with SRS data
        new_words = []
        words_with_srs = []
        
        for record in srs_records:
            if record.get('repetitions', 0) == 0 and not record.get('last_reviewed'):
                new_words.append(record)
            else:
                words_with_srs.append(record)
        
        # Get words due for review
        due_reviews = [
            record for record in words_with_srs
            if record.get('due_date') and 
            date.fromisoformat(str(record['due_date'])) <= today
        ]
        
        # Sort by due date (most overdue first)
        due_reviews.sort(key=lambda x: x.get('due_date', date.max))
        
        # Get overdue words first, then upcoming
        overdue = [r for r in due_reviews if date.fromisoformat(str(r['due_date'])) < today]
        upcoming = [r for r in due_reviews if date.fromisoformat(str(r['due_date'])) == today]
        
        # Combine: overdue first, then upcoming
        review_words = (overdue + upcoming)[:review_count]
        
        # Get new words
        new_words_selected = new_words[:new_word_count]
        
        return {
            'new': new_words_selected,
            'review': review_words
        }
    
    @staticmethod
    def calculate_mastery_level(srs_data: SRSData) -> float:
        """
        Calculate mastery level (0-1) based on SRS data
        Higher repetitions and ease factor = higher mastery
        """
        if srs_data.repetitions == 0:
            return 0.0
        
        # Base mastery from repetitions (capped at 0.7)
        repetition_score = min(0.7, srs_data.repetitions / 10.0)
        
        # Boost from ease factor (capped at 0.3)
        ease_boost = min(0.3, (srs_data.ease_factor - 1.3) / 2.0)
        
        return min(1.0, repetition_score + ease_boost)

# FastAPI router
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class SRSUpdateRequest(BaseModel):
    student_id: str
    word_id: str
    quality: int  # 0-5

class SRSUpdateResponse(BaseModel):
    ease_factor: float
    interval: int
    repetitions: int
    due_date: str
    mastery_level: float

class DueWordsRequest(BaseModel):
    student_id: str
    new_count: int = 4
    review_count: int = 8

class DueWordsResponse(BaseModel):
    new_words: List[Dict[str, Any]]
    review_words: List[Dict[str, Any]]

@router.post("/update", response_model=SRSUpdateResponse)
async def update_srs(request: SRSUpdateRequest):
    """Update SRS data after a word review"""
    try:
        from db import srs as db_srs
        
        # Fetch current SRS data from database
        existing = await db_srs.get_srs_progress(request.student_id, request.word_id)
        
        if existing:
            # Convert database record to SRSData
            current_data = SRSData(
                ease_factor=existing.get('ease_factor', 2.5),
                interval=existing.get('interval', 1),
                repetitions=existing.get('repetitions', 0),
                due_date=date.fromisoformat(existing.get('due_date', date.today().isoformat())),
                last_reviewed=datetime.fromisoformat(existing['last_reviewed']) if existing.get('last_reviewed') else None
            )
        else:
            # Create new SRS data
            current_data = SRSData()
        
        # Calculate next review
        updated_data = SM2Algorithm.calculate_next_review(current_data, request.quality)
        
        # Calculate mastery
        mastery = SM2Algorithm.calculate_mastery_level(updated_data)
        
        # Save to database
        await db_srs.upsert_srs_progress(
            student_id=request.student_id,
            word_id=request.word_id,
            ease_factor=updated_data.ease_factor,
            interval=updated_data.interval,
            repetitions=updated_data.repetitions,
            due_date=updated_data.due_date,
            last_reviewed=updated_data.last_reviewed
        )
        
        return SRSUpdateResponse(
            ease_factor=updated_data.ease_factor,
            interval=updated_data.interval,
            repetitions=updated_data.repetitions,
            due_date=updated_data.due_date.isoformat(),
            mastery_level=mastery
        )
    except Exception as e:
        logger.error(f"Error updating SRS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/due-words", response_model=DueWordsResponse)
async def get_due_words(request: DueWordsRequest):
    """Get words due for review and new words for session"""
    try:
        from db import srs as db_srs, words as db_words
        
        # Fetch SRS records from database with word data
        srs_records = await db_srs.get_due_words_for_student(request.student_id)
        
        # Format records for SM2 algorithm
        formatted_records = []
        for record in srs_records:
            word_data = record.get('words', {})
            if word_data:
                formatted_records.append({
                    'id': record['word_id'],
                    'word': word_data.get('word', ''),
                    'definition': word_data.get('definition', ''),
                    'example': word_data.get('example'),
                    'relic_type': word_data.get('relic_type', 'echo'),
                    'difficulty_score': word_data.get('difficulty_score', 50),
                    'repetitions': record.get('repetitions', 0),
                    'due_date': record.get('due_date'),
                    'last_reviewed': record.get('last_reviewed')
                })
        
        # Get due words using SM2 algorithm
        due_words = SM2Algorithm.get_due_words(
            formatted_records,
            new_word_count=request.new_count,
            review_count=request.review_count
        )
        
        # If we don't have enough words, get some from the words table
        if len(due_words['new']) < request.new_count:
            # Get words that student hasn't practiced yet
            practiced_word_ids = [r['word_id'] for r in srs_records]
            available_words = await db_words.search_words(
                min_difficulty=30,
                max_difficulty=70,
                limit=request.new_count * 2
            )
            
            # Filter out already practiced words
            new_words = [
                w for w in available_words 
                if w['id'] not in practiced_word_ids
            ][:request.new_count - len(due_words['new'])]
            
            # Add to new words list
            for word in new_words:
                due_words['new'].append({
                    'id': word['id'],
                    'word': word['word'],
                    'definition': word['definition'],
                    'example': word.get('example'),
                    'relic_type': word.get('relic_type', 'echo'),
                    'difficulty_score': word.get('difficulty_score', 50)
                })
        
        return DueWordsResponse(
            new_words=due_words['new'],
            review_words=due_words['review']
        )
    except Exception as e:
        logger.error(f"Error getting due words: {e}")
        raise HTTPException(status_code=500, detail=str(e))

