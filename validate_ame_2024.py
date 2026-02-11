"""
VALIDATE AME 2024 - Excel vs Supabase
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("VALIDATION AME 2024 - Excel vs Supabase")
print("="*80)

# ============================================================================
# LOAD EXCEL
# ============================================================================
print("\n1. Loading Excel...")

df_excel = pd.read_excel('source/data_produksi_AME_2024.xlsx')

# Remove header row if present
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

# Convert to numeric
df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

excel_blocks = len(df_excel)
excel_actual = df_excel['Realisasi'].sum()
excel_target = df_excel['Potensi'].sum()

print(f"  Blocks: {excel_blocks}")
print(f"  Actual: {excel_actual:,.2f} Ton")
print(f"  Target: {excel_target:,.2f} Ton")

# ============================================================================
# LOAD SUPABASE
# ============================================================================
print("\n2. Loading Supabase (AME 2024)...")

# Production
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

# Blocks
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

# Divisions
divisions_data = supabase.table('divisions').select('*').execute()
df_divisions = pd.DataFrame(divisions_data.data)

# Estates
estates_data = supabase.table('estates').select('*').execute()
df_estates = pd.DataFrame(estates_data.data)

# Build hierarchy with proper joins
df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], 
                   left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], 
              left_on='division_id', right_on='id', suffixes=('', '_d'), how='left')
df = df.merge(df_estates[['id', 'estate_code']], 
              left_on='estate_id', right_on='id', suffixes=('', '_e'), how='left')

# Filter AME 2024
df_ame_2024 = df[(df['year'] == 2024) & (df['estate_code'] == 'AME')]

db_blocks = len(df_ame_2024)
db_actual = df_ame_2024['real_ton'].sum()
db_target = df_ame_2024['potensi_ton'].sum()

print(f"  Blocks: {db_blocks}")
print(f"  Actual: {db_actual:,.2f} Ton")
print(f"  Target: {db_target:,.2f} Ton")

# ============================================================================
# COMPARISON
# ============================================================================
print("\n" + "="*80)
print("COMPARISON:")
print("="*80)

diff_blocks = excel_blocks - db_blocks
diff_actual = excel_actual - db_actual
diff_target = excel_target - db_target

print(f"\nExcel vs Supabase:")
print(f"  Blocks: {excel_blocks} vs {db_blocks} (diff: {diff_blocks:+d})")
print(f"  Actual: {excel_actual:,.2f} vs {db_actual:,.2f} (diff: {diff_actual:+,.2f})")
print(f"  Target: {excel_target:,.2f} vs {db_target:,.2f} (diff: {diff_target:+,.2f})")

# ============================================================================
# BLOCK-BY-BLOCK
# ============================================================================
excel_block_set = set(df_excel['BLOCK'].unique())
db_block_set = set(df_ame_2024['block_code'].unique())

extra_in_db = db_block_set - excel_block_set
missing_in_db = excel_block_set - db_block_set

print("\n" + "="*80)
print("BLOCK DIFFERENCES:")
print("="*80)

if missing_in_db:
    print(f"\nMISSING in Supabase ({len(missing_in_db)} blocks):")
    # Get data from Excel
    df_missing = df_excel[df_excel['BLOCK'].isin(missing_in_db)].copy()
   
    total_missing_actual = df_missing['Realisasi'].sum()
    total_missing_target = df_missing['Potensi'].sum()
    
    for block in sorted(missing_in_db)[:20]:
        block_data = df_missing[df_missing['BLOCK'] == block].iloc[0]
        print(f"  - {block}: {block_data['Realisasi']:.2f} Ton")
    
    if len(missing_in_db) > 20:
        print(f"  ... and {len(missing_in_db) - 20} more")
    
    print(f"\n  Total missing:")
    print(f"    Actual: {total_missing_actual:,.2f} Ton")
    print(f"    Target: {total_missing_target:,.2f} Ton")

if extra_in_db:
    print(f"\nEXTRA in Supabase ({len(extra_in_db)} blocks):")
    for block in sorted(extra_in_db)[:20]:
        print(f"  - {block}")
    if len(extra_in_db) > 20:
        print(f"  ... and {len(extra_in_db) - 20} more")

# ============================================================================
# VERDICT
# ============================================================================
print("\n" + "="*80)
print("VERDICT:")
print("="*80)

if abs(diff_actual) < 10:
    print("\n✅ MATCH! Data sudah sync")
else:
    print(f"\n⚠️ DISCREPANCY FOUND")
    print(f"  Difference: {abs(diff_actual):,.2f} Ton ({abs(diff_actual)/excel_actual*100:.2f}%)")
    
    if len(missing_in_db) > 0:
        print(f"\n  Need to INSERT {len(missing_in_db)} missing blocks")

print("\nDONE")
