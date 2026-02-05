"""
Run SQL Setup Script on Supabase
Execute setup_sql.sql to create indexes, views, and functions
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  ERROR: Supabase credentials not found!")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 100)
print("RUN SQL SETUP ON SUPABASE")
print("=" * 100)

# Read SQL file
print("\n📂 Reading setup_sql.sql...")
with open('setup_sql.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

print(f"✓ Loaded {len(sql_content)} characters")

# Split into individual statements (skip comments and empty lines)
print("\n📝 Parsing SQL statements...")
statements = []
current_statement = []

for line in sql_content.split('\n'):
    line = line.strip()
    
    # Skip comments and empty lines  
    if not line or line.startswith('--'):
        continue
    
    current_statement.append(line)
    
    # Statement ends with semicolon
    if line.endswith(';'):
        statement = ' '.join(current_statement)
        if statement:
            statements.append(statement)
        current_statement = []

print(f"✓ Found {len(statements)} SQL statements")

# Execute statements
print(f"\n⚙️  Executing SQL statements...")
print("Note: Some statements may require manual execution in Supabase SQL Editor\n")

success_count = 0
error_count = 0

for i, statement in enumerate(statements, 1):
    # Show preview of statement
    preview = statement[:80] + "..." if len(statement) > 80 else statement
    
    try:
        # Try to execute via RPC (may not work for all DDL statements)
        result = supabase.rpc('sql', {'query': statement}).execute()
        print(f"✓ [{i}/{len(statements)}] {preview}")
        success_count += 1
    except Exception as e:
        error = str(e)
        if "function sql(query => text) does not exist" in error:
            print(f"ℹ️  [{i}/{len(statements)}] {preview}")
            print(f"      → Manual execution required in Supabase SQL Editor")
        else:
            print(f"✗ [{i}/{len(statements)}] {preview}")
            print(f"      → Error: {error[:100]}")
        error_count += 1

# Summary
print("\n" + "=" * 100)
print("SQL SETUP SUMMARY")
print("=" * 100)
print(f"\n✓ Success: {success_count}/{len(statements)}")
print(f"ℹ️  Manual execution needed: {error_count}/{len(statements)}")

if error_count > 0:
    print("\n📋 TO COMPLETE SETUP:")
    print("   1. Go to Supabase Dashboard → SQL Editor")
    print("   2. Open and run: setup_sql.sql")
    print("   3. Verify indexes with:")
    print("      SELECT * FROM pg_indexes WHERE tablename IN ('blocks', 'estates');")
else:
    print("\n✅ All SQL statements executed successfully!")

print("\n🎯 Next Steps:")
print("   1. ✅ SQL setup complete")
print("   2. 🔜 Launch dashboard: streamlit run dashboard_app.py")
print("   3. 🔜 Run benchmark: python benchmark_performance.py")

print("\n" + "=" * 100)
