-- Migration to fix user ID mismatch for teacher@gauntlet.com
-- This fixes the data inconsistency where auth.users and public.users have different IDs

-- Step 1: Temporarily change the old user record's email to allow creating the new one
UPDATE public.users
SET email = 'teacher@gauntlet.com.old_' || id::text
WHERE id = '5d518340-ff7d-4c6b-baed-fe2fd4db6ec9';

-- Step 2: Create the new user record with the correct ID
INSERT INTO public.users (id, email, role)
VALUES ('048458a7-73e2-4f45-aa06-e2a2f2b73237', 'teacher@gauntlet.com', 'teacher')
ON CONFLICT (id) DO UPDATE
SET email = EXCLUDED.email,
    role = EXCLUDED.role;

-- Step 3: Update teacher record to use the correct user_id
-- Old user_id: 5d518340-ff7d-4c6b-baed-fe2fd4db6ec9
-- New user_id: 048458a7-73e2-4f45-aa06-e2a2f2b73237
UPDATE public.teachers
SET user_id = '048458a7-73e2-4f45-aa06-e2a2f2b73237'
WHERE user_id = '5d518340-ff7d-4c6b-baed-fe2fd4db6ec9';

-- Step 4: Update any student records that might be using the old user_id
UPDATE public.students
SET user_id = '048458a7-73e2-4f45-aa06-e2a2f2b73237'
WHERE user_id = '5d518340-ff7d-4c6b-baed-fe2fd4db6ec9';

-- Step 5: Delete the old user record (now safe since all foreign keys are updated)
DELETE FROM public.users
WHERE id = '5d518340-ff7d-4c6b-baed-fe2fd4db6ec9';

