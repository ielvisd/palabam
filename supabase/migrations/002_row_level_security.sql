-- Row Level Security (RLS) Policies
-- Ensures users can only access their own data

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.srs_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quests ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view their own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Students policies
CREATE POLICY "Students can view their own data"
    ON public.students FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Students can update their own data"
    ON public.students FOR UPDATE
    USING (auth.uid() = user_id);

-- Teachers can view all students (for dashboard)
CREATE POLICY "Teachers can view all students"
    ON public.students FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teachers
            WHERE user_id = auth.uid()
        )
    );

-- Teachers policies
CREATE POLICY "Teachers can view their own data"
    ON public.teachers FOR SELECT
    USING (auth.uid() = user_id);

-- Profiles policies
CREATE POLICY "Students can view their own profiles"
    ON public.profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = profiles.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can create their own profiles"
    ON public.profiles FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = profiles.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can update their own profiles"
    ON public.profiles FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = profiles.student_id AND user_id = auth.uid()
        )
    );

-- Teachers can view all profiles
CREATE POLICY "Teachers can view all profiles"
    ON public.profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teachers
            WHERE user_id = auth.uid()
        )
    );

-- Words are publicly readable (vocabulary database)
CREATE POLICY "Anyone can view words"
    ON public.words FOR SELECT
    USING (true);

-- SRS progress policies
CREATE POLICY "Students can view their own SRS progress"
    ON public.srs_progress FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = srs_progress.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can insert their own SRS progress"
    ON public.srs_progress FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = srs_progress.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can update their own SRS progress"
    ON public.srs_progress FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = srs_progress.student_id AND user_id = auth.uid()
        )
    );

-- Teachers can view all SRS progress
CREATE POLICY "Teachers can view all SRS progress"
    ON public.srs_progress FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teachers
            WHERE user_id = auth.uid()
        )
    );

-- Sessions policies
CREATE POLICY "Students can view their own sessions"
    ON public.sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = sessions.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can create their own sessions"
    ON public.sessions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = sessions.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can update their own sessions"
    ON public.sessions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = sessions.student_id AND user_id = auth.uid()
        )
    );

-- Teachers can view all sessions
CREATE POLICY "Teachers can view all sessions"
    ON public.sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.teachers
            WHERE user_id = auth.uid()
        )
    );

-- Quests policies
CREATE POLICY "Students can view their own quests"
    ON public.quests FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = quests.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can create their own quests"
    ON public.quests FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = quests.student_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Students can update their own quests"
    ON public.quests FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = quests.student_id AND user_id = auth.uid()
        )
    );

