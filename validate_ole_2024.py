"""
VALIDATE OLE 2024 - Excel vs Supabase
Includes handling for F005A -> F005A_OLE mapping
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("VALIDATION OLE 2024")
print("="*60)

# 1. Load Excel
print("\n1. Loading Excel...")
file_path = 'source/data_produksi_OLE_2024.xlsx'
df_excel = pd.read_excel(file_path)

if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

# Handle special mapping for F005A in Excel -> Should match F005A_OLE in DB
# But strict validation first compares raw codes.
# We will check if F005A is missing later.

excel_blocks = len(df_excel)
excel_actual = df_excel['Realisasi'].sum()
excel_target = df_excel['Potensi'].sum()

print(f"  Blocks: {excel_blocks}")
print(f"  Actual: {excel_actual:,.2f} Ton")
print(f"  Target: {excel_target:,.2f} Ton")

# 2. Load Supabase
print("\n2. Loading Supabase (OLE 2024)...")

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

# Join
df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], 
                   left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], 
              left_on='division_id', right_on='id', suffixes=('', '_d'), how='left')
df = df.merge(df_estates[['id', 'estate_code']], 
              left_on='estate_id', right_on='id', suffixes=('', '_e'), how='left')

# Filter OLE 2024
df_ole_2024 = df[(df['year'] == 2024) & (df['estate_code'] == 'OLE')]

db_blocks = len(df_ole_2024)
db_actual = df_ole_2024['real_ton'].sum()
db_target = df_ole_2024['potensi_ton'].sum()

print(f"  Blocks: {db_blocks}")
print(f"  Actual: {db_actual:,.2f} Ton")
print(f"  Target: {db_target:,.2f} Ton")

# 3. Comparison
print("\n" + "="*80)
print("COMPARISON:")
print("="*60)

diff_actual = excel_actual - db_actual

print(f"\nExcel vs Supabase:")
print(f"  Actual: {excel_actual:,.2f} vs {db_actual:,.2f} (diff: {diff_actual:+,.2f})")

# Find Missing
excel_block_set = set(df_excel['BLOCK'].unique())
db_block_set = set(df_ole_2024['block_code'].unique())

# Special logic: map F005A_OLE to F005A for comparison
normalized_db_blocks = {b.replace('F005A_OLE', 'F005A') for b in db_block_set}

missing_in_db = excel_block_set - normalized_db_blocks
extra_in_db = normalized_db_blocks - excel_block_set

print("\n" + "="*80)
print("MISSING ANALYSIS:")
print("="*60)

if len(missing_in_db) > 0:
    print(f"\nTotal missing blocks in DB: {len(missing_in_db)}")
    
    missing_list = list(missing_in_db)
    df_missing = df_excel[df_excel['BLOCK'].isin(missing_list)]
    
    for _, row in df_missing.iterrows():
        print(f"  - {row['BLOCK']}: {row['Realisasi']:.2f} Ton")

    total_missing_val = df_missing['Realisasi'].sum()
    print(f"\n  Total Missing Value: {total_missing_val:,.2f} Ton")
else:
    print("\nNo missing blocks!")

print("\nDONE")
