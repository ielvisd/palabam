"""
Transcript Parser
Detects and parses multiple transcript formats to extract speaker information
"""
import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class TranscriptParser:
    """Parses transcripts in multiple formats to extract speaker information"""
    
    # Common speaker label patterns
    SPEAKER_PATTERNS = [
        r'^(\w+):\s*(.+)$',  # "Speaker: text"
        r'^\[(\w+)\]:\s*(.+)$',  # "[Speaker]: text"
        r'^<(\w+)>\s*(.+)$',  # "<Speaker> text"
        r'^(\w+)\s*-\s*(.+)$',  # "Speaker - text"
    ]
    
    def __init__(self):
        pass
    
    def parse(self, transcript: str) -> Dict[str, Any]:
        """
        Parse transcript and detect format, extract speakers
        
        Args:
            transcript: Raw transcript text
            
        Returns:
            Dictionary with:
            - format_detected: str (one of: 'labeled', 'json', 'plain')
            - speakers: List[Dict] with name, text, word_count
            - raw_text: str (original transcript)
        """
        if not transcript or not transcript.strip():
            return {
                'format_detected': 'plain',
                'speakers': [],
                'raw_text': transcript
            }
        
        # Try JSON format first
        json_result = self._try_parse_json(transcript)
        if json_result:
            return json_result
        
        # Try labeled format
        labeled_result = self._try_parse_labeled(transcript)
        if labeled_result:
            return labeled_result
        
        # Fallback to plain text (single speaker)
        return {
            'format_detected': 'plain',
            'speakers': [{
                'name': 'Speaker',
                'text': transcript.strip(),
                'word_count': len(transcript.split())
            }],
            'raw_text': transcript
        }
    
    def _try_parse_json(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Try to parse as JSON format"""
        try:
            # Try parsing as JSON
            data = json.loads(transcript.strip())
            
            # Check if it's a transcript-like JSON structure
            if isinstance(data, dict):
                # Look for common transcript JSON structures
                speakers_data = None
                
                # Format 1: {"speakers": [{"name": "...", "text": "..."}]}
                if 'speakers' in data and isinstance(data['speakers'], list):
                    speakers_data = data['speakers']
                
                # Format 2: {"transcript": [{"speaker": "...", "text": "..."}]}
                elif 'transcript' in data and isinstance(data['transcript'], list):
                    speakers_data = data['transcript']
                
                # Format 3: Direct array of speaker objects
                elif isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and ('speaker' in data[0] or 'name' in data[0]):
                        speakers_data = data
                
                if speakers_data:
                    speakers = []
                    speaker_texts = defaultdict(list)
                    
                    for item in speakers_data:
                        if isinstance(item, dict):
                            # Extract speaker name
                            speaker_name = (
                                item.get('speaker') or 
                                item.get('name') or 
                                item.get('label') or 
                                'Unknown'
                            )
                            
                            # Extract text
                            text = (
                                item.get('text') or 
                                item.get('content') or 
                                item.get('transcript') or 
                                ''
                            )
                            
                            if text:
                                speaker_texts[speaker_name].append(text)
                    
                    # Combine all text for each speaker
                    for speaker_name, texts in speaker_texts.items():
                        combined_text = ' '.join(texts)
                        speakers.append({
                            'name': speaker_name,
                            'text': combined_text,
                            'word_count': len(combined_text.split())
                        })
                    
                    if speakers:
                        return {
                            'format_detected': 'json',
                            'speakers': speakers,
                            'raw_text': transcript
                        }
            
        except (json.JSONDecodeError, ValueError, TypeError):
            # Not valid JSON, continue to other formats
            pass
        
        return None
    
    def _try_parse_labeled(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Try to parse as labeled format (e.g., "Speaker: text")"""
        lines = transcript.strip().split('\n')
        
        if len(lines) < 2:
            # Need at least 2 lines to be a multi-speaker transcript
            return None
        
        speakers = []
        current_speaker = None
        current_text = []
        speaker_texts = defaultdict(list)
        
        # Try to match speaker patterns
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            matched = False
            for pattern in self.SPEAKER_PATTERNS:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    speaker_name = match.group(1).strip()
                    text = match.group(2).strip()
                    
                    if text:  # Only add if there's actual text
                        speaker_texts[speaker_name].append(text)
                    matched = True
                    break
            
            # If no pattern matched, check if previous line had a speaker
            # and this might be continuation
            if not matched and current_speaker:
                # Continuation of previous speaker's text
                speaker_texts[current_speaker].append(line)
            elif not matched:
                # Could be plain text without labels - check if it looks like labeled format
                # by checking if most lines have labels
                pass
        
        # Check if we found multiple speakers or consistent labeling
        if len(speaker_texts) >= 2:
            # Multiple speakers detected
            for speaker_name, texts in speaker_texts.items():
                combined_text = ' '.join(texts)
                speakers.append({
                    'name': speaker_name,
                    'text': combined_text,
                    'word_count': len(combined_text.split())
                })
            
            if speakers:
                return {
                    'format_detected': 'labeled',
                    'speakers': speakers,
                    'raw_text': transcript
                }
        elif len(speaker_texts) == 1:
            # Single speaker with labels - still consider it labeled format
            speaker_name, texts = list(speaker_texts.items())[0]
            combined_text = ' '.join(texts)
            speakers.append({
                'name': speaker_name,
                'text': combined_text,
                'word_count': len(combined_text.split())
            })
            
            return {
                'format_detected': 'labeled',
                'speakers': speakers,
                'raw_text': transcript
            }
        
        return None
    
    def extract_student_text(self, parsed_result: Dict[str, Any], student_speaker_name: Optional[str] = None) -> str:
        """
        Extract text for a specific speaker (typically the student)
        
        Args:
            parsed_result: Result from parse() method
            student_speaker_name: Name of the speaker to extract (if None, returns first speaker)
            
        Returns:
            Combined text for the specified speaker
        """
        speakers = parsed_result.get('speakers', [])
        
        if not speakers:
            # Fallback to raw text
            return parsed_result.get('raw_text', '')
        
        if student_speaker_name:
            # Find speaker by name (case-insensitive)
            for speaker in speakers:
                if speaker['name'].lower() == student_speaker_name.lower():
                    return speaker['text']
        
        # Return first speaker if no name specified
        return speakers[0]['text'] if speakers else parsed_result.get('raw_text', '')


def parse_transcript(transcript: str) -> Dict[str, Any]:
    """
    Convenience function to parse a transcript
    
    Args:
        transcript: Raw transcript text
        
    Returns:
        Parsed transcript result
    """
    parser = TranscriptParser()
    return parser.parse(transcript)

