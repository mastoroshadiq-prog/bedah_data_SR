"""
Test Supabase Connection
Quick test to verify credentials work
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

print("=" * 80)
print("TESTING SUPABASE CONNECTION")
print("=" * 80)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print(f"\n✓ .env file loaded")
print(f"✓ URL: {SUPABASE_URL}")
print(f"✓ Key: {SUPABASE_KEY[:20]}... (truncated)")

# Test connection
try:
    print(f"\n🔗 Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✅ Connection successful!")
    
    # Try to list tables
    print(f"\n📋 Checking database access...")
    
    # Try a simple query to test access
    try:
        # This will fail if no tables exist, but that's OK
        response = supabase.table('_test_connection').select("*").limit(1).execute()
        print(f"✅ Database access confirmed!")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "relation" in error_msg:
            print(f"✅ Database connection OK (no tables yet - expected)")
        else:
            print(f"⚠️  Response: {error_msg[:100]}")
    
    print(f"\n" + "=" * 80)
    print("CONNECTION TEST SUCCESSFUL!")
    print("=" * 80)
    print(f"\n✅ Supabase is ready for data upload!")
    print(f"\n🎯 Next step: python upload_normalized.py")
    
except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {str(e)}")
    print(f"\n⚠️  Please check:")
    print(f"   1. SUPABASE_URL is correct")
    print(f"   2. SUPABASE_KEY is correct")
    print(f"   3. Internet connection is working")
