"""
Automated tests for the profiling pipeline
Tests transcript analysis, vocabulary level calculation, and profile creation
"""
import pytest
from nlp.profiler import StoryProfiler
from nlp.dataset_loader import DatasetLoader


class TestProfiler:
    """Test suite for StoryProfiler"""
    
    @pytest.fixture
    def profiler(self):
        """Create a profiler instance for testing"""
        return StoryProfiler()
    
    @pytest.fixture
    def sample_transcript_short(self):
        """Short transcript for testing"""
        return "I like to play games with my friends. We have fun together."
    
    @pytest.fixture
    def sample_transcript_long(self):
        """Longer transcript for testing"""
        return """
        Once upon a time, there was a brave explorer who ventured into the mysterious forest.
        The explorer discovered ancient artifacts and encountered fascinating creatures.
        Through perseverance and intelligence, the explorer solved complex puzzles and unlocked hidden secrets.
        The journey was challenging but ultimately rewarding.
        """
    
    def test_profiler_initialization(self, profiler):
        """Test that profiler initializes correctly"""
        assert profiler is not None
        assert profiler.nlp is not None
        assert profiler.dataset_loader is not None
    
    def test_analyze_short_transcript(self, profiler, sample_transcript_short):
        """Test analyzing a short transcript"""
        result = profiler.analyze_transcript(sample_transcript_short)
        
        assert 'word_scores' in result
        assert 'resonance_data' in result
        assert 'vocabulary_level' in result
        assert len(result['word_scores']) > 0
        assert result['resonance_data']['total_words'] > 0
        assert result['resonance_data']['unique_words'] > 0
    
    def test_analyze_long_transcript(self, profiler, sample_transcript_long):
        """Test analyzing a longer transcript"""
        result = profiler.analyze_transcript(sample_transcript_long)
        
        assert 'word_scores' in result
        assert 'resonance_data' in result
        assert 'vocabulary_level' in result
        assert result['resonance_data']['unique_words'] > 5
        assert result['resonance_data']['total_words'] > 20
    
    def test_vocabulary_level_calculation(self, profiler, sample_transcript_long):
        """Test that vocabulary level is calculated"""
        result = profiler.analyze_transcript(sample_transcript_long)
        
        assert result['vocabulary_level'] is not None
        assert isinstance(result['vocabulary_level'], str)
        assert len(result['vocabulary_level']) > 0
    
    def test_word_scores_structure(self, profiler, sample_transcript_short):
        """Test that word scores have correct structure"""
        result = profiler.analyze_transcript(sample_transcript_short)
        
        for word, score_data in result['word_scores'].items():
            assert 'difficulty_score' in score_data
            assert 'relic_type' in score_data
            assert isinstance(score_data['difficulty_score'], (int, float))
            assert score_data['difficulty_score'] >= 0
            assert score_data['difficulty_score'] <= 100
    
    def test_resonance_data_structure(self, profiler, sample_transcript_long):
        """Test that resonance data has all required fields"""
        result = profiler.analyze_transcript(sample_transcript_long)
        resonance = result['resonance_data']
        
        assert 'vocabulary_level' in resonance
        assert 'total_words' in resonance
        assert 'unique_words' in resonance
        assert 'relic_distribution' in resonance
        assert 'complexity_score' in resonance
        assert 'lexical_diversity' in resonance
    
    def test_empty_transcript_error(self, profiler):
        """Test that empty transcript raises error"""
        with pytest.raises(ValueError, match="too short"):
            profiler.analyze_transcript("")
    
    def test_very_short_transcript_error(self, profiler):
        """Test that very short transcript raises error"""
        with pytest.raises(ValueError, match="too short"):
            profiler.analyze_transcript("hi")
    
    def test_relic_distribution(self, profiler, sample_transcript_long):
        """Test that relic distribution is calculated"""
        result = profiler.analyze_transcript(sample_transcript_long)
        distribution = result['resonance_data']['relic_distribution']
        
        assert isinstance(distribution, dict)
        assert 'whisper' in distribution or 'echo' in distribution or 'resonance' in distribution or 'thunder' in distribution


class TestDatasetLoader:
    """Test suite for DatasetLoader"""
    
    @pytest.fixture
    def dataset_loader(self):
        """Create a dataset loader instance"""
        return DatasetLoader()
    
    def test_dataset_loader_initialization(self, dataset_loader):
        """Test that dataset loader initializes"""
        assert dataset_loader is not None
        assert hasattr(dataset_loader, 'coca_data')
        assert hasattr(dataset_loader, 'lexile_data')
    
    def test_get_word_frequency(self, dataset_loader):
        """Test getting word frequency"""
        # Test with common word
        freq = dataset_loader.get_word_frequency("the")
        assert isinstance(freq, int)
        assert freq >= 0
    
    def test_get_lexile_score(self, dataset_loader):
        """Test getting lexile score"""
        score = dataset_loader.get_lexile_score("the")
        # Score might be None if word not in dataset
        if score is not None:
            assert isinstance(score, int)
    
    def test_calculate_difficulty_score(self, dataset_loader):
        """Test difficulty score calculation"""
        difficulty, relic_type = dataset_loader.calculate_difficulty_score("the")
        
        assert isinstance(difficulty, int)
        assert 0 <= difficulty <= 100
        assert relic_type in ['whisper', 'echo', 'resonance', 'thunder']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

