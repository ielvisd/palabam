"""
Relic Resonance Recommender
Suggests ZPD-balanced words (70-80% learnability) based on student profiles
"""
from typing import Dict, List, Any, Optional
import logging
from .dataset_loader import get_dataset_loader

logger = logging.getLogger(__name__)

class WordRecommender:
    """Recommends vocabulary words based on student profiles"""
    
    def __init__(self):
        self.dataset_loader = get_dataset_loader()
    
    async def recommend_words(
        self,
        profile: Dict[str, Any],
        count: int = 7,
        zpd_range: tuple = (0.70, 0.80)
    ) -> List[Dict[str, Any]]:
        """
        Recommend words in the Zone of Proximal Development (ZPD)
        Now with improved personalization based on student's actual vocabulary
        
        Args:
            profile: Student's relic resonance profile
            count: Number of words to recommend (default 5-7)
            zpd_range: Target learnability range (default 70-80%)
            
        Returns:
            List of recommended words with metadata and rationale
        """
        word_scores = profile.get('word_scores', {})
        resonance_data = profile.get('resonance_data', {})
        
        # Calculate current vocabulary level
        current_level = self._calculate_current_level(word_scores, resonance_data)
        
        # Get current grade level from resonance data
        current_grade_level = resonance_data.get('vocabulary_level', '4-5')  # Default to 4-5 if not set
        
        # Analyze student's vocabulary patterns
        student_analysis = self._analyze_student_vocabulary(word_scores, resonance_data)
        
        # Log student analysis for debugging
        logger.info(f"Student analysis - grade_level: {current_grade_level}, avg_difficulty: {student_analysis.get('avg_difficulty', 0):.1f}, "
                   f"lexical_diversity: {student_analysis.get('lexical_diversity', 0):.3f}, "
                   f"gap_range: {student_analysis.get('gap_range', (0, 0))}, "
                   f"themes: {student_analysis.get('themes', [])}, "
                   f"pos_distribution: {student_analysis.get('pos_distribution', {})}")
        
        # Get larger word pool for better diversity using grade-based ZPD
        all_zpd_words = await self._find_zpd_words(current_level, zpd_range, count * 10, current_grade_level)
        
        logger.info(f"Found {len(all_zpd_words)} words in ZPD range")
        
        # Filter out words already in profile
        existing_words = set(word_scores.keys())
        candidate_words = [w for w in all_zpd_words if w['word'] not in existing_words]
        
        logger.info(f"After filtering existing words, {len(candidate_words)} candidates remain")
        
        # Score each candidate word based on personalization factors
        scored_words = []
        for word_data in candidate_words:
            score = self._calculate_personalization_score(
                word_data, 
                student_analysis, 
                word_scores,
                current_level
            )
            word_data['personalization_score'] = score
            word_data['rationale'] = self._generate_rationale(word_data, student_analysis, word_scores)
            scored_words.append(word_data)
        
        # Sort by combined relevance and personalization
        recommendations = sorted(
            scored_words,
            key=lambda x: (x.get('relevance_score', 0) * 0.4 + x.get('personalization_score', 0) * 0.6),
            reverse=True
        )
        
        # Log top recommendations for debugging
        logger.info(f"Top 10 recommendations before diversity filter:")
        for i, rec in enumerate(recommendations[:10]):
            logger.info(f"  {i+1}. {rec.get('word')} - relevance: {rec.get('relevance_score', 0):.3f}, personalization: {rec.get('personalization_score', 0):.3f}")
        
        # Apply diversity filter to avoid similar words
        final_recommendations = self._apply_diversity_filter(recommendations, count)
        
        # Final deduplication check (case-insensitive)
        seen_words = set()
        unique_recommendations = []
        for rec in final_recommendations:
            word_lower = rec.get('word', '').lower()
            if word_lower not in seen_words:
                seen_words.add(word_lower)
                unique_recommendations.append(rec)
        
        # Log final recommendations
        logger.info(f"Final {len(unique_recommendations)} recommendations after diversity filter and deduplication:")
        for i, rec in enumerate(unique_recommendations):
            logger.info(f"  {i+1}. {rec.get('word')} - {rec.get('rationale', 'No rationale')}")
        
        return unique_recommendations[:count]
    
    def _calculate_current_level(self, word_scores: Dict[str, Any], resonance_data: Dict[str, Any]) -> float:
        """Calculate student's current vocabulary level (0-100)"""
        if not word_scores:
            return 30.0  # Beginner default
        
        # Average difficulty of words used
        avg_difficulty = sum(
            score.get('difficulty_score', 50)
            for score in word_scores.values()
        ) / len(word_scores)
        
        # Adjust based on complexity score
        complexity = resonance_data.get('complexity_score', 0.5)
        adjusted_level = avg_difficulty * (0.7 + 0.3 * complexity)
        
        return min(100.0, adjusted_level)
    
    async def _find_zpd_words(
        self,
        current_level: float,
        zpd_range: tuple,
        count: int,
        current_grade_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find words in the ZPD range using grade-based approach
        ZPD = words 1-2 grade levels above student's current grade
        """
        # Use grade-based ZPD if grade level is provided
        if current_grade_level:
            from .profiler import StoryProfiler
            profiler = StoryProfiler()
            
            # Get next 1-2 grade levels
            target_grades = profiler.get_next_grade_levels(current_grade_level)
            
            # Convert grade levels to difficulty ranges
            target_ranges = []
            for grade in target_grades:
                grade_range = profiler.grade_level_to_difficulty_range(grade)
                target_ranges.append(grade_range)
            
            # Combine ranges into min/max
            if target_ranges:
                target_min = min(r[0] for r in target_ranges)
                target_max = max(r[1] for r in target_ranges)
            else:
                # Fallback: use current level + 5 to +15
                target_min = current_level + 5
                target_max = min(current_level + 15, 75)  # Cap at 12th grade level
        else:
            # Fallback to old method if no grade level
            # But use a more reasonable formula: words 5-15 points above current level
            target_min = current_level + 5
            target_max = min(current_level + 15, 75)  # Cap at 12th grade level
        
        logger.info(f"ZPD target range: {target_min:.1f} - {target_max:.1f} (for grade {current_grade_level or 'unknown'})")
        
        # Get larger word pool from database for better selection
        sample_words = await self._get_word_pool(limit=count * 10)  # Get more candidates
        
        recommendations = []
        
        seen_words = set()  # Track words to avoid duplicates
        for word_data in sample_words:
            difficulty = word_data.get('difficulty_score', 50)
            word = word_data.get('word', '').lower()  # Normalize to lowercase
            
            # Skip if we've already seen this word
            if word in seen_words:
                continue
            
            # Check if word is in ZPD range
            if target_min <= difficulty <= target_max:
                seen_words.add(word)  # Mark as seen
                
                # Calculate relevance score
                relevance = self._calculate_relevance(difficulty, current_level, target_min, target_max)
                
                # Get word frequency for personalization
                frequency = word_data.get('coca_frequency') or word_data.get('frequency', 0) or self.dataset_loader.get_word_frequency(word)
                
                # Try to infer POS from word if not available
                pos = word_data.get('pos', 'UNKNOWN')
                if pos == 'UNKNOWN':
                    # Simple POS inference (in production, use NLP)
                    pos = self._infer_pos(word)
                
                # Add grade level metadata
                from .profiler import StoryProfiler
                profiler = StoryProfiler()
                grade_level = profiler.difficulty_to_grade_level(difficulty)
                
                recommendations.append({
                    'word': word_data.get('word', ''),  # Keep original casing
                    'difficulty_score': difficulty,
                    'grade_level': grade_level,
                    'relic_type': word_data.get('relic_type', 'echo'),
                    'definition': word_data.get('definition', ''),
                    'example': word_data.get('example', ''),
                    'frequency': frequency,
                    'pos': pos,
                    'relevance_score': relevance
                })
        
        return recommendations
    
    def _infer_pos(self, word: str) -> str:
        """Simple POS inference (basic heuristic, in production use NLP)"""
        # Common suffixes for POS
        if word.endswith(('tion', 'sion', 'ness', 'ment', 'ity')):
            return 'NOUN'
        elif word.endswith(('ed', 'ing', 'ize', 'ise')):
            return 'VERB'
        elif word.endswith(('ly',)):
            return 'ADV'
        elif word.endswith(('al', 'ic', 'ous', 'ful', 'less')):
            return 'ADJ'
        else:
            return 'NOUN'  # Default assumption
    
    def _calculate_relevance(
        self,
        difficulty: float,
        current_level: float,
        target_min: float,
        target_max: float
    ) -> float:
        """Calculate how relevant a word is to the student's ZPD"""
        # Words closer to the middle of ZPD range are more relevant
        zpd_center = (target_min + target_max) / 2
        distance_from_center = abs(difficulty - zpd_center)
        zpd_width = target_max - target_min
        
        # Normalize relevance (closer to center = higher relevance)
        relevance = 1.0 - (distance_from_center / (zpd_width / 2))
        return max(0.0, min(1.0, relevance))
    
    async def _get_word_pool(self, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get pool of words to recommend from database
        """
        try:
            from db import words as db_words
            
            # Search for words in broader range (20-90 difficulty) for better selection
            word_pool = await db_words.search_words(
                min_difficulty=20,
                max_difficulty=90,
                limit=limit
            )
            
            if word_pool:
                return word_pool
            
            # Fallback to sample words if database is empty
            logger.warning("Word pool from database is empty, using fallback")
            return self._get_fallback_word_pool()
            
        except Exception as e:
            logger.warning(f"Error fetching word pool from database: {e}, using fallback")
            return self._get_fallback_word_pool()
    
    def _get_fallback_word_pool(self) -> List[Dict[str, Any]]:
        """Fallback word pool if database is unavailable - expanded for diversity (80+ words)"""
        from .profiler import StoryProfiler
        profiler = StoryProfiler()
        
        words = [
            # K-1 Grade words (5-15 difficulty)
            {'word': 'happy', 'difficulty_score': 10, 'relic_type': 'whisper', 'definition': 'feeling joy', 'example': 'I am happy today.', 'pos': 'ADJ', 'frequency': 12000},
            {'word': 'play', 'difficulty_score': 8, 'relic_type': 'whisper', 'definition': 'to have fun', 'example': 'Let\'s play outside.', 'pos': 'VERB', 'frequency': 15000},
            {'word': 'friend', 'difficulty_score': 12, 'relic_type': 'whisper', 'definition': 'a person you like', 'example': 'She is my friend.', 'pos': 'NOUN', 'frequency': 11000},
            {'word': 'big', 'difficulty_score': 6, 'relic_type': 'whisper', 'definition': 'large in size', 'example': 'That is a big tree.', 'pos': 'ADJ', 'frequency': 18000},
            {'word': 'run', 'difficulty_score': 9, 'relic_type': 'whisper', 'definition': 'to move fast', 'example': 'I can run fast.', 'pos': 'VERB', 'frequency': 14000},
            
            # 2-3 Grade words (15-25 difficulty)
            {'word': 'brave', 'difficulty_score': 30, 'relic_type': 'echo', 'definition': 'showing courage', 'example': 'She was brave during the storm.', 'pos': 'ADJ', 'frequency': 3800},
            {'word': 'explore', 'difficulty_score': 38, 'relic_type': 'echo', 'definition': 'to travel through an area to learn about it', 'example': 'We want to explore the mountains.', 'pos': 'VERB', 'frequency': 4200},
            {'word': 'mystery', 'difficulty_score': 42, 'relic_type': 'echo', 'definition': 'something that is difficult to understand or explain', 'example': 'The mystery of the missing keys.', 'pos': 'NOUN', 'frequency': 3100},
            {'word': 'creative', 'difficulty_score': 36, 'relic_type': 'echo', 'definition': 'having the ability to create', 'example': 'She is very creative with her art.', 'pos': 'ADJ', 'frequency': 4800},
            {'word': 'journey', 'difficulty_score': 40, 'relic_type': 'echo', 'definition': 'an act of traveling from one place to another', 'example': 'Our journey took three days.', 'pos': 'NOUN', 'frequency': 3500},
            
            # 4-5 Grade words (25-35 difficulty)  
            {'word': 'curious', 'difficulty_score': 35, 'relic_type': 'echo', 'definition': 'eager to know or learn something', 'example': 'The curious child asked many questions.', 'pos': 'ADJ', 'frequency': 4500},
            {'word': 'adventure', 'difficulty_score': 40, 'relic_type': 'echo', 'definition': 'an exciting or dangerous experience', 'example': 'We went on an adventure in the forest.', 'pos': 'NOUN', 'frequency': 3200},
            {'word': 'challenge', 'difficulty_score': 45, 'relic_type': 'echo', 'definition': 'a task or situation that tests ability', 'example': 'The math problem was a real challenge.', 'pos': 'NOUN', 'frequency': 5500},
            {'word': 'wonder', 'difficulty_score': 32, 'relic_type': 'echo', 'definition': 'a feeling of amazement', 'example': 'I wonder what will happen next.', 'pos': 'VERB', 'frequency': 5200},
            {'word': 'imagine', 'difficulty_score': 34, 'relic_type': 'echo', 'definition': 'to form a mental picture', 'example': 'Can you imagine living on Mars?', 'pos': 'VERB', 'frequency': 4600},
            {'word': 'discover', 'difficulty_score': 50, 'relic_type': 'resonance', 'definition': 'to find something for the first time', 'example': 'Scientists discover new things every day.', 'pos': 'VERB', 'frequency': 3800},
            {'word': 'observe', 'difficulty_score': 48, 'relic_type': 'resonance', 'definition': 'to notice or watch', 'example': 'Scientists observe nature carefully.', 'pos': 'VERB', 'frequency': 4100},
            {'word': 'describe', 'difficulty_score': 44, 'relic_type': 'echo', 'definition': 'to give an account in words', 'example': 'Please describe what you saw.', 'pos': 'VERB', 'frequency': 5500},
            {'word': 'explain', 'difficulty_score': 38, 'relic_type': 'echo', 'definition': 'to make something clear', 'example': 'Can you explain how this works?', 'pos': 'VERB', 'frequency': 6200},
            {'word': 'understand', 'difficulty_score': 35, 'relic_type': 'echo', 'definition': 'to comprehend or grasp', 'example': 'I understand the problem now.', 'pos': 'VERB', 'frequency': 7800},
            
            # Intermediate words (45-65 difficulty)
            {'word': 'accomplish', 'difficulty_score': 55, 'relic_type': 'resonance', 'definition': 'to achieve or complete successfully', 'example': 'She worked hard to accomplish her goals.', 'pos': 'VERB', 'frequency': 4200},
            {'word': 'evidence', 'difficulty_score': 52, 'relic_type': 'resonance', 'definition': 'proof or indication', 'example': 'The evidence supports the theory.', 'pos': 'NOUN', 'frequency': 4800},
            {'word': 'method', 'difficulty_score': 54, 'relic_type': 'resonance', 'definition': 'a way of doing something', 'example': 'We used a new method to solve it.', 'pos': 'NOUN', 'frequency': 5100},
            {'word': 'significant', 'difficulty_score': 58, 'relic_type': 'resonance', 'definition': 'important or notable', 'example': 'This is a significant discovery.', 'pos': 'ADJ', 'frequency': 6200},
            {'word': 'conclude', 'difficulty_score': 56, 'relic_type': 'resonance', 'definition': 'to reach a decision', 'example': 'We can conclude from the results.', 'pos': 'VERB', 'frequency': 3500},
            {'word': 'analyze', 'difficulty_score': 60, 'relic_type': 'resonance', 'definition': 'to examine in detail', 'example': 'We need to analyze the data carefully.', 'pos': 'VERB', 'frequency': 2800},
            {'word': 'determine', 'difficulty_score': 58, 'relic_type': 'resonance', 'definition': 'to decide or find out', 'example': 'We need to determine the cause.', 'pos': 'VERB', 'frequency': 4400},
            {'word': 'establish', 'difficulty_score': 61, 'relic_type': 'resonance', 'definition': 'to set up or create', 'example': 'They want to establish a new rule.', 'pos': 'VERB', 'frequency': 3600},
            {'word': 'evaluate', 'difficulty_score': 59, 'relic_type': 'resonance', 'definition': 'to assess or judge', 'example': 'We must evaluate all options.', 'pos': 'VERB', 'frequency': 2700},
            {'word': 'precise', 'difficulty_score': 62, 'relic_type': 'resonance', 'definition': 'exact and accurate', 'example': 'The measurements must be precise.', 'pos': 'ADJ', 'frequency': 2900},
            {'word': 'investigate', 'difficulty_score': 64, 'relic_type': 'resonance', 'definition': 'to examine or study', 'example': 'Detectives investigate crimes.', 'pos': 'VERB', 'frequency': 2200},
            {'word': 'demonstrate', 'difficulty_score': 63, 'relic_type': 'resonance', 'definition': 'to show or prove', 'example': 'The experiment demonstrates the theory.', 'pos': 'VERB', 'frequency': 3300},
            {'word': 'resilient', 'difficulty_score': 65, 'relic_type': 'resonance', 'definition': 'able to recover quickly from difficulties', 'example': 'She was resilient after the setback.', 'pos': 'ADJ', 'frequency': 2500},
            {'word': 'strategy', 'difficulty_score': 57, 'relic_type': 'resonance', 'definition': 'a plan of action', 'example': 'We need a new strategy to win.', 'pos': 'NOUN', 'frequency': 3400},
            {'word': 'approach', 'difficulty_score': 53, 'relic_type': 'resonance', 'definition': 'a way of dealing with something', 'example': 'Let\'s try a different approach.', 'pos': 'NOUN', 'frequency': 4900},
            {'word': 'consider', 'difficulty_score': 47, 'relic_type': 'echo', 'definition': 'to think carefully about', 'example': 'We should consider all options.', 'pos': 'VERB', 'frequency': 6800},
            {'word': 'develop', 'difficulty_score': 51, 'relic_type': 'resonance', 'definition': 'to grow or cause to grow', 'example': 'We need to develop new skills.', 'pos': 'VERB', 'frequency': 5600},
            {'word': 'examine', 'difficulty_score': 55, 'relic_type': 'resonance', 'definition': 'to inspect closely', 'example': 'Let\'s examine the evidence.', 'pos': 'VERB', 'frequency': 3200},
            {'word': 'identify', 'difficulty_score': 59, 'relic_type': 'resonance', 'definition': 'to recognize or establish', 'example': 'Can you identify this bird?', 'pos': 'VERB', 'frequency': 3800},
            {'word': 'interpret', 'difficulty_score': 61, 'relic_type': 'resonance', 'definition': 'to explain the meaning of', 'example': 'How do you interpret this data?', 'pos': 'VERB', 'frequency': 2600},
            {'word': 'organize', 'difficulty_score': 49, 'relic_type': 'echo', 'definition': 'to arrange systematically', 'example': 'Let\'s organize our notes.', 'pos': 'VERB', 'frequency': 4100},
            {'word': 'predict', 'difficulty_score': 54, 'relic_type': 'resonance', 'definition': 'to say what will happen', 'example': 'Can you predict the weather?', 'pos': 'VERB', 'frequency': 2900},
            {'word': 'recognize', 'difficulty_score': 52, 'relic_type': 'resonance', 'definition': 'to identify from previous experience', 'example': 'I recognize that voice.', 'pos': 'VERB', 'frequency': 4500},
            {'word': 'represent', 'difficulty_score': 56, 'relic_type': 'resonance', 'definition': 'to stand for or symbolize', 'example': 'This flag represents our country.', 'pos': 'VERB', 'frequency': 4200},
            {'word': 'summarize', 'difficulty_score': 58, 'relic_type': 'resonance', 'definition': 'to give a brief statement', 'example': 'Please summarize the main points.', 'pos': 'VERB', 'frequency': 2400},
            {'word': 'synthesize', 'difficulty_score': 64, 'relic_type': 'resonance', 'definition': 'to combine into a whole', 'example': 'We need to synthesize these ideas.', 'pos': 'VERB', 'frequency': 1800},
            {'word': 'transform', 'difficulty_score': 60, 'relic_type': 'resonance', 'definition': 'to change completely', 'example': 'The caterpillar will transform into a butterfly.', 'pos': 'VERB', 'frequency': 3100},
            {'word': 'adapt', 'difficulty_score': 55, 'relic_type': 'resonance', 'definition': 'to adjust to new conditions', 'example': 'Animals adapt to their environment.', 'pos': 'VERB', 'frequency': 2800},
            {'word': 'comprehend', 'difficulty_score': 62, 'relic_type': 'resonance', 'definition': 'to understand fully', 'example': 'I cannot comprehend this problem.', 'pos': 'VERB', 'frequency': 2200},
            {'word': 'construct', 'difficulty_score': 53, 'relic_type': 'resonance', 'definition': 'to build or make', 'example': 'We will construct a new bridge.', 'pos': 'VERB', 'frequency': 3600},
            {'word': 'contribute', 'difficulty_score': 57, 'relic_type': 'resonance', 'definition': 'to give or add', 'example': 'Everyone can contribute ideas.', 'pos': 'VERB', 'frequency': 3300},
            {'word': 'critique', 'difficulty_score': 63, 'relic_type': 'resonance', 'definition': 'to evaluate critically', 'example': 'Let\'s critique this essay.', 'pos': 'VERB', 'frequency': 1900},
            {'word': 'debate', 'difficulty_score': 54, 'relic_type': 'resonance', 'definition': 'to discuss opposing views', 'example': 'We will debate the topic tomorrow.', 'pos': 'VERB', 'frequency': 2700},
            {'word': 'defend', 'difficulty_score': 50, 'relic_type': 'echo', 'definition': 'to protect or support', 'example': 'I will defend my position.', 'pos': 'VERB', 'frequency': 4100},
            {'word': 'distinguish', 'difficulty_score': 61, 'relic_type': 'resonance', 'definition': 'to recognize as different', 'example': 'Can you distinguish these colors?', 'pos': 'VERB', 'frequency': 2500},
            {'word': 'elaborate', 'difficulty_score': 59, 'relic_type': 'resonance', 'definition': 'to add more detail', 'example': 'Can you elaborate on that?', 'pos': 'VERB', 'frequency': 2100},
            {'word': 'emphasize', 'difficulty_score': 60, 'relic_type': 'resonance', 'definition': 'to give special importance', 'example': 'I want to emphasize this point.', 'pos': 'VERB', 'frequency': 2900},
            {'word': 'enhance', 'difficulty_score': 58, 'relic_type': 'resonance', 'definition': 'to improve', 'example': 'This will enhance our understanding.', 'pos': 'VERB', 'frequency': 3200},
            {'word': 'formulate', 'difficulty_score': 63, 'relic_type': 'resonance', 'definition': 'to create or develop', 'example': 'Let\'s formulate a plan.', 'pos': 'VERB', 'frequency': 2000},
            {'word': 'illustrate', 'difficulty_score': 59, 'relic_type': 'resonance', 'definition': 'to explain with examples', 'example': 'This diagram illustrates the process.', 'pos': 'VERB', 'frequency': 2400},
            {'word': 'implement', 'difficulty_score': 61, 'relic_type': 'resonance', 'definition': 'to put into effect', 'example': 'We will implement the new policy.', 'pos': 'VERB', 'frequency': 3100},
            {'word': 'justify', 'difficulty_score': 62, 'relic_type': 'resonance', 'definition': 'to show to be right', 'example': 'Can you justify your answer?', 'pos': 'VERB', 'frequency': 2300},
            {'word': 'persuade', 'difficulty_score': 58, 'relic_type': 'resonance', 'definition': 'to convince', 'example': 'I tried to persuade them to come.', 'pos': 'VERB', 'frequency': 2600},
            {'word': 'prioritize', 'difficulty_score': 60, 'relic_type': 'resonance', 'definition': 'to treat as most important', 'example': 'We must prioritize safety.', 'pos': 'VERB', 'frequency': 2700},
            {'word': 'propose', 'difficulty_score': 57, 'relic_type': 'resonance', 'definition': 'to suggest', 'example': 'I propose we meet tomorrow.', 'pos': 'VERB', 'frequency': 3500},
            {'word': 'refine', 'difficulty_score': 59, 'relic_type': 'resonance', 'definition': 'to improve by making small changes', 'example': 'We need to refine our approach.', 'pos': 'VERB', 'frequency': 2200},
            {'word': 'reinforce', 'difficulty_score': 61, 'relic_type': 'resonance', 'definition': 'to strengthen', 'example': 'This will reinforce our argument.', 'pos': 'VERB', 'frequency': 2400},
            {'word': 'resolve', 'difficulty_score': 56, 'relic_type': 'resonance', 'definition': 'to find a solution', 'example': 'We must resolve this conflict.', 'pos': 'VERB', 'frequency': 3800},
            {'word': 'specify', 'difficulty_score': 58, 'relic_type': 'resonance', 'definition': 'to state clearly', 'example': 'Please specify your requirements.', 'pos': 'VERB', 'frequency': 3000},
            {'word': 'theorize', 'difficulty_score': 65, 'relic_type': 'resonance', 'definition': 'to form a theory', 'example': 'Scientists theorize about the universe.', 'pos': 'VERB', 'frequency': 1500},
            {'word': 'validate', 'difficulty_score': 62, 'relic_type': 'resonance', 'definition': 'to confirm as valid', 'example': 'We need to validate these results.', 'pos': 'VERB', 'frequency': 2800},
            
            # Advanced words (66-85 difficulty)
            {'word': 'perseverance', 'difficulty_score': 75, 'relic_type': 'thunder', 'definition': 'persistence in doing something despite difficulty', 'example': 'His perseverance paid off in the end.', 'pos': 'NOUN', 'frequency': 1800},
            {'word': 'sophisticated', 'difficulty_score': 72, 'relic_type': 'thunder', 'definition': 'complex or advanced', 'example': 'This is a sophisticated system.', 'pos': 'ADJ', 'frequency': 2400},
            {'word': 'comprehensive', 'difficulty_score': 68, 'relic_type': 'thunder', 'definition': 'complete and including everything', 'example': 'We need a comprehensive study.', 'pos': 'ADJ', 'frequency': 2900},
            {'word': 'elaborate', 'difficulty_score': 70, 'relic_type': 'thunder', 'definition': 'detailed and complicated', 'example': 'This is an elaborate design.', 'pos': 'ADJ', 'frequency': 2100},
            {'word': 'profound', 'difficulty_score': 73, 'relic_type': 'thunder', 'definition': 'very great or intense', 'example': 'This had a profound effect.', 'pos': 'ADJ', 'frequency': 2000},
            {'word': 'substantial', 'difficulty_score': 69, 'relic_type': 'thunder', 'definition': 'of considerable importance or size', 'example': 'We made substantial progress.', 'pos': 'ADJ', 'frequency': 3100},
            {'word': 'theoretical', 'difficulty_score': 71, 'relic_type': 'thunder', 'definition': 'based on theory rather than practice', 'example': 'This is a theoretical approach.', 'pos': 'ADJ', 'frequency': 2500},
            {'word': 'ambiguous', 'difficulty_score': 74, 'relic_type': 'thunder', 'definition': 'having more than one meaning', 'example': 'The message was ambiguous.', 'pos': 'ADJ', 'frequency': 1800},
            {'word': 'coherent', 'difficulty_score': 67, 'relic_type': 'thunder', 'definition': 'logical and consistent', 'example': 'Her argument was coherent.', 'pos': 'ADJ', 'frequency': 2200},
            {'word': 'contradictory', 'difficulty_score': 72, 'relic_type': 'thunder', 'definition': 'opposing or conflicting', 'example': 'These statements are contradictory.', 'pos': 'ADJ', 'frequency': 1900},
            {'word': 'hypothetical', 'difficulty_score': 70, 'relic_type': 'thunder', 'definition': 'supposed but not necessarily real', 'example': 'This is a hypothetical situation.', 'pos': 'ADJ', 'frequency': 2100},
            {'word': 'paradoxical', 'difficulty_score': 76, 'relic_type': 'thunder', 'definition': 'seemingly contradictory', 'example': 'This seems paradoxical.', 'pos': 'ADJ', 'frequency': 1400},
            {'word': 'philosophical', 'difficulty_score': 75, 'relic_type': 'thunder', 'definition': 'relating to philosophy', 'example': 'This is a philosophical question.', 'pos': 'ADJ', 'frequency': 2000},
            {'word': 'systematic', 'difficulty_score': 66, 'relic_type': 'thunder', 'definition': 'done according to a system', 'example': 'We need a systematic approach.', 'pos': 'ADJ', 'frequency': 2800},
            {'word': 'analytical', 'difficulty_score': 69, 'relic_type': 'thunder', 'definition': 'relating to analysis', 'example': 'She has an analytical mind.', 'pos': 'ADJ', 'frequency': 2400},
            {'word': 'conceptual', 'difficulty_score': 71, 'relic_type': 'thunder', 'definition': 'relating to concepts', 'example': 'This is a conceptual framework.', 'pos': 'ADJ', 'frequency': 1900},
            {'word': 'empirical', 'difficulty_score': 73, 'relic_type': 'thunder', 'definition': 'based on observation', 'example': 'We need empirical evidence.', 'pos': 'ADJ', 'frequency': 2200},
            {'word': 'methodological', 'difficulty_score': 77, 'relic_type': 'thunder', 'definition': 'relating to methods', 'example': 'This is a methodological issue.', 'pos': 'ADJ', 'frequency': 1600},
            {'word': 'phenomenological', 'difficulty_score': 82, 'relic_type': 'thunder', 'definition': 'relating to phenomena', 'example': 'This is a phenomenological study.', 'pos': 'ADJ', 'frequency': 800}
        ]
        
        # Add grade_level metadata to all words
        for word_data in words:
            difficulty = word_data.get('difficulty_score', 50)
            word_data['grade_level'] = profiler.difficulty_to_grade_level(difficulty)
        
        # Deduplicate by word (case-insensitive)
        seen_words = set()
        unique_words = []
        for word_data in words:
            word_lower = word_data.get('word', '').lower()
            if word_lower not in seen_words:
                seen_words.add(word_lower)
                unique_words.append(word_data)
        
        return unique_words
    
    def _analyze_student_vocabulary(
        self, 
        word_scores: Dict[str, Any], 
        resonance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze student's vocabulary to identify patterns and gaps"""
        analysis = {
            'pos_distribution': {},  # Part of speech distribution
            'difficulty_distribution': [],  # List of difficulty scores
            'themes': resonance_data.get('themes', []),
            'avg_difficulty': 0,
            'lexical_diversity': 0,
            'gap_words': []  # Words at their level they should know
        }
        
        if not word_scores:
            return analysis
        
        # Analyze part of speech distribution
        pos_counts = {}
        difficulties = []
        word_frequencies = []
        
        for word, score_data in word_scores.items():
            pos = score_data.get('pos', 'UNKNOWN')
            pos_counts[pos] = pos_counts.get(pos, 0) + 1
            
            difficulty = score_data.get('difficulty_score', 50)
            difficulties.append(difficulty)
            
            frequency = score_data.get('frequency', 0)
            word_frequencies.append(frequency)
        
        analysis['pos_distribution'] = pos_counts
        analysis['difficulty_distribution'] = difficulties
        analysis['avg_difficulty'] = sum(difficulties) / len(difficulties) if difficulties else 50
        analysis['lexical_diversity'] = len(word_scores) / max(1, sum(s.get('count', 1) for s in word_scores.values()))
        
        # Identify gaps: common words at their level they're not using
        # Use grade-appropriate range (about 1 grade level span)
        avg_level = analysis['avg_difficulty']
        # For grade-based gaps, use a tighter range (about 10 points)
        gap_range = (max(0, avg_level - 5), min(75, avg_level + 10))  # Cap at 12th grade
        analysis['gap_range'] = gap_range
        
        return analysis
    
    def _calculate_personalization_score(
        self,
        word_data: Dict[str, Any],
        student_analysis: Dict[str, Any],
        word_scores: Dict[str, Any],
        current_level: float
    ) -> float:
        """Calculate how well a word matches the student's needs"""
        score = 0.0
        word = word_data.get('word', '')
        difficulty = word_data.get('difficulty_score', 50)
        frequency = word_data.get('frequency', 0) or self.dataset_loader.get_word_frequency(word)
        
        # 1. Gap identification (30% weight): Words at their level they should know
        gap_range = student_analysis.get('gap_range', (30, 70))
        if gap_range[0] <= difficulty <= gap_range[1]:
            gap_score = 1.0 - abs(difficulty - (gap_range[0] + gap_range[1]) / 2) / (gap_range[1] - gap_range[0])
            score += gap_score * 0.3
        
        # 2. COCA frequency weighting (25% weight): Prioritize high-utility words
        if frequency > 0:
            # Log scale: more frequent = higher score
            import math
            freq_score = min(1.0, math.log10(max(1, frequency)) / 6.0)  # Normalize to 0-1
            score += freq_score * 0.25
        
        # 3. Part of speech diversity (20% weight): Balance POS distribution
        word_pos = word_data.get('pos', 'UNKNOWN')
        pos_dist = student_analysis.get('pos_distribution', {})
        total_pos = sum(pos_dist.values()) if pos_dist else 1
        
        # If student uses few words of this POS, boost score
        pos_count = pos_dist.get(word_pos, 0)
        pos_ratio = pos_count / total_pos if total_pos > 0 else 0
        # Lower ratio = more needed for diversity
        pos_score = 1.0 - min(1.0, pos_ratio * 2)  # Boost if underrepresented
        score += pos_score * 0.2
        
        # 4. Thematic relevance (15% weight): Match student's writing themes
        themes = student_analysis.get('themes', [])
        # Simple word overlap check (in production, use semantic similarity)
        theme_score = 0.0
        if themes:
            word_lower = word.lower()
            for theme in themes:
                if theme in word_lower or word_lower in theme:
                    theme_score = 0.5
                    break
            # Check if word is semantically related (simple heuristic)
            # Words with similar difficulty in same range might be related
            avg_diff = student_analysis.get('avg_difficulty', 50)
            if abs(difficulty - avg_diff) < 10:
                theme_score = max(theme_score, 0.3)
        score += theme_score * 0.15
        
        # 5. Lexical sophistication (10% weight): Encourage growth
        lexical_diversity = student_analysis.get('lexical_diversity', 0.5)
        # If student has low diversity, recommend more common words
        # If high diversity, recommend more sophisticated words
        if lexical_diversity < 0.3:
            # Low diversity: prioritize common words
            if frequency > 1000:
                score += 0.1
        else:
            # High diversity: can handle more sophisticated words
            if difficulty > current_level * 0.8:
                score += 0.1
        
        return min(1.0, score)
    
    def _generate_rationale(
        self,
        word_data: Dict[str, Any],
        student_analysis: Dict[str, Any],
        word_scores: Dict[str, Any]
    ) -> str:
        """
        Generate clear pedagogical rationale for why this word was recommended.
        Focuses on helping teachers understand the recommendation.
        """
        word = word_data.get('word', '')
        difficulty = word_data.get('difficulty_score', 50)
        grade_level = word_data.get('grade_level', '')
        frequency = word_data.get('frequency', 0) or self.dataset_loader.get_word_frequency(word)
        
        # Get student's current grade level
        from .profiler import StoryProfiler
        profiler = StoryProfiler()
        current_grade = student_analysis.get('vocabulary_level', '4-5')
        current_min, current_max = profiler.grade_level_to_difficulty_range(current_grade)
        current_avg = (current_min + current_max) / 2
        
        # Primary rationale based on ZPD positioning
        primary_rationale = None
        
        # Check if word is in ZPD (next 1-2 grade levels)
        next_grades = profiler.get_next_grade_levels(current_grade)
        if next_grades:
            next_min, next_max = profiler.grade_level_to_difficulty_range(next_grades[0])
            if next_min <= difficulty <= next_max:
                # Word is in the perfect ZPD range
                if grade_level:
                    primary_rationale = f"Perfect for {current_grade} grade student - targets {grade_level} level vocabulary"
                else:
                    primary_rationale = f"Targets next level vocabulary growth for {current_grade} grade student"
        
        # If no primary rationale, use gap-based
        if not primary_rationale:
            gap_range = student_analysis.get('gap_range', (current_min - 5, current_max + 5))
            if gap_range[0] <= difficulty <= gap_range[1]:
                if difficulty < current_min:
                    primary_rationale = f"Fills vocabulary gap - common {grade_level} word student should know"
                else:
                    primary_rationale = f"Expands vocabulary at {grade_level} level, slightly above current {current_grade} level"
            else:
                primary_rationale = f"Appropriate for {grade_level} grade level" if grade_level else "Valuable vocabulary expansion"
        
        # Secondary rationales (contextual)
        secondary = []
        
        # Frequency-based
        if frequency > 5000:
            secondary.append("highly useful in academic writing")
        elif frequency > 2000:
            secondary.append("commonly used in grade-level texts")
        
        # POS diversity
        word_pos = word_data.get('pos', 'UNKNOWN')
        pos_dist = student_analysis.get('pos_distribution', {})
        if word_pos in pos_dist:
            pos_count = pos_dist[word_pos]
            total_pos = sum(pos_dist.values()) if pos_dist else 1
            if pos_count / total_pos < 0.15:
                secondary.append("expands part-of-speech variety")
        
        # Theme relevance
        themes = student_analysis.get('themes', [])
        if themes and any(theme in word.lower() for theme in themes):
            secondary.append("relevant to student's writing topics")
        
        # Combine into clear pedagogical message
        if secondary:
            return f"{primary_rationale} • {', '.join(secondary)}"
        else:
            return primary_rationale
    
    def _apply_diversity_filter(
        self,
        recommendations: List[Dict[str, Any]],
        count: int
    ) -> List[Dict[str, Any]]:
        """Ensure recommendations are diverse (different POS, difficulty levels) and unique"""
        if len(recommendations) <= count:
            # Still deduplicate even if we have fewer recommendations
            seen_words = set()
            unique_recommendations = []
            for rec in recommendations:
                word_lower = rec.get('word', '').lower()
                if word_lower not in seen_words:
                    seen_words.add(word_lower)
                    unique_recommendations.append(rec)
            return unique_recommendations
        
        selected = []
        used_pos = set()
        difficulty_levels = {'low': 0, 'mid': 0, 'high': 0}
        seen_words = set()  # Track words to avoid duplicates
        
        for word_data in recommendations:
            if len(selected) >= count:
                break
            
            word = word_data.get('word', '')
            word_lower = word.lower()
            difficulty = word_data.get('difficulty_score', 50)
            pos = word_data.get('pos', 'UNKNOWN')
            
            # Skip duplicates
            if word_lower in seen_words:
                continue
            
            # Categorize difficulty
            if difficulty < 40:
                diff_cat = 'low'
            elif difficulty < 70:
                diff_cat = 'mid'
            else:
                diff_cat = 'high'
            
            # Prefer diversity: different POS and difficulty levels
            pos_penalty = 0.1 if pos in used_pos else 0
            diff_penalty = 0.05 if difficulty_levels[diff_cat] >= count // 3 else 0
            
            # Adjust score for diversity
            original_score = word_data.get('personalization_score', 0)
            word_data['personalization_score'] = original_score - pos_penalty - diff_penalty
        
        # Re-sort with diversity adjustments
        recommendations = sorted(
            recommendations,
            key=lambda x: (x.get('relevance_score', 0) * 0.4 + x.get('personalization_score', 0) * 0.6),
            reverse=True
        )
        
        # Select diverse set with deduplication
        selected = []
        used_pos = set()
        difficulty_levels = {'low': 0, 'mid': 0, 'high': 0}
        seen_words = set()  # Track words to avoid duplicates
        
        for word_data in recommendations:
            if len(selected) >= count:
                break
            
            word = word_data.get('word', '')
            word_lower = word.lower()
            difficulty = word_data.get('difficulty_score', 50)
            pos = word_data.get('pos', 'UNKNOWN')
            
            # Skip duplicates
            if word_lower in seen_words:
                continue
            
            if difficulty < 40:
                diff_cat = 'low'
            elif difficulty < 70:
                diff_cat = 'mid'
            else:
                diff_cat = 'high'
            
            # Prefer words with different POS and difficulty
            if pos not in used_pos or difficulty_levels[diff_cat] < count // 3:
                selected.append(word_data)
                seen_words.add(word_lower)
                used_pos.add(pos)
                difficulty_levels[diff_cat] += 1
        
        # Fill remaining slots if needed (with deduplication)
        for word_data in recommendations:
            if len(selected) >= count:
                break
            word_lower = word_data.get('word', '').lower()
            if word_lower not in seen_words and word_data not in selected:
                selected.append(word_data)
                seen_words.add(word_lower)
        
        return selected
    
    def evolve_word(self, current_word: str, mastery_level: float) -> Optional[Dict[str, Any]]:
        """
        Suggest next word evolution based on mastery
        Dynamic pacing: Mastery → evolution (e.g., "big" → "enormous")
        """
        if mastery_level < 0.8:  # Not yet mastered
            return None
        
        # Find more advanced synonym or related word
        # This would use a thesaurus or word relationship database
        evolution_map = {
            'big': {'word': 'enormous', 'difficulty_score': 45},
            'happy': {'word': 'ecstatic', 'difficulty_score': 60},
            'sad': {'word': 'melancholy', 'difficulty_score': 70},
            'good': {'word': 'excellent', 'difficulty_score': 50},
            'bad': {'word': 'terrible', 'difficulty_score': 50}
        }
        
        if current_word.lower() in evolution_map:
            return evolution_map[current_word.lower()]
        
        return None

# FastAPI router
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RecommendRequest(BaseModel):
    profile: Dict[str, Any]
    count: int = 7
    zpd_range: tuple = (0.70, 0.80)

class RecommendResponse(BaseModel):
    recommended_words: List[Dict[str, Any]]

@router.post("/", response_model=RecommendResponse)
async def recommend_words(request: RecommendRequest):
    """Get word recommendations based on profile"""
    try:
        recommender = WordRecommender()
        recommendations = await recommender.recommend_words(
            request.profile,
            count=request.count,
            zpd_range=request.zpd_range
        )
        
        return RecommendResponse(recommended_words=recommendations)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}")
async def get_student_recommendations(student_id: str):
    """Get recommendations for a student from database"""
    try:
        from db import recommendations as db_recommendations
        
        recs = await db_recommendations.get_student_recommendations(
            student_id=student_id,
            status="pending",
            limit=20
        )
        
        return {"recommended_words": recs}
    except Exception as e:
        logger.error(f"Error fetching student recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

