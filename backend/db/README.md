# Database Integration Module

This module handles all Supabase database operations for Palabam.

## Structure

- `supabase_client.py` - Supabase client initialization
- `profiles.py` - Relic resonance profile operations
- `words.py` - Vocabulary word operations
- `srs.py` - Spaced repetition system operations
- `sessions.py` - Session tracking operations

## Setup

1. **Configure Environment Variables**:
   Create `backend/.env` file:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_service_role_key
   ```

2. **Apply Database Migrations**:
   ```bash
   # Using Supabase CLI
   supabase db push
   
   # Or manually run migrations from supabase/migrations/
   ```

3. **Test Connection**:
   ```bash
   python3 scripts/test_db_connection.py
   ```

4. **Seed Words Database** (optional):
   ```bash
   python3 scripts/seed_words.py --limit 1000
   ```

## Usage

### Profiles
```python
from db import profiles as db_profiles

# Create profile
profile_id = await db_profiles.create_profile(
    student_id="...",
    resonance_data={...},
    word_scores={...}
)

# Get profile
profile = await db_profiles.get_profile(profile_id)
```

### Words
```python
from db import words as db_words

# Get word
word = await db_words.get_word("resilient")

# Search words
results = await db_words.search_words(
    min_difficulty=30,
    max_difficulty=70,
    limit=50
)
```

### SRS Progress
```python
from db import srs as db_srs

# Get progress
progress = await db_srs.get_srs_progress(student_id, word_id)

# Update progress
await db_srs.upsert_srs_progress(
    student_id="...",
    word_id="...",
    ease_factor=2.5,
    interval=6,
    repetitions=1,
    due_date=date.today()
)
```

## Integration Status

✅ **Profiles**: Fully integrated
✅ **Words**: Fully integrated  
✅ **SRS Progress**: Fully integrated
✅ **Sessions**: Ready to use

All backend endpoints now use real database operations instead of placeholders!

