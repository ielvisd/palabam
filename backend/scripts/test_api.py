"""
Quick API Testing Script
Tests all Story Spark endpoints
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")
    return response.json()

def test_create_class(teacher_id: str = "test-teacher-1") -> Dict[str, Any]:
    """Test class creation"""
    print("\nTesting class creation...")
    response = requests.post(
        f"{BASE_URL}/api/classes/",
        json={"teacher_id": teacher_id, "name": "Test Class - API Test"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Class created: {data['name']} with code {data['code']}")
    return data

def test_get_class_by_code(code: str):
    """Test getting class by code"""
    print(f"\nTesting get class by code: {code}...")
    response = requests.get(f"{BASE_URL}/api/classes/code/{code}")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Class found: {data['name']}")
    return data

def test_join_class(code: str, student_id: str = "test-student-1", student_name: str = "Test Student"):
    """Test student joining class"""
    print(f"\nTesting student join class...")
    response = requests.post(
        f"{BASE_URL}/api/classes/join",
        json={"code": code, "student_id": student_id, "student_name": student_name}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Student joined: {data['message']}")
    return data

def test_submit_story(student_id: str, story_text: str = None):
    """Test story submission"""
    if story_text is None:
        story_text = "I had an amazing weekend. I went to the park with my friends. We played soccer and had a picnic. The weather was perfect and we laughed a lot. It was a wonderful day filled with joy and excitement."
    
    print(f"\nTesting story submission...")
    print(f"Story length: {len(story_text.split())} words")
    
    response = requests.post(
        f"{BASE_URL}/api/submissions/",
        json={
            "student_id": student_id,
            "type": "story-spark",
            "content": story_text,
            "source": "text"
        }
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Story submitted")
    print(f"   Vocabulary Level: {data.get('vocabulary_level', 'N/A')}")
    print(f"   Recommended Words: {len(data.get('recommended_words', []))}")
    print(f"   Words: {', '.join(data.get('recommended_words', [])[:5])}")
    return data

def test_get_student_progress(student_id: str):
    """Test getting student progress"""
    print(f"\nTesting get student progress...")
    response = requests.get(f"{BASE_URL}/api/students/{student_id}/progress")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Progress retrieved")
    print(f"   Level: {data.get('vocabulary_level', 'N/A')}")
    print(f"   Streak: {data.get('current_streak', 0)} days")
    print(f"   Stories: {data.get('submission_count', 0)}")
    print(f"   Points: {data.get('total_points', 0)}")
    print(f"   Words Written: {data.get('total_words_written', 0)}")
    return data

def test_get_recommendations(student_id: str):
    """Test getting recommendations"""
    print(f"\nTesting get recommendations...")
    response = requests.get(f"{BASE_URL}/api/students/{student_id}/recommendations")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Recommendations retrieved: {len(data.get('recommended_words', []))} words")
    return data

def test_get_achievements(student_id: str):
    """Test getting achievements"""
    print(f"\nTesting get achievements...")
    response = requests.get(f"{BASE_URL}/api/students/{student_id}/achievements")
    assert response.status_code == 200
    data = response.json()
    achievements = data.get('achievements', [])
    print(f"✅ Achievements retrieved: {len(achievements)} earned")
    for ach in achievements[:5]:
        print(f"   - {ach.get('achievement_type', 'N/A')}")
    return data

def test_get_submissions(student_id: str):
    """Test getting submission history"""
    print(f"\nTesting get submissions...")
    response = requests.get(f"{BASE_URL}/api/students/{student_id}/submissions")
    assert response.status_code == 200
    data = response.json()
    submissions = data.get('submissions', [])
    print(f"✅ Submissions retrieved: {len(submissions)} total")
    return data

def run_full_test_flow():
    """Run complete test flow"""
    print("=" * 60)
    print("PALABAM API TEST SUITE")
    print("=" * 60)
    
    try:
        # 1. Health check
        test_health()
        
        # 2. Create class
        class_data = test_create_class()
        class_code = class_data['code']
        class_id = class_data['id']
        
        # 3. Get class by code
        test_get_class_by_code(class_code)
        
        # 4. Join class
        student_id = "test-student-api"
        test_join_class(class_code, student_id, "API Test Student")
        
        # 5. Submit story
        story = "I had an amazing weekend. I went to the park with my friends. We played soccer and had a picnic. The weather was perfect and we laughed a lot. It was a wonderful day filled with joy and excitement. I felt happy and grateful for such a great time."
        submission = test_submit_story(student_id, story)
        
        # Wait a bit for processing
        time.sleep(1)
        
        # 6. Get progress
        progress = test_get_student_progress(student_id)
        
        # 7. Get recommendations
        recommendations = test_get_recommendations(student_id)
        
        # 8. Get achievements
        achievements = test_get_achievements(student_id)
        
        # 9. Get submissions
        submissions = test_get_submissions(student_id)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_full_test_flow()
    exit(0 if success else 1)

