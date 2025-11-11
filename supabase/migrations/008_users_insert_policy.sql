-- Allow users to create their own user record
-- This is needed for signup flows where users create their own records

DROP POLICY IF EXISTS "Users can create their own record" ON public.users;
CREATE POLICY "Users can create their own record"
    ON public.users FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Also allow users to create their own teacher/student/parent records
-- This is needed for signup flows

DROP POLICY IF EXISTS "Users can create their own teacher record" ON public.teachers;
CREATE POLICY "Users can create their own teacher record"
    ON public.teachers FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own student record" ON public.students;
CREATE POLICY "Users can create their own student record"
    ON public.students FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create their own parent record" ON public.parents;
CREATE POLICY "Users can create their own parent record"
    ON public.parents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

