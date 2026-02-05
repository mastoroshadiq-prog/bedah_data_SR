from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Get ALL records with no limit
response = sb.table('production_annual').select('*').limit(2000).execute()
df = pd.DataFrame(response.data)

print("=" * 80)
print("COMPLETE DATABASE CHECK")
print("=" * 80)
print(f"\nTotal records returned: {len(df)}")
print(f"\nYear distribution:")
print(df['year'].value_counts().sort_index())
print(f"\nUnique years: {sorted(df['year'].unique())}")
print("=" * 80)
