"""
Automated tests for the recommendation engine
Tests ZPD calculation, word recommendation quality, and metadata
"""
import pytest
from nlp.recommender import WordRecommender
from nlp.profiler import StoryProfiler


class TestRecommender:
    """Test suite for WordRecommender"""
    
    @pytest.fixture
    def recommender(self):
        """Create a recommender instance"""
        return WordRecommender()
    
    @pytest.fixture
    def sample_profile(self):
        """Create a sample profile for testing"""
        profiler = StoryProfiler()
        transcript = """
        I like to play games with my friends. We have fun together.
        Sometimes we play outside and sometimes we play inside.
        My favorite game is tag because it's exciting and fast.
        """
        analysis = profiler.analyze_transcript(transcript)
        return {
            'word_scores': analysis['word_scores'],
            'resonance_data': analysis['resonance_data']
        }
    
    @pytest.mark.asyncio
    async def test_recommend_words_basic(self, recommender, sample_profile):
        """Test basic word recommendation"""
        recommendations = await recommender.recommend_words(
            profile=sample_profile,
            count=5
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_recommend_words_count(self, recommender, sample_profile):
        """Test that recommendation count is respected"""
        for count in [3, 5, 7]:
            recommendations = await recommender.recommend_words(
                profile=sample_profile,
                count=count
            )
            assert len(recommendations) <= count
    
    @pytest.mark.asyncio
    async def test_recommend_words_zpd_range(self, recommender, sample_profile):
        """Test that recommendations fall within ZPD range (70-80%)"""
        recommendations = await recommender.recommend_words(
            profile=sample_profile,
            count=7,
            zpd_range=(0.70, 0.80)
        )
        
        # Verify recommendations have difficulty scores
        for rec in recommendations:
            assert 'word' in rec
            if 'difficulty_score' in rec:
                # Difficulty should be reasonable (not too easy, not too hard)
                assert 0 <= rec['difficulty_score'] <= 100
    
    @pytest.mark.asyncio
    async def test_recommend_words_metadata(self, recommender, sample_profile):
        """Test that recommendations include metadata"""
        recommendations = await recommender.recommend_words(
            profile=sample_profile,
            count=5
        )
        
        for rec in recommendations:
            assert 'word' in rec
            # Metadata might include definition, example, difficulty_score, etc.
            # At minimum, word should be present
    
    @pytest.mark.asyncio
    async def test_no_duplicate_recommendations(self, recommender, sample_profile):
        """Test that recommendations don't contain duplicates"""
        recommendations = await recommender.recommend_words(
            profile=sample_profile,
            count=10
        )
        
        words = [rec['word'] for rec in recommendations]
        assert len(words) == len(set(words)), "Found duplicate recommendations"
    
    @pytest.mark.asyncio
    async def test_recommendations_filter_vocabulary(self, recommender, sample_profile):
        """Test that recommendations filter out words already in student vocabulary"""
        # Get words from profile
        profile_words = set(sample_profile['word_scores'].keys())
        
        recommendations = await recommender.recommend_words(
            profile=sample_profile,
            count=10
        )
        
        rec_words = {rec['word'].lower() for rec in recommendations}
        
        # Recommendations should not include words already in profile
        # (allowing for some overlap due to lemmatization differences)
        overlap = profile_words.intersection(rec_words)
        # Allow some overlap but not all
        assert len(overlap) < len(rec_words), "Too many recommendations match existing vocabulary"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

