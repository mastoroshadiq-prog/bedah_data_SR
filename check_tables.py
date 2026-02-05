"""
Check and Create Tables if Needed
Ensure all required tables exist before upload
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CHECKING TABLES IN SUPABASE")
print("=" * 80)

# Tables we need
REQUIRED_TABLES = ['estates', 'blocks', 'production_data', 'realisasi_potensi']

print(f"\n🔍 Checking for required tables...")

tables_exist = {}
for table in REQUIRED_TABLES:
    try:
        response = supabase.table(table).select("*").limit(1).execute()
        tables_exist[table] = True
        print(f"  ✅ {table}: EXISTS")
    except Exception as e:
        tables_exist[table] = False
        if "does not exist" in str(e) or "not found" in str(e).lower():
            print(f"  ❌ {table}: NOT FOUND")
        else:
            print(f"  ⚠️  {table}: {str(e)[:60]}...")

all_exist = all(tables_exist.values())

print(f"\n" + "=" * 80)

if all_exist:
    print("✅ ALL TABLES EXIST!")
    print("=" * 80)
    print(f"\n🎯 Ready to upload data!")
    print(f"\nRun: python upload_normalized.py")
else:
    print("⚠️  TABLES NEED TO BE CREATED")
    print("=" * 80)
    
    missing = [t for t, exists in tables_exist.items() if not exists]
    print(f"\n📋 Missing tables: {', '.join(missing)}")
    
    print(f"\n🔧 SOLUTION: Create tables in Supabase")
    print(f"\n📝 Option 1: Use Supabase Dashboard")
    print(f"   1. Go to: {SUPABASE_URL.replace('https://', 'https://app.')}/project/_/editor")
    print(f"   2. Click 'New Table'")
    print(f"   3. Create each missing table")
    
    print(f"\n📝 Option 2: Run SQL in Supabase SQL Editor")
    print(f"   1. Go to: {SUPABASE_URL.replace('https://', 'https://app.')}/project/_/sql")
    print(f"   2. Run the SQL from: setup_sql.sql")
    
    print(f"\n📝 Option 3: Let upload script create tables")
    print(f"   - Try running: python upload_normalized.py")
    print(f"   - Script will attempt to create tables automatically")

print(f"\n" + "=" * 80)
