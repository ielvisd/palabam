#!/usr/bin/env python3
"""
Create Demo Student Account
Creates a demo student account (student@gauntlet.com) and links it to the teacher's first class
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.create_demo_accounts import create_demo_student, assign_student_to_class
from db.supabase_client import get_supabase_client
import asyncio
from db import classes as db_classes

def main():
    """Create demo student account and link to teacher's class"""
    print("=" * 60)
    print("Creating Demo Student Account")
    print("=" * 60)
    
    # Create student account
    student_id = create_demo_student(
        email="student@gauntlet.com",
        name="Demo Student",
        password="demo123456"
    )
    
    if not student_id:
        print("\n❌ Failed to create student account.")
        return 1
    
    # Get teacher's first class
    supabase = get_supabase_client()
    
    # Find teacher by email
    teacher_user = supabase.table("users").select("id").eq("email", "teacher@gauntlet.com").execute()
    if not teacher_user.data:
        print("\n❌ Teacher account not found.")
        return 1
    
    teacher_user_id = teacher_user.data[0]["id"]
    
    # Get teacher record
    teacher_record = supabase.table("teachers").select("id").eq("user_id", teacher_user_id).execute()
    if not teacher_record.data:
        print("\n❌ Teacher record not found.")
        return 1
    
    teacher_id = teacher_record.data[0]["id"]
    
    # Get teacher's first class
    classes_result = supabase.table("classes").select("id, name").eq("teacher_id", teacher_id).order("created_at", desc=False).limit(1).execute()
    
    if not classes_result.data:
        print("\n⚠️  No classes found for teacher. Creating a default class...")
        # Create a default class
        class_data = asyncio.run(db_classes.create_class(teacher_id, "Demo Class"))
        if not class_data:
            print("\n❌ Failed to create class.")
            return 1
        class_id = class_data["id"]
        print(f"✓ Created class: {class_data['name']} (Code: {class_data['code']})")
    else:
        class_id = classes_result.data[0]["id"]
        class_name = classes_result.data[0]["name"]
        print(f"\n✓ Found class: {class_name}")
    
    # Assign student to class
    print(f"\nAssigning student to class...")
    success = assign_student_to_class(class_id, student_id)
    
    if success:
        print(f"✓ Student assigned to class successfully")
    else:
        print(f"⚠️  Student may already be in class or assignment failed")
    
    print("\n" + "=" * 60)
    print("✅ Demo Student Account Created!")
    print("=" * 60)
    print("\nDemo Student Account:")
    print("  Email: student@gauntlet.com")
    print("  Password: demo123456")
    print(f"  Linked to class: {classes_result.data[0]['name'] if classes_result.data else 'Demo Class'}")
    print("\nNote: This account can sign in directly with password")
    print("      on the login page. Just enter the email and password!")
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

