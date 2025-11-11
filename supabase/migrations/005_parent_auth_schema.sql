-- Parent Authentication Schema
-- Adds parents table, parent-student relationships, and RLS policies

-- Update users.role to include 'parent'
ALTER TABLE public.users 
DROP CONSTRAINT IF EXISTS users_role_check;

ALTER TABLE public.users 
ADD CONSTRAINT users_role_check 
CHECK (role IN ('student', 'teacher', 'admin', 'parent'));

-- Parents table (similar structure to teachers)
CREATE TABLE IF NOT EXISTS public.parents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Parent-Students junction table (many-to-many relationship)
-- Supports multiple parents per student and multiple students per parent
CREATE TABLE IF NOT EXISTS public.parent_students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID NOT NULL REFERENCES public.parents(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(parent_id, student_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_parents_user_id ON public.parents(user_id);
CREATE INDEX IF NOT EXISTS idx_parent_students_parent_id ON public.parent_students(parent_id);
CREATE INDEX IF NOT EXISTS idx_parent_students_student_id ON public.parent_students(student_id);

-- Apply updated_at trigger for parents
CREATE TRIGGER update_parents_updated_at BEFORE UPDATE ON public.parents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS on new tables
ALTER TABLE public.parents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.parent_students ENABLE ROW LEVEL SECURITY;

-- Parents can view their own profile
CREATE POLICY "Parents can view their own profile"
    ON public.parents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Parents can update their own profile"
    ON public.parents FOR UPDATE
    USING (auth.uid() = user_id);

-- Parents can view their children's student records (via parent_students junction)
CREATE POLICY "Parents can view their children"
    ON public.students FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = students.id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view parent_students relationships for their own children
CREATE POLICY "Parents can view their parent_students links"
    ON public.parent_students FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parents
            WHERE id = parent_students.parent_id 
            AND user_id = auth.uid()
        )
    );

-- Parents can create parent_students links (when linking students)
CREATE POLICY "Parents can link students"
    ON public.parent_students FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.parents
            WHERE id = parent_students.parent_id 
            AND user_id = auth.uid()
        )
    );

-- Parents can view their children's profiles
CREATE POLICY "Parents can view their children's profiles"
    ON public.profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = profiles.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's SRS progress
CREATE POLICY "Parents can view their children's SRS progress"
    ON public.srs_progress FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = srs_progress.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's sessions
CREATE POLICY "Parents can view their children's sessions"
    ON public.sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = sessions.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's quests
CREATE POLICY "Parents can view their children's quests"
    ON public.quests FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = quests.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's submissions (from story spark schema)
CREATE POLICY "Parents can view their children's submissions"
    ON public.submissions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = submissions.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's student progress
CREATE POLICY "Parents can view their children's student progress"
    ON public.student_progress FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = student_progress.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's achievements
CREATE POLICY "Parents can view their children's achievements"
    ON public.achievements FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = achievements.student_id 
            AND p.user_id = auth.uid()
        )
    );

-- Parents can view their children's class memberships
CREATE POLICY "Parents can view their children's class memberships"
    ON public.class_students FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = class_students.student_id 
            AND p.user_id = auth.uid()
        )
    );

