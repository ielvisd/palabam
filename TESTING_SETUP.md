# Testing Setup Guide

## Database Setup

The Palabam API requires proper Supabase Auth users to create teachers and students. The database has foreign key constraints that prevent creating test data without valid auth.users entries.

## Setting Up Test Data

### Option 1: Use Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to Authentication > Users
3. Create test users:
   - Teacher: `test-teacher@palabam.test`
   - Student: `test-student@palabam.test`
4. Note the user IDs from the auth.users table
5. Manually create teacher and student records in the database:

```sql
-- Replace USER_ID_FROM_AUTH with actual user ID from auth.users
INSERT INTO public.teachers (id, user_id, name)
VALUES (
    '22222222-2222-2222-2222-222222222222'::uuid,
    'USER_ID_FROM_AUTH'::uuid,
    'Test Teacher'
);

INSERT INTO public.students (id, user_id, name)
VALUES (
    '44444444-4444-4444-4444-444444444444'::uuid,
    'USER_ID_FROM_AUTH'::uuid,
    'Test Student'
);
```

### Option 2: Use Supabase Auth API

You can programmatically create users using the Supabase Auth API, then create teacher/student records.

### Option 3: Test Without Full Setup

Some endpoints can be tested without full user setup:
- Health check: `/health`
- Class lookup by code: `/api/classes/code/{code}` (if class exists)

## Running Tests

Once test users are set up:

```bash
cd backend/scripts
python3 test_api.py
```

## Current Limitations

- Class creation requires an existing teacher record
- Student submissions require an existing student record
- All foreign key constraints are enforced at the database level

## Future Improvements

- Add a test mode that uses service role key to bypass RLS
- Create a test data seeding script that uses Supabase Auth API
- Add database migrations for test data setup

