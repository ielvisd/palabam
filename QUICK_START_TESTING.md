# Quick Start Testing Guide

## Step 1: Start the Backend

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 2: Start the Frontend (in a new terminal)

```bash
cd frontend
pnpm dev
```

You should see:
```
Nuxt is ready on http://localhost:3000
```

## Step 3: Run API Tests

In a third terminal:

```bash
# Option 1: Use the test script
./test.sh

# Option 2: Run Python test directly
cd backend/scripts
python3 test_api.py
```

## Step 4: Manual Testing

1. **Open browser**: http://localhost:3000

2. **Test Teacher Flow**:
   - Go to `/dashboard`
   - Click "Create Class"
   - Enter class name, create class
   - Copy the class code

3. **Test Student Flow**:
   - Go to `/join-class` (or open in incognito/new browser)
   - Enter the class code
   - Enter student name
   - Join class

4. **Test Story Spark**:
   - Go to `/story-spark`
   - Type or speak a story (min 10 words)
   - Submit and see recommendations

5. **Test Student Dashboard**:
   - Go to `/student/dashboard`
   - View progress, achievements, recommendations

## Common Issues

### Backend won't start
- Check if port 8000 is already in use
- Verify Python dependencies: `pip install -r requirements.txt`
- Check Supabase credentials in `.env`

### Frontend won't start
- Check if port 3000 is in use
- Install dependencies: `pnpm install`
- Check Node.js version (should be 18+)

### API tests fail
- Ensure backend is running first
- Check database connection
- Verify migrations are applied

### Voice input doesn't work
- Use Chrome or Edge browser
- Check microphone permissions
- Try text mode as fallback

## Next Steps

1. Follow `TESTING_GUIDE.md` for detailed scenarios
2. Use `TEST_CHECKLIST.md` for systematic testing
3. Document any bugs found
4. Test on mobile devices if possible

## Quick Verification

Run these commands to verify setup:

```bash
# Check backend health
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# Check frontend
curl http://localhost:3000

# Should return HTML
```

