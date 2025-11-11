-- Profiles and Recommendations Schema Enhancement
-- Adds missing fields to profiles table and creates recommendations tracking table

-- Enhance profiles table with missing fields
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS transcript TEXT,
ADD COLUMN IF NOT EXISTS vocabulary_level TEXT,
ADD COLUMN IF NOT EXISTS recommended_words JSONB DEFAULT '[]'::jsonb;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_student_id ON public.profiles(student_id);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON public.profiles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_vocabulary_level ON public.profiles(vocabulary_level);

-- Recommendations table for tracking recommended words
CREATE TABLE IF NOT EXISTS public.recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    word TEXT NOT NULL,
    definition TEXT,
    example TEXT,
    difficulty_score INTEGER,
    lexile_score INTEGER,
    coca_frequency INTEGER,
    relic_type TEXT CHECK (relic_type IN ('whisper', 'echo', 'resonance', 'thunder')),
    recommended_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'mastered', 'reviewed', 'dismissed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for recommendations
CREATE INDEX IF NOT EXISTS idx_recommendations_student_id ON public.recommendations(student_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_profile_id ON public.recommendations(profile_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON public.recommendations(status);
CREATE INDEX IF NOT EXISTS idx_recommendations_recommended_at ON public.recommendations(recommended_at DESC);

-- Apply updated_at trigger to recommendations
CREATE TRIGGER update_recommendations_updated_at BEFORE UPDATE ON public.recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS on recommendations
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Recommendations
-- Teachers can view recommendations for their students
CREATE POLICY "Teachers can view recommendations for their students"
    ON public.recommendations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.class_students cs
            JOIN public.classes c ON cs.class_id = c.id
            WHERE cs.student_id = recommendations.student_id
            AND c.teacher_id = (
                SELECT id FROM public.teachers WHERE user_id = auth.uid()
            )
        )
    );

-- Students can view their own recommendations
CREATE POLICY "Students can view their own recommendations"
    ON public.recommendations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = recommendations.student_id
            AND user_id = auth.uid()
        )
    );

-- Parents can view recommendations for their children
CREATE POLICY "Parents can view recommendations for their children"
    ON public.recommendations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.parent_students ps
            JOIN public.parents p ON ps.parent_id = p.id
            WHERE ps.student_id = recommendations.student_id
            AND p.user_id = auth.uid()
        )
    );

-- Teachers can update recommendation status
CREATE POLICY "Teachers can update recommendation status"
    ON public.recommendations FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.class_students cs
            JOIN public.classes c ON cs.class_id = c.id
            WHERE cs.student_id = recommendations.student_id
            AND c.teacher_id = (
                SELECT id FROM public.teachers WHERE user_id = auth.uid()
            )
        )
    );

-- Students can update their own recommendation status
CREATE POLICY "Students can update their own recommendation status"
    ON public.recommendations FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.students
            WHERE id = recommendations.student_id
            AND user_id = auth.uid()
        )
    );

-- Ensure profiles table has proper RLS (if not already set)
-- Teachers can view profiles for their students
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'profiles' 
        AND policyname = 'Teachers can view profiles for their students'
    ) THEN
        CREATE POLICY "Teachers can view profiles for their students"
            ON public.profiles FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM public.class_students cs
                    JOIN public.classes c ON cs.class_id = c.id
                    WHERE cs.student_id = profiles.student_id
                    AND c.teacher_id = (
                        SELECT id FROM public.teachers WHERE user_id = auth.uid()
                    )
                )
            );
    END IF;
END $$;

-- Students can view their own profiles
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'profiles' 
        AND policyname = 'Students can view their own profiles'
    ) THEN
        CREATE POLICY "Students can view their own profiles"
            ON public.profiles FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM public.students
                    WHERE id = profiles.student_id
                    AND user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- Parents can view profiles for their children
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'profiles' 
        AND policyname = 'Parents can view profiles for their children'
    ) THEN
        CREATE POLICY "Parents can view profiles for their children"
            ON public.profiles FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM public.parent_students ps
                    JOIN public.parents p ON ps.parent_id = p.id
                    WHERE ps.student_id = profiles.student_id
                    AND p.user_id = auth.uid()
                )
            );
    END IF;
END $$;

