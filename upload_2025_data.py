"""
UPLOAD 2025 PRODUCTION DATA - Emergency Fix
Missing 638 records for year 2025
"""

from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import os
import math

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print("=" * 80)
print("UPLOADING MISSING 2025 DATA")
print("=" * 80)

# Load CSV
df = pd.read_csv('output/normalized_tables/phase3_production/production_annual.csv')

# Filter 2025 only
df_2025 = df[df['year'] == 2025].copy()

print(f"\n2025 records in CSV: {len(df_2025)}")

# Check what's already in database
response = supabase.table('production_annual').select('*').eq('year', 2025).execute()
existing_2025 = len(response.data)

print(f"2025 records in database: {existing_2025}")

if existing_2025 > 0:
    print(f"\n⚠️  {existing_2025} records already exist. Skipping to avoid duplicates.")
    print("If you want to re-upload, delete 2025 data first.")
else:
    print(f"\nUploading {len(df_2025)} records...")
    
    # Clean NaN values
    df_2025 = df_2025.fillna(value=None)
    
    # Convert to dict
    records = df_2025.to_dict('records')
    
    # Additional cleanup for NaN
    for record in records:
        for key, value in record.items():
            if isinstance(value, float) and math.isnan(value):
                record[key] = None
    
    # Upload in batches
    batch_size = 500
    uploaded = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            supabase.table('production_annual').insert(batch).execute()
            uploaded += len(batch)
            print(f"  Uploaded {uploaded}/{len(records)}")
        except Exception as e:
            print(f"  ❌ Error at batch {i//batch_size + 1}: {e}")
            break
    
    if uploaded == len(records):
        print(f"\n✅ SUCCESS! Uploaded all {uploaded} records for 2025")
    else:
        print(f"\n⚠️  Partial upload: {uploaded}/{len(records)}")

# Verify
response = supabase.table('production_annual').select('year', count='exact').execute()
df_verify = pd.DataFrame(response.data)
print("\n" + "=" * 80)
print("FINAL DATABASE STATUS:")
print("=" * 80)
print(df_verify['year'].value_counts().sort_index())
print(f"\nTotal: {response.count} records")
print("=" * 80)
