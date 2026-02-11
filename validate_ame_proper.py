"""
PROPER AME 2023 VALIDATION
Using correct estate relationship via divisions table
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("AME 2023 VALIDATION - USING PROPER ESTATE RELATIONSHIP")
print("="*80)

# Load Excel
print("\n1. Loading Excel...")
df_excel = pd.read_excel('source/data_produksi_AME_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

excel_blocks = len(df_excel)
excel_actual = df_excel['Realisasi'].sum()
excel_target = df_excel['Potensi'].sum()

print(f"  Excel: {excel_blocks} blocks")
print(f"  Actual: {excel_actual:,.2f} Ton")
print(f"  Target: {excel_target:,.2f} Ton")

# Load Supabase with proper joins
print("\n2. Loading Supabase (with estate joins)...")

# Production data
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

# Divisions (has estate info)
divisions_data = supabase.table('divisions').select('*').execute()
df_divisions = pd.DataFrame(divisions_data.data)

# Estates
estates_data = supabase.table('estates').select('*').execute()
df_estates = pd.DataFrame(estates_data.data)

print(f"  Production records: {len(df_prod)}")
print(f"  Blocks: {len(df_blocks)}")
print(f"  Divisions: {len(df_divisions)}")
print(f"  Estates: {len(df_estates)}")

# Build full hierarchy
df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], 
                   left_on='block_id', right_on='id', 
                   suffixes=('', '_block'), how='left')

df = df.merge(df_divisions[['id', 'division_code', 'division_name', 'estate_id']], 
              left_on='division_id', right_on='id',
              suffixes=('', '_div'), how='left')

df = df.merge(df_estates[['id', 'estate_code', 'estate_name']], 
              left_on='estate_id', right_on='id',
              suffixes=('', '_estate'), how='left')

# Filter for AME 2023
df_ame_2023 = df[(df['year'] == 2023) & (df['estate_code'] == 'AME')].copy()

db_blocks = len(df_ame_2023)
db_actual = df_ame_2023['real_ton'].sum()
db_target = df_ame_2023['potensi_ton'].sum()

print(f"\n  AME 2023 in Supabase:")
print(f"    Blocks: {db_blocks}")
print(f"    Actual: {db_actual:,.2f} Ton")
print(f"    Target: {db_target:,.2f} Ton")

# Compare
print("\n" + "="*80)
print("COMPARISON:")
print("="*80)

print(f"\nEXCEL vs SUPABASE:")
print(f"  Blocks: {excel_blocks} vs {db_blocks} (diff: {excel_blocks - db_blocks:+d})")
print(f"  Actual: {excel_actual:,.2f} vs {db_actual:,.2f} (diff: {excel_actual - db_actual:+,.2f})")
print(f"  Target: {excel_target:,.2f} vs {db_target:,.2f} (diff: {excel_target - db_target:+,.2f})")

# Block-by-block
excel_block_set = set(df_excel['BLOCK'].unique())
db_block_set = set(df_ame_2023['block_code'].unique())

extra_in_db = db_block_set - excel_block_set
missing_in_db = excel_block_set - db_block_set

print(f"\n" + "="*80)
print("BLOCK DIFFERENCES:")
print("="*80)

if extra_in_db:
    print(f"\nEXTRA in Supabase ({len(extra_in_db)} blocks):")
    for block in sorted(extra_in_db)[:30]:
        print(f"  - {block}")
    if len(extra_in_db) > 30:
        print(f"  ... and {len(extra_in_db) - 30} more")

if missing_in_db:
    print(f"\nMISSING in Supabase ({len(missing_in_db)} blocks):")
    for block in sorted(missing_in_db)[:30]:
        print(f"  - {block}")
    if len(missing_in_db) > 30:
        print(f"  ... and {len(missing_in_db) - 30} more")

# Verdict
print("\n" + "="*80)
print("VERDICT:")
print("="*80)

if abs(excel_actual - db_actual) < 100:
    print("\nOK - Data match (< 100 Ton difference)")
else:
    print(f"\nDISCREPANCY FOUND")
    print(f"  Difference: {abs(excel_actual - db_actual):,.2f} Ton")
    print(f"  Percentage: {abs(excel_actual - db_actual)/excel_actual*100:.2f}%")
    
    if len(extra_in_db) > 0:
        print(f"\n  Supabase has {len(extra_in_db)} extra blocks")
    if len(missing_in_db) > 0:
        print(f"  Supabase missing {len(missing_in_db)} blocks")

print("\nDONE")
