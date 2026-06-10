"""
Debug user registration and phone number fetching
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.user_management import user_manager
from database.models import User, SessionLocal
from services.sms_service import sms_service

def debug_user_database():
    """Debug user registration and phone number issues"""
    print("🔍 ResQAlert User Database Debug")
    print("=" * 50)
    
    # Test 1: Check database connection
    try:
        db = SessionLocal()
        print("✅ Database connection: SUCCESS")
        db.close()
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return
    
    # Test 2: Get all users using user_manager
    print("\n👥 Testing User Manager...")
    try:
        all_users = user_manager.get_all_users()
        print(f"✅ Found {len(all_users)} users via user_manager")
        
        for i, user in enumerate(all_users, 1):
            print(f"   {i}. {user.name} - {user.phone} - {user.email}")
            print(f"      Location: {user.location_name}")
            print(f"      Registered: {user.created_at}")
    
    except Exception as e:
        print(f"❌ User Manager failed: {e}")
    
    # Test 3: Direct database query
    print("\n🗄️  Testing Direct Database Query...")
    try:
        db = SessionLocal()
        users = db.query(User).all()
        print(f"✅ Found {len(users)} users via direct query")
        
        for i, user in enumerate(users, 1):
            print(f"   {i}. {user.name}")
            print(f"      Phone: '{user.phone}' (length: {len(user.phone) if user.phone else 'None'})")
            print(f"      Email: '{user.email}'")
            print(f"      Location: '{user.location_name}'")
            print(f"      Created: {user.created_at}")
            print(f"      User ID: {user.id}")
            print()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Direct query failed: {e}")
    
    # Test 4: Test SMS to registered numbers
    print("📱 Testing SMS to Registered Numbers...")
    try:
        all_users = user_manager.get_all_users()
        
        if all_users:
            for user in all_users:
                if user.phone:
                    print(f"\n🧪 Testing SMS to {user.name} ({user.phone})")
                    
                    # Test if number format is correct
                    formatted = sms_service._format_phone_number(user.phone)
                    print(f"   Original: '{user.phone}'")
                    print(f"   Formatted: '{formatted}'")
                    
                    # Check if in verified numbers
                    account_info = sms_service.get_account_info()
                    if account_info["status"] == "success":
                        verified = user.phone in account_info["verified_numbers"]
                        print(f"   Verified: {verified}")
                        
                        if not verified:
                            print(f"   Available verified numbers:")
                            for vn in account_info["verified_numbers"]:
                                print(f"     • '{vn}'")
                    
                    # Simulate SMS sending
                    print(f"   Would send SMS: {'✅ YES' if formatted else '❌ NO - Invalid format'}")
                else:
                    print(f"\n❌ {user.name} has no phone number registered")
        else:
            print("❌ No users found in database")
    
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
    
    # Test 5: Check database tables
    print("\n🗄️  Database Table Check...")
    try:
        db = SessionLocal()
        
        # Check User table
        user_count = db.query(User).count()
        print(f"✅ User table: {user_count} records")
        
        # Check Alert table 
        from database.models import Alert
        alert_count = db.query(Alert).count()
        print(f"✅ Alert table: {alert_count} records")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database table check failed: {e}")
    
    print("\n" + "=" * 50)
    print("📋 DEBUG SUMMARY:")
    
    if all_users:
        print(f"✅ Users in database: {len(all_users)}")
        phone_users = [u for u in all_users if u.phone]
        print(f"✅ Users with phone numbers: {len(phone_users)}")
        
        if phone_users:
            print("📱 Phone numbers that would receive alerts:")
            for user in phone_users:
                print(f"   • {user.name}: {user.phone}")
        else:
            print("❌ NO users have phone numbers - this is the problem!")
    else:
        print("❌ NO users found in database")

if __name__ == "__main__":
    debug_user_database()
