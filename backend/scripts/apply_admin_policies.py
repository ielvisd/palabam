#!/usr/bin/env python3
"""
Apply Admin Policies Migration
Executes the admin policies SQL using Supabase client
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.supabase_client import get_supabase_client

# Read the migration SQL
MIGRATION_SQL = """
-- Admin Role Policies
-- Allows admin users to access all data across the system

-- Admin can view all users
CREATE POLICY IF NOT EXISTS "Admins can view all users"
    ON public.users FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can update all users
CREATE POLICY IF NOT EXISTS "Admins can update all users"
    ON public.users FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all students
CREATE POLICY IF NOT EXISTS "Admins can view all students"
    ON public.students FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can update all students
CREATE POLICY IF NOT EXISTS "Admins can update all students"
    ON public.students FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all teachers
CREATE POLICY IF NOT EXISTS "Admins can view all teachers"
    ON public.teachers FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all profiles
CREATE POLICY IF NOT EXISTS "Admins can view all profiles"
    ON public.profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all SRS progress
CREATE POLICY IF NOT EXISTS "Admins can view all SRS progress"
    ON public.srs_progress FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all sessions
CREATE POLICY IF NOT EXISTS "Admins can view all sessions"
    ON public.sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all quests
CREATE POLICY IF NOT EXISTS "Admins can view all quests"
    ON public.quests FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all submissions (from story spark)
CREATE POLICY IF NOT EXISTS "Admins can view all submissions"
    ON public.submissions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all student progress
CREATE POLICY IF NOT EXISTS "Admins can view all student progress"
    ON public.student_progress FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all achievements
CREATE POLICY IF NOT EXISTS "Admins can view all achievements"
    ON public.achievements FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all classes
CREATE POLICY IF NOT EXISTS "Admins can view all classes"
    ON public.classes FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all invites
CREATE POLICY IF NOT EXISTS "Admins can view all invites"
    ON public.invites FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admin can view all parents
CREATE POLICY IF NOT EXISTS "Admins can view all parents"
    ON public.parents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.users
            WHERE id = auth.uid() AND role = 'admin'
        )
    );
"""

def apply_migration():
    """Apply the admin policies migration"""
    try:
        print("Connecting to Supabase...")
        client = get_supabase_client()
        
        print("Applying admin policies migration...")
        print("This may take a moment...")
        
        # Execute the SQL using RPC or direct SQL execution
        # Note: Supabase Python client doesn't have direct SQL execution
        # We need to use the REST API or psql
        # For now, let's try using the REST API via the client
        
        # Split SQL into individual statements
        statements = [s.strip() for s in MIGRATION_SQL.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"Executing {len(statements)} policy creation statements...")
        
        # Use Supabase's REST API to execute SQL
        # We'll need to use the service role key to execute raw SQL
        import os
        import requests
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment")
            return False
        
        # Execute SQL via REST API
        # Supabase doesn't expose direct SQL execution via REST, so we need to use psql
        # or the Supabase CLI, or create a migration file
        
        print("\n⚠️  Direct SQL execution via Python client is limited.")
        print("Please use one of these methods:")
        print("\n1. Supabase Dashboard:")
        print("   - Go to SQL Editor")
        print("   - Copy the SQL from supabase/migrations/010_admin_policies.sql")
        print("   - Execute it")
        print("\n2. Supabase CLI:")
        print("   supabase db push")
        print("\n3. psql (if you have connection string):")
        print("   psql <connection_string> -f supabase/migrations/010_admin_policies.sql")
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)



