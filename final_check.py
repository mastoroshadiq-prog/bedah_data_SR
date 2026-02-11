"""
Final check - Did the 3 blocks get inserted?
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("FINAL CHECK - 3 Missing Blocks")
print("="*60)

# Load production
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

# Load blocks
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

# Merge
df = df_prod.merge(df_blocks[['id', 'block_code']], 
                   left_on='block_id', right_on='id', 
                   suffixes=('', '_b'), how='left')

# Check for the 3 blocks
check_blocks = ['A001A', 'A002A', 'C006A']
df_check = df[(df['year'] == 2023) & (df['block_code'].isin(check_blocks))]

print(f"\nChecking for blocks: {check_blocks}")
print("\nFound:")
print(df_check[['id', 'block_code', 'year', 'real_ton', 'potensi_ton']].to_string(index=False))

if len(df_check) == 3:
    print(f"\n✓ ALL 3 BLOCKS FOUND!")
    total_actual = df_check['real_ton'].sum()
    total_target = df_check['potensi_ton'].sum()
    print(f"\nTotal from 3 blocks:")
    print(f"  Actual: {total_actual:,.2f} Ton")
    print(f"  Target: {total_target:,.2f} Ton")
else:
    print(f"\n✗ Only {len(df_check)}/3 blocks found")

print("\nDONE")
