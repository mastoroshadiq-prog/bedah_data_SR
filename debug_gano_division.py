# Quick debug script to check if block_code extraction will work
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Get sample ganoderma data
gano_data = supabase.table('block_pest_disease').select('*').limit(10).execute()
df_gano = pd.DataFrame(gano_data.data)

# Get blocks data
blocks_data = supabase.table('blocks').select('id, block_code').execute()
df_blocks = pd.DataFrame(blocks_data.data)

print("=== GANODERMA DATA ===")
print(f"Columns: {df_gano.columns.tolist()}")
print(f"Sample block_ids: {df_gano['block_id'].head().tolist()}")

print("\n=== BLOCKS DATA ===")
print(f"Columns: {df_blocks.columns.tolist()}")
print(f"Sample ids: {df_blocks['id'].head().tolist()}")
print(f"Sample block_codes: {df_blocks['block_code'].head().tolist()}")

# Try merge
merged = df_gano.merge(df_blocks, left_on='block_id', right_on='id', how='left')
print(f"\n=== MERGED DATA ===")
print(f"Columns: {merged.columns.tolist()}")
print(f"Block codes merged: {merged['block_code'].notna().sum()} / {len(merged)}")
print(f"Sample: {merged[['block_id', 'block_code']].head()}")

# Extract division
if 'block_code' in merged.columns:
    merged['division'] = merged['block_code'].str[1]
    print(f"\n=== DIVISION EXTRACTION ===")
    print(f"Divisions found: {merged['division'].value_counts()}")
