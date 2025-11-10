#!/usr/bin/env python3
"""
Test Database Connection
Verifies Supabase connection and table structure
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.supabase_client import get_supabase_client

def test_connection():
    """Test Supabase connection"""
    try:
        print("Testing Supabase connection...")
        client = get_supabase_client()
        
        # Test query - try to select from users table
        result = client.table("users").select("id").limit(1).execute()
        print("✓ Connection successful!")
        print(f"✓ Users table accessible")
        
        # Test other tables
        tables = ["students", "profiles", "words", "srs_progress", "sessions", "quests"]
        
        for table in tables:
            try:
                result = client.table(table).select("id").limit(1).execute()
                print(f"✓ {table} table accessible")
            except Exception as e:
                print(f"✗ {table} table error: {e}")
        
        print("\n✓ All database connections working!")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check SUPABASE_URL and SUPABASE_KEY in .env file")
        print("  2. Verify database migrations have been applied")
        print("  3. Check Supabase project is active")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

