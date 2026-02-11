"""
VALIDATE OLE 2023 - Excel vs Supabase
Using proper estate hierarchy (blocks -> divisions -> estates)
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("VALIDATION OLE 2023 - Excel vs Supabase")
print("="*80)

# Check file
file_path = 'source/data_produksi_OLE_2023.xlsx'
if not os.path.exists(file_path):
    print(f"\n❌ File not found: {file_path}")
    exit(1)

# Load Excel
print("\n1. Loading Excel...")
df_excel = pd.read_excel(file_path)

if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

excel_blocks = len(df_excel)
excel_actual = df_excel['Realisasi'].sum()
excel_target = df_excel['Potensi'].sum()

print(f"  Blocks: {excel_blocks}")
print(f"  Actual: {excel_actual:,.2f} Ton")
print(f"  Target: {excel_target:,.2f} Ton")

# Load Supabase with proper joins
print("\n2. Loading Supabase (OLE 2023)...")

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

blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
divisions_data = supabase.table('divisions').select('*').execute()
df_divisions = pd.DataFrame(divisions_data.data)
estates_data = supabase.table('estates').select('*').execute()
df_estates = pd.DataFrame(estates_data.data)

# Build hierarchy
df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], 
                   left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], 
              left_on='division_id', right_on='id', suffixes=('', '_d'), how='left')
df = df.merge(df_estates[['id', 'estate_code']], 
              left_on='estate_id', right_on='id', suffixes=('', '_e'), how='left')

# Filter OLE 2023
df_ole_2023 = df[(df['year'] == 2023) & (df['estate_code'] == 'OLE')]

db_blocks = len(df_ole_2023)
db_actual = df_ole_2023['real_ton'].sum()
db_target = df_ole_2023['potensi_ton'].sum()

print(f"  Blocks: {db_blocks}")
print(f"  Actual: {db_actual:,.2f} Ton")
print(f"  Target: {db_target:,.2f} Ton")

# Comparison
print("\n" + "="*80)
print("COMPARISON:")
print("="*80)

diff_actual = excel_actual - db_actual

print(f"\nExcel vs Supabase:")
print(f"  Blocks: {excel_blocks} vs {db_blocks}")
print(f"  Actual: {excel_actual:,.2f} vs {db_actual:,.2f} (diff: {diff_actual:+,.2f})")

# Find missing
excel_block_set = set(df_excel['BLOCK'].unique())
db_block_set = set(df_ole_2023['block_code'].unique())
missing_in_db = excel_block_set - db_block_set

all_blocks = set(df_blocks['block_code'])
not_in_blocks_table = missing_in_db - all_blocks
in_blocks_but_no_data = missing_in_db & all_blocks

print("\n" + "="*80)
print("MISSING ANALYSIS:")
print("="*80)

if len(missing_in_db) > 0:
    print(f"\nTotal missing: {len(missing_in_db)}")
    print(f"  Typos (not in blocks table): {len(not_in_blocks_table)}")
    print(f"  Need data insert: {len(in_blocks_but_no_data)}")
    
    if not_in_blocks_table:
        print(f"\n  Typo blocks:")
        for b in sorted(not_in_blocks_table)[:10]:
            print(f"    - {b}")
    
    if in_blocks_but_no_data:
        print(f"\n  Blocks needing 2023 data:")
        df_missing = df_excel[df_excel['BLOCK'].isin(in_blocks_but_no_data)]
        total_missing = df_missing['Realisasi'].sum()
        
        for block in sorted(in_blocks_but_no_data)[:20]:
            block_data = df_missing[df_missing['BLOCK'] == block].iloc[0]
            print(f"    - {block}: {block_data['Realisasi']:.2f} Ton")
        
        if len(in_blocks_but_no_data) > 20:
            print(f"    ... and {len(in_blocks_but_no_data) - 20} more")
        
        print(f"\n  Total missing: {total_missing:,.2f} Ton")

# Verdict
print("\n" + "="*80)
print("VERDICT:")
print("="*80)

if abs(diff_actual) < 10:
    print("\n✅ MATCH! OLE 2023 complete!")
else:
    print(f"\n⚠️ DISCREPANCY: {abs(diff_actual):,.2f} Ton ({abs(diff_actual)/excel_actual*100:.2f}%)")
    if len(in_blocks_but_no_data) > 0:
        print(f"   Need to INSERT {len(in_blocks_but_no_data)} blocks")

print("\nDONE")
