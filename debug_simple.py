from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("STEP 1: Check each year")
for year in [2023, 2024, 2025]:
    r = sb.table('production_annual').select('id', count='exact').eq('year', year).execute()
    print(f"Year {year}: {r.count} records")

print("\nSTEP 2: Load with limit(5000)")
r = sb.table('production_annual').select('*').limit(5000).execute()
df = pd.DataFrame(r.data)
print(f"Total loaded: {len(df)}")
print(f"Years: {sorted(df['year'].unique())}")
print(f"2025 exists: {2025 in df['year'].values}")
