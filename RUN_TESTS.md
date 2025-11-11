# How to Run Tests

## Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**If you see errors:**
- Missing dependencies: `pip install -r requirements.txt`
- Database errors: Check your `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`
- Import errors: Check that all files are in place

## Step 2: Run API Tests (in a NEW terminal)

Keep the backend running, open a NEW terminal:

```bash
cd /Users/elvisibarra/Documents/GauntletAI/palabam
./test.sh
```

Or run directly:
```bash
cd backend/scripts
python3 test_api.py
```

## Step 3: Manual Frontend Testing

In a THIRD terminal, start the frontend:

```bash
cd frontend
pnpm dev
```

Then open http://localhost:3000 in your browser and test:
1. Go to `/dashboard` → Create a class
2. Go to `/join-class` → Join with the class code
3. Go to `/story-spark` → Submit a story
4. Go to `/student/dashboard` → Check progress

## Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.8+)
python3 --version

# Install dependencies
cd backend
pip install -r requirements.txt

# Check for .env file
ls -la .env

# Try starting with more verbose output
python3 -m uvicorn main:app --reload --port 8000 --log-level debug
```

### Tests fail with connection error
- Make sure backend is running (check http://localhost:8000/health)
- Wait a few seconds after starting backend
- Check firewall isn't blocking port 8000

### Import errors in backend
```bash
cd backend
python3 -c "from api import classes, submissions, students; print('Imports OK')"
```

### Database connection issues
- Verify Supabase credentials in `.env`
- Check database migrations are applied
- Test connection: `python3 scripts/test_db_connection.py`

## Quick Health Check

Test if everything is working:

```bash
# Terminal 1: Backend
cd backend && python3 -m uvicorn main:app --reload --port 8000

# Terminal 2: Test
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

curl http://localhost:8000/
# Should return: {"message":"Palabam API is running","version":"1.0.0"}
```

## Expected Test Results

When tests pass, you should see:
```
✅ Health check passed
✅ Class created: Test Class - API Test with code ABC123
✅ Class found: Test Class - API Test
✅ Student joined: Successfully joined class
✅ Story submitted
   Vocabulary Level: intermediate
   Recommended Words: 7
✅ Progress retrieved
   Level: intermediate
   Streak: 1 days
   Stories: 1
✅ ALL TESTS PASSED!
```

