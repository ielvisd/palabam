# Palabam Testing Checklist

Use this checklist to systematically test all features.

## Setup ✅
- [ ] Backend server running on port 8000
- [ ] Frontend dev server running on port 3000
- [ ] Supabase database connected
- [ ] Migrations applied (001, 002, 004)
- [ ] NLP models installed (spaCy, NLTK)

## Core Features

### Teacher Features
- [ ] **Create Class**
  - [ ] Can create a new class
  - [ ] Class code is generated (6 characters)
  - [ ] Code is unique
  - [ ] Success modal shows code
  - [ ] Can copy code to clipboard
  - [ ] Class appears in "My Classes" section

- [ ] **View Classes**
  - [ ] All classes display correctly
  - [ ] Student count is accurate
  - [ ] Can view students in each class
  - [ ] Class codes are visible and copyable

- [ ] **View Students**
  - [ ] Students from classes appear in dashboard
  - [ ] Can expand student cards
  - [ ] Recommended words display for each student
  - [ ] Vocabulary levels are shown
  - [ ] Search/filter works

- [ ] **Export Data**
  - [ ] CSV export works
  - [ ] Exported data is correct
  - [ ] PDF export (if implemented)

### Student Features
- [ ] **Join Class**
  - [ ] Can enter class code
  - [ ] Code validation works
  - [ ] Can join with student name
  - [ ] Success message appears
  - [ ] Navigation to Story Spark works

- [ ] **Story Spark - Text Mode**
  - [ ] Prompt appears
  - [ ] Can type story
  - [ ] Word count updates
  - [ ] Can submit story (min 10 words)
  - [ ] Analysis completes
  - [ ] Vocabulary level shown
  - [ ] Recommended words appear
  - [ ] Points awarded

- [ ] **Story Spark - Voice Mode (Real-time)**
  - [ ] Can toggle voice mode
  - [ ] Can start recording
  - [ ] Text appears as speaking (real-time)
  - [ ] Can stop recording
  - [ ] Transcript is accurate
  - [ ] Can submit voice transcript

- [ ] **Story Spark - Voice Mode (Record)**
  - [ ] Can switch to record mode
  - [ ] Can record audio
  - [ ] Transcription appears after stopping
  - [ ] Can edit transcript
  - [ ] Can submit

- [ ] **Student Dashboard**
  - [ ] Vocabulary level displays
  - [ ] Day streak shows correctly
  - [ ] Story count is accurate
  - [ ] Points total is correct
  - [ ] Recommended words appear
  - [ ] Achievements show (if earned)
  - [ ] Submission history displays

- [ ] **File Upload** (if implemented)
  - [ ] Can upload file
  - [ ] File is processed
  - [ ] Recommendations generated

### System Features
- [ ] **Progress Tracking**
  - [ ] Vocabulary level updates after submission
  - [ ] Word count increments
  - [ ] Submission count increments
  - [ ] Streak calculates correctly
  - [ ] Points awarded correctly

- [ ] **Achievement System**
  - [ ] "First Story" awarded after first submission
  - [ ] Streak achievements (7 days, 30 days)
  - [ ] Word count achievements (1000, 5000)
  - [ ] "Vocabulary Master" at advanced level
  - [ ] Achievements appear in dashboard

- [ ] **Recommendations**
  - [ ] 5-7 words recommended per student
  - [ ] Words are ZPD-appropriate
  - [ ] Words include definitions/examples
  - [ ] Recommendations update with new submissions

## Edge Cases & Error Handling

- [ ] **Invalid Inputs**
  - [ ] Empty class name (should show error)
  - [ ] Invalid class code (should show error)
  - [ ] Story too short (< 10 words)
  - [ ] Empty student name

- [ ] **Network Errors**
  - [ ] Backend offline (should show error)
  - [ ] Slow connection (loading states work)
  - [ ] API errors (error messages appear)

- [ ] **Browser Compatibility**
  - [ ] Chrome (voice should work)
  - [ ] Firefox (text mode should work)
  - [ ] Safari (voice should work)
  - [ ] Mobile browsers

- [ ] **Data Persistence**
  - [ ] Classes persist after refresh
  - [ ] Student progress persists
  - [ ] Submissions are saved
  - [ ] Achievements persist

## Performance

- [ ] **Response Times**
  - [ ] Class creation < 500ms
  - [ ] Story submission < 3s
  - [ ] Dashboard load < 2s
  - [ ] Recommendations < 1s

- [ ] **Concurrent Users**
  - [ ] Multiple students can join same class
  - [ ] Multiple submissions process correctly
  - [ ] No data conflicts

## Mobile Testing

- [ ] **Responsive Design**
  - [ ] Dashboard works on mobile
  - [ ] Story Spark works on tablet
  - [ ] Touch targets are large enough
  - [ ] Voice input works on mobile

## Security

- [ ] **Data Access**
  - [ ] Students can only see their own data
  - [ ] Teachers can see their students
  - [ ] Class codes are unique
  - [ ] No unauthorized access

## Notes

Document any issues found:

### Issues Found:
1. 
2. 
3. 

### Suggestions:
1. 
2. 
3. 

---

**Test Date:** _______________
**Tester:** _______________
**Environment:** Development / Production

