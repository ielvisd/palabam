# Palabam Testing Guide

## Overview
This guide helps you test the Story Spark interactive experience and vocabulary recommendation engine end-to-end.

## Prerequisites

1. **Backend Running**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Frontend Running**
   ```bash
   cd frontend
   pnpm dev
   ```

3. **Database Setup**
   - Ensure Supabase is configured
   - Run migrations: `001_initial_schema.sql`, `002_row_level_security.sql`, `004_story_spark_schema.sql`
   - Set environment variables: `SUPABASE_URL`, `SUPABASE_KEY`

4. **NLP Models**
   ```bash
   cd backend
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords
   ```

## Test Scenarios

### 1. Teacher Class Creation Flow

**Steps:**
1. Navigate to `/dashboard` (educator dashboard)
2. Click "Create Class" button
3. Enter class name: "Test Class - 7th Grade"
4. Click "Create Class"
5. Verify success modal appears with class code
6. Copy the class code
7. Verify class appears in "My Classes" section

**Expected Results:**
- ✅ Class created successfully
- ✅ Unique 6-character code generated
- ✅ Code is copyable
- ✅ Class appears in dashboard

**API Test:**
```bash
curl -X POST http://localhost:8000/api/classes/ \
  -H "Content-Type: application/json" \
  -d '{"teacher_id": "test-teacher-1", "name": "Test Class"}'
```

### 2. Student Join Class Flow

**Steps:**
1. Navigate to `/join-class`
2. Enter the class code from step 1
3. Enter student name: "Test Student"
4. Click "Join Class"
5. Verify success message

**Expected Results:**
- ✅ Student successfully joins class
- ✅ Success message displayed
- ✅ Navigation options to Story Spark and Dashboard appear

**API Test:**
```bash
# First validate code
curl http://localhost:8000/api/classes/code/ABC123

# Then join
curl -X POST http://localhost:8000/api/classes/join \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC123", "student_id": "test-student-1", "student_name": "Test Student"}'
```

### 3. Story Spark Submission (Text Mode)

**Steps:**
1. Navigate to `/story-spark`
2. Ensure "Voice Mode" is OFF (text mode)
3. Read the story prompt
4. Type a story (minimum 10 words, e.g., "I had an amazing weekend. I went to the park with my friends. We played soccer and had a picnic. The weather was perfect and we laughed a lot.")
5. Click "Submit Story"
6. Wait for analysis
7. Verify results show:
   - Vocabulary level
   - Recommended words
   - Navigation to dashboard

**Expected Results:**
- ✅ Story submitted successfully
- ✅ Vocabulary level displayed (beginner/intermediate/advanced/expert)
- ✅ 5-7 recommended words shown
- ✅ Points awarded (10 + bonus for word count)

**API Test:**
```bash
curl -X POST http://localhost:8000/api/submissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-student-1",
    "type": "story-spark",
    "content": "I had an amazing weekend. I went to the park with my friends. We played soccer and had a picnic.",
    "source": "text"
  }'
```

### 4. Story Spark Submission (Voice Mode - Real-time)

**Steps:**
1. Navigate to `/story-spark`
2. Toggle "Voice Mode" ON
3. Ensure "Real-time" mode is selected
4. Click "Start Speaking"
5. Speak a story (e.g., "Tell me about your perfect day")
6. Watch text appear in real-time as you speak
7. Click "Stop Recording" when done
8. Verify transcript appears
9. Submit the story

**Expected Results:**
- ✅ Voice recognition works
- ✅ Text appears as you speak (real-time transcription)
- ✅ Transcript is accurate
- ✅ Can submit voice transcript

**Note:** Requires browser with Web Speech API support (Chrome, Edge, Safari)

### 5. Story Spark Submission (Voice Mode - Record)

**Steps:**
1. Navigate to `/story-spark`
2. Toggle "Voice Mode" ON
3. Switch to "Record" mode (if available)
4. Click "Start Recording"
5. Speak your story
6. Click "Stop Recording"
7. Wait for transcription
8. Verify transcript appears
9. Submit the story

**Expected Results:**
- ✅ Recording works
- ✅ Transcription appears after stopping
- ✅ Can edit transcript before submitting

### 6. Student Progress Dashboard

