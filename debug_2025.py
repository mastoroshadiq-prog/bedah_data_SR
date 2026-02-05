from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("=" * 80)
print("STEP 1: VERIFY DATABASE CONTENT")
print("=" * 80)

# Check each year separately
for year in [2023, 2024, 2025]:
    response = sb.table('production_annual').select('id', count='exact').eq('year', year).execute()
    print(f"Year {year}: {response.count} records")

print("\n" + "=" * 80)
print("STEP 2: LOAD WITH LIMIT 5000")
print("=" * 80)

response = sb.table('production_annual').select('*').limit(5000).execute()
print(f"Records loaded: {len(response.data)}")

import pandas as pd
df = pd.DataFrame(response.data)
print(f"\nYear distribution:")
print(df['year'].value_counts().sort_index())
print(f"\nUnique years: {sorted(df['year'].unique())}")

print("\n" + "=" * 80)
print("CONCLUSION:")
if 2025 in df['year'].unique():
    print("✅ 2025 DATA EXISTS in database and CAN BE LOADED with limit(5000)")
else:
    print("❌ 2025 DATA MISSING - Need to investigate why")
print("=" * 80)
