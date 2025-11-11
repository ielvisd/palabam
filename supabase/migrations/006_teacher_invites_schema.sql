-- Teacher Invites Schema
-- Allows teachers to invite students via email or shareable links

-- Create invites table
CREATE TABLE IF NOT EXISTS public.invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_id UUID NOT NULL REFERENCES public.classes(id) ON DELETE CASCADE,
    code TEXT UNIQUE NOT NULL, -- Short unique code for shareable links
    teacher_id UUID NOT NULL REFERENCES public.teachers(id) ON DELETE CASCADE,
    email TEXT, -- Nullable - for email-based invites
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired')),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_invites_code ON public.invites(code);
CREATE INDEX IF NOT EXISTS idx_invites_class_id ON public.invites(class_id);
CREATE INDEX IF NOT EXISTS idx_invites_teacher_id ON public.invites(teacher_id);
CREATE INDEX IF NOT EXISTS idx_invites_email ON public.invites(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_invites_status ON public.invites(status);

-- Apply updated_at trigger
CREATE TRIGGER update_invites_updated_at BEFORE UPDATE ON public.invites
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.invites ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Invites
-- Teachers can view and manage invites for their own classes
CREATE POLICY "Teachers can view invites for their classes"
    ON public.invites FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.classes
            WHERE classes.id = invites.class_id
            AND classes.teacher_id = (
                SELECT id FROM public.teachers WHERE user_id = auth.uid()
            )
        )
    );

-- Teachers can create invites for their classes
CREATE POLICY "Teachers can create invites for their classes"
    ON public.invites FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.classes
            WHERE classes.id = invites.class_id
            AND classes.teacher_id = (
                SELECT id FROM public.teachers WHERE user_id = auth.uid()
            )
        )
        AND teacher_id = (
            SELECT id FROM public.teachers WHERE user_id = auth.uid()
        )
    );

-- Teachers can update invites for their classes
CREATE POLICY "Teachers can update invites for their classes"
    ON public.invites FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.classes
            WHERE classes.id = invites.class_id
            AND classes.teacher_id = (
                SELECT id FROM public.teachers WHERE user_id = auth.uid()
            )
        )
    );

-- Anyone can view invite details by code (for validation during signup)
CREATE POLICY "Anyone can view invite by code"
    ON public.invites FOR SELECT
    USING (true); -- Allow public read access for invite validation

-- Function to generate unique invite code
CREATE OR REPLACE FUNCTION generate_invite_code()
RETURNS TEXT AS $$
DECLARE
    chars TEXT := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; -- Exclude confusing chars (0, O, I, 1)
    result TEXT := '';
    i INTEGER;
BEGIN
    FOR i IN 1..8 LOOP
        result := result || substr(chars, floor(random() * length(chars) + 1)::integer, 1);
    END LOOP;
    
    -- Check if code already exists, regenerate if needed
    WHILE EXISTS (SELECT 1 FROM public.invites WHERE code = result) LOOP
        result := '';
        FOR i IN 1..8 LOOP
            result := result || substr(chars, floor(random() * length(chars) + 1)::integer, 1);
        END LOOP;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

