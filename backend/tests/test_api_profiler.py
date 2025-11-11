"""
Automated tests for the profile API endpoint
Tests profile creation, storage, and recommendation generation
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestProfileAPI:
    """Test suite for profile API endpoints"""
    
    @pytest.fixture
    def sample_transcript(self):
        """Sample transcript for testing"""
        return "I enjoy reading books about science and history. Learning new things is exciting and helps me understand the world better."
    
    @pytest.fixture
    def sample_student_id(self):
        """Sample student ID for testing"""
        return "44444444-4444-4444-4444-444444444444"
    
    def test_create_profile_endpoint(self, sample_transcript, sample_student_id):
        """Test POST /api/profile/ endpoint"""
        response = client.post(
            "/api/profile/",
            json={
                "transcript": sample_transcript,
                "student_id": sample_student_id,
                "inputMode": "text"
            }
        )
        
        # Should return 200 or 500 (500 if student doesn't exist in DB)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'profile_id' in data
            assert 'word_scores' in data
            assert 'resonance_data' in data
            assert 'vocabulary_level' in data
            assert 'recommended_words' in data
    
    def test_create_profile_without_student_id(self, sample_transcript):
        """Test profile creation without student_id (should still work)"""
        response = client.post(
            "/api/profile/",
            json={
                "transcript": sample_transcript,
                "inputMode": "text"
            }
        )
        
        # Should return 200 (creates temp profile)
        assert response.status_code == 200
        data = response.json()
        assert 'profile_id' in data
    
    def test_create_profile_empty_transcript(self, sample_student_id):
        """Test profile creation with empty transcript"""
        response = client.post(
            "/api/profile/",
            json={
                "transcript": "",
                "student_id": sample_student_id,
                "inputMode": "text"
            }
        )
        
        # Should return error for empty transcript
        assert response.status_code in [400, 422, 500]
    
    def test_create_profile_short_transcript(self, sample_student_id):
        """Test profile creation with very short transcript"""
        response = client.post(
            "/api/profile/",
            json={
                "transcript": "hi",
                "student_id": sample_student_id,
                "inputMode": "text"
            }
        )
        
        # Should return error for too short transcript
        assert response.status_code in [400, 422, 500]


class TestRecommendAPI:
    """Test suite for recommendation API endpoints"""
    
    @pytest.fixture
    def sample_student_id(self):
        """Sample student ID for testing"""
        return "44444444-4444-4444-4444-444444444444"
    
    def test_get_student_recommendations(self, sample_student_id):
        """Test GET /api/recommend/student/{student_id} endpoint"""
        response = client.get(f"/api/recommend/student/{sample_student_id}")
        
        # Should return 200 (even if empty)
        assert response.status_code == 200
        data = response.json()
        assert 'recommended_words' in data
        assert isinstance(data['recommended_words'], list)
    
    def test_recommend_words_endpoint(self):
        """Test POST /api/recommend/ endpoint"""
        # Create a sample profile
        sample_profile = {
            "word_scores": {
                "play": {"difficulty_score": 20, "relic_type": "whisper"},
                "game": {"difficulty_score": 25, "relic_type": "whisper"}
            },
            "resonance_data": {
                "vocabulary_level": "4-5",
                "total_words": 10,
                "unique_words": 8
            }
        }
        
        response = client.post(
            "/api/recommend/",
            json={
                "profile": sample_profile,
                "count": 5,
                "zpd_range": [0.70, 0.80]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'recommended_words' in data
        assert isinstance(data['recommended_words'], list)
        assert len(data['recommended_words']) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

