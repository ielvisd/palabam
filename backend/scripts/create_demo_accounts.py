#!/usr/bin/env python3
"""
Create Demo Accounts Script
Creates demo teacher and student accounts using Supabase Admin API
"""
import sys
import os
from pathlib import Path
import requests
from typing import Dict, Any, Optional
from supabase import create_client

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.supabase_client import get_supabase_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_auth_user(email: str, password: str, user_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create an auth user using Supabase Admin API
    
    Args:
        email: User email
        password: User password (for demo accounts)
        user_metadata: Metadata to attach to user
        
    Returns:
        User data if successful, None otherwise
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    # Verify service role key format (should start with eyJ and be long)
    if not supabase_service_key.startswith("eyJ") or len(supabase_service_key) < 100:
        print(f"  ⚠️  WARNING: SUPABASE_KEY might not be a service role key.")
        print(f"     Service role keys are long JWT tokens (200+ chars).")
        print(f"     Current key length: {len(supabase_service_key)}")
        print(f"     Please verify you're using the SERVICE ROLE KEY, not the anon key.")
        print(f"     Get it from: Supabase Dashboard > Settings > API > service_role key")
    
    # Use direct HTTP API call (Python client doesn't support admin methods)
    # Ensure URL doesn't have trailing slash
    base_url = supabase_url.rstrip('/')
    admin_url = f"{base_url}/auth/v1/admin/users"
    headers = {
        "apikey": supabase_service_key,
        "Authorization": f"Bearer {supabase_service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Debug: Print first/last chars of key (don't print full key for security)
    print(f"  Using service role key (length: {len(supabase_service_key)}, starts with: {supabase_service_key[:10]}...)")
    
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,  # Auto-confirm email for demo accounts
        "user_metadata": user_metadata
    }
    
    try:
        response = requests.post(admin_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            # Handle both single user object and wrapped response
            if isinstance(result, dict) and "id" in result:
                return result
            elif isinstance(result, dict) and "user" in result:
                return result["user"]
            return result
        else:
            print(f"  Error response: {response.status_code} - {response.text}")
            # Try to parse error
            try:
                error_data = response.json()
                if error_data.get("error_code") == "not_admin":
                    print(f"\n  ❌ ERROR: The SUPABASE_KEY in your .env file is not a service role key!")
                    print(f"     The service role key is required for admin operations.")
                    print(f"     Get it from: Supabase Dashboard > Settings > API > service_role key")
                    print(f"     Make sure you're using the SERVICE_ROLE key, not the anon/public key.")
                    return None
                if "user_already_registered" in str(error_data) or error_data.get("code") == "user_already_registered":
                    # User already exists, try to get the user
                    print(f"  User already exists, attempting to retrieve...")
                    get_url = f"{supabase_url}/auth/v1/admin/users"
                    get_headers = {
                        "apikey": supabase_service_key,
                        "Authorization": f"Bearer {supabase_service_key}",
                    }
                    get_response = requests.get(
                        get_url,
                        headers=get_headers,
                        params={"email": email},
                        timeout=30
                    )
                    if get_response.status_code == 200:
                        result = get_response.json()
                        users = result.get("users", []) if isinstance(result, dict) else result
                        if isinstance(users, list) and users:
                            return users[0]
                        elif isinstance(users, dict) and "id" in users:
                            return users
            except Exception as parse_error:
                print(f"  Error parsing response: {parse_error}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  Error creating auth user {email}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None

def create_demo_teacher(email: str = "teacher@gauntlet.com", name: str = "Demo Teacher", password: str = "demo123456"):
    """
    Create a demo teacher account
    
    Args:
        email: Teacher email
        name: Teacher name
        password: Password for the account
    """
    print(f"\nCreating demo teacher account: {email}")
    
    supabase = get_supabase_client()
    
    # Check if user already exists
    existing_user = supabase.table("users").select("id, email").eq("email", email).execute()
    if existing_user.data:
        print(f"  ⚠️  User {email} already exists (ID: {existing_user.data[0]['id']})")
        user_id = existing_user.data[0]['id']
    else:
        # Create auth user
        print("  Creating auth user...")
        auth_user = create_auth_user(email, password, {"name": name, "role": "teacher"})
        
        if not auth_user:
            print(f"  ✗ Failed to create auth user for {email}")
            return False
        
        user_id = auth_user.get("id")
        print(f"  ✓ Auth user created (ID: {user_id})")
        
        # Create user record
        print("  Creating user record...")
        try:
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "role": "teacher"
            }).execute()
            print("  ✓ User record created")
        except Exception as e:
            print(f"  ⚠️  User record may already exist: {e}")
    
    # Check if teacher record exists
    existing_teacher = supabase.table("teachers").select("id").eq("user_id", user_id).execute()
    if existing_teacher.data:
        print(f"  ⚠️  Teacher record already exists (ID: {existing_teacher.data[0]['id']})")
        return True
    
    # Create teacher record
    print("  Creating teacher record...")
    try:
        teacher_result = supabase.table("teachers").insert({
            "user_id": user_id,
            "name": name
        }).execute()
        
        if teacher_result.data:
            print(f"  ✓ Teacher record created (ID: {teacher_result.data[0]['id']})")
            print(f"\n  ✅ Demo teacher account created successfully!")
            print(f"     Email: {email}")
            print(f"     Password: {password}")
            return True
        else:
            print("  ✗ Failed to create teacher record")
            return False
    except Exception as e:
        print(f"  ✗ Error creating teacher record: {e}")
        return False

def create_demo_student(email: str = "sally-sixth-grader@gauntlet.com", name: str = "Sally Sixth Grader", password: str = "demo123456"):
    """
    Create a demo student account
    
    Args:
        email: Student email
        name: Student name
        password: Password for the account
    """
    print(f"\nCreating demo student account: {email}")
    
    supabase = get_supabase_client()
    
    # Check if user already exists
    existing_user = supabase.table("users").select("id, email").eq("email", email).execute()
    if existing_user.data:
        print(f"  ⚠️  User {email} already exists (ID: {existing_user.data[0]['id']})")
        user_id = existing_user.data[0]['id']
    else:
        # Create auth user
        print("  Creating auth user...")
        auth_user = create_auth_user(email, password, {"name": name, "role": "student"})
        
        if not auth_user:
            print(f"  ✗ Failed to create auth user for {email}")
            return False
        
        user_id = auth_user.get("id")
        print(f"  ✓ Auth user created (ID: {user_id})")
        
        # Create user record
        print("  Creating user record...")
        try:
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "role": "student"
            }).execute()
            print("  ✓ User record created")
        except Exception as e:
            print(f"  ⚠️  User record may already exist: {e}")
    
    # Check if student record exists
    existing_student = supabase.table("students").select("id").eq("user_id", user_id).execute()
    if existing_student.data:
        print(f"  ⚠️  Student record already exists (ID: {existing_student.data[0]['id']})")
        return True
    
    # Create student record
    print("  Creating student record...")
    try:
        student_result = supabase.table("students").insert({
            "user_id": user_id,
            "name": name
        }).execute()
        
        if student_result.data:
            print(f"  ✓ Student record created (ID: {student_result.data[0]['id']})")
            print(f"\n  ✅ Demo student account created successfully!")
            print(f"     Email: {email}")
            print(f"     Password: {password}")
            return True
        else:
            print("  ✗ Failed to create student record")
            return False
    except Exception as e:
        print(f"  ✗ Error creating student record: {e}")
        return False

def main():
    """Main function to create demo accounts"""
    print("=" * 60)
    print("Creating Demo Accounts")
    print("=" * 60)
    
    # Create teacher account
    teacher_success = create_demo_teacher()
    
    # Create student account
    student_success = create_demo_student()
    
    print("\n" + "=" * 60)
    if teacher_success and student_success:
        print("✅ All demo accounts created successfully!")
        print("\nDemo Accounts (ready to use!):")
        print("  Teacher: teacher@gauntlet.com")
        print("           Password: demo123456")
        print("  Student: sally-sixth-grader@gauntlet.com")
        print("           Password: demo123456")
        print("\nNote: These demo accounts can sign in directly with password")
        print("      on the login page. Just enter the email and password!")
        return 0
    else:
        print("⚠️  Some accounts may not have been created.")
        print("    Check the output above for details.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