**Steps:**
1. After submitting at least one story, navigate to `/student/dashboard`
2. Verify the following sections:
   - Stats cards (Vocabulary Level, Day Streak, Stories Told, Points Earned)
   - Vocabulary Level progress bar
   - Recommended Words section
   - Achievements (if any earned)
   - Recent Stories list

**Expected Results:**
- ✅ All stats display correctly
- ✅ Vocabulary level matches submission result
- ✅ Recommended words appear
- ✅ Submission history shows previous stories
- ✅ Achievements appear if conditions met

**API Test:**
```bash
# Get progress
curl http://localhost:8000/api/students/test-student-1/progress

# Get recommendations
curl http://localhost:8000/api/students/test-student-1/recommendations

# Get achievements
curl http://localhost:8000/api/students/test-student-1/achievements

# Get submissions
curl http://localhost:8000/api/students/test-student-1/submissions
```

### 7. Educator Dashboard - View Students

**Steps:**
1. Navigate to `/dashboard` as teacher
2. Verify "My Classes" section shows created classes
3. Click "View Students" on a class
4. Verify students who joined are listed
5. Expand a student card
6. Verify recommended words appear
7. Test search/filter functionality

**Expected Results:**
- ✅ Classes listed with codes
- ✅ Student count accurate
- ✅ Can view students per class
- ✅ Student recommendations visible
- ✅ Search/filter works

### 8. File Upload (Student)

**Steps:**
1. Navigate to `/student/dashboard` or `/story-spark`
2. Look for file upload option (if implemented)
3. Upload a text file or document
4. Verify file is processed
5. Check recommendations appear

**API Test:**
```bash
curl -X POST http://localhost:8000/api/submissions/upload \
  -F "file=@test_essay.txt" \
  -F "student_id=test-student-1"
```

### 9. Achievement System

**Steps:**
1. Submit multiple stories (at least 1)
2. Check for "First Story" achievement
3. Submit stories on consecutive days for streak achievements
4. Write 1000+ words total for word count achievements
5. Verify achievements appear in student dashboard

**Expected Results:**
- ✅ "First Story" achievement after first submission
- ✅ Streak achievements after 7 and 30 days
- ✅ Word count achievements at milestones
- ✅ "Vocabulary Master" when reaching advanced level

### 10. Export Functionality

**Steps:**
1. Navigate to `/dashboard` as teacher
2. Ensure there are students with recommendations
3. Click "Export CSV"
4. Verify CSV file downloads
5. Open CSV and verify data is correct

**Expected Results:**
- ✅ CSV downloads successfully
- ✅ Contains student names, levels, recommended words
- ✅ Data is properly formatted

## Common Issues & Solutions

### Issue: "Speech recognition not supported"
**Solution:** Use Chrome, Edge, or Safari. Web Speech API requires HTTPS in production.

### Issue: "Class code not found"
**Solution:** Verify class was created successfully. Check database for class record.

### Issue: "No recommendations generated"
**Solution:** 
- Check backend logs for NLP processing errors
- Verify spaCy model is installed: `python -m spacy download en_core_web_sm`
- Ensure word database has entries

### Issue: "Student progress not updating"
**Solution:**
- Check database connection
- Verify student_id is consistent
- Check backend logs for errors

### Issue: "Voice transcription not working"
**Solution:**
- Check browser permissions for microphone
- Verify Web Speech API is available
- Try text mode as fallback

## Performance Testing

### Load Test
```bash
# Test multiple concurrent submissions
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/submissions/ \
    -H "Content-Type: application/json" \
    -d "{\"student_id\": \"student-$i\", \"type\": \"story-spark\", \"content\": \"Test story $i\", \"source\": \"text\"}" &
done
wait
```

### Response Time Targets
- Class creation: < 500ms
- Story submission: < 3s (includes NLP analysis)
- Dashboard load: < 2s
- Recommendations: < 1s

## Database Verification

```sql
-- Check classes
SELECT * FROM classes;

-- Check students
SELECT * FROM students;

-- Check submissions
SELECT * FROM submissions ORDER BY created_at DESC LIMIT 10;

-- Check progress
SELECT * FROM student_progress;

-- Check achievements
SELECT * FROM achievements;
```

## Next Steps After Testing

1. **Fix any bugs found**
2. **Improve error messages** based on user feedback
3. **Optimize slow endpoints**
4. **Add missing features** identified during testing
5. **Document edge cases** discovered

