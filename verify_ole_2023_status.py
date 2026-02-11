"""
VERIFY OLE 2023 STATUS
Check if data exists in Supabase and matches expected totals.
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("VERIFYING OLE 2023 DATA IN SUPABASE")
print("="*60)

# Load Data
all_prod = []
page = 0
while True:
    start = page * 1000
    end = start + 999
    response = supabase.table('production_annual').select('*').range(start, end).execute()
    if not response.data:
        break
    all_prod.extend(response.data)
    if len(response.data) < 1000:
        break
    page += 1

df_prod = pd.DataFrame(all_prod)

# Load Hierarchy
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
divisions_data = supabase.table('divisions').select('*').execute()
df_divisions = pd.DataFrame(divisions_data.data)
estates_data = supabase.table('estates').select('*').execute()
df_estates = pd.DataFrame(estates_data.data)

# Join
df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], 
                   left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], 
              left_on='division_id', right_on='id', suffixes=('', '_d'), how='left')
df = df.merge(df_estates[['id', 'estate_code', 'estate_name']], 
              left_on='estate_id', right_on='id', suffixes=('', '_e'), how='left')

# Filter OLE 2023
df_ole_2023 = df[(df['year'] == 2023) & (df['estate_code'] == 'OLE')]

# Stats
count = len(df_ole_2023)
actual = df_ole_2023['real_ton'].sum()
target = df_ole_2023['potensi_ton'].sum()

print(f"Total Blocks Found: {count}")
print(f"Total Actual (Realisasi): {actual:,.2f} Ton")
print(f"Total Target (Potensi):   {target:,.2f} Ton")

print("\n" + "="*60)
print("STATUS CHECK:")
print("="*60)

EXPECTED_ACTUAL = 49877.76
EXPECTED_TARGET = 65249.87

diff = abs(actual - EXPECTED_ACTUAL)

if diff < 1.0:
    print("✅ CONFIRMED: Data OLE 2023 sudah masuk dan MATCH!")
else:
    print(f"⚠️ DISCREPANCY DETECTED!")
    print(f"   Expected: {EXPECTED_ACTUAL:,.2f}")
    print(f"   Diff:     {diff:,.2f}")

print("\nSample Data (First 5 blocks):")
print(df_ole_2023[['block_code', 'real_ton', 'potensi_ton']].head().to_string(index=False))

print("\nDONE")
