"""
VALIDATE DBE 2025
Validate Dirgahayu (DBE) vs Supabase
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("VALIDATION DBE 2025")
print("="*60)

# 1. Load Excel
file_path = 'source/data_produksi_DBE_2025.xlsx'
df_excel = pd.read_excel(file_path)

if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

excel_blocks = len(df_excel)
excel_actual = df_excel['Realisasi'].sum()
excel_target = df_excel['Potensi'].sum()

print(f"Excel:")
print(f"  Blocks: {excel_blocks}")
print(f"  Actual: {excel_actual:,.2f} Ton")
print(f"  Target: {excel_target:,.2f} Ton")

# 2. Supabase
print("\nLoading Supabase...")
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

# Filter DBE 2025
df_dbe_2025 = df[(df['year'] == 2025) & (df['estate_code'] == 'DBE')]

db_blocks = len(df_dbe_2025)
db_actual = df_dbe_2025['real_ton'].sum()

print(f"\nSupabase:")
print(f"  Blocks: {db_blocks}")
print(f"  Actual: {db_actual:,.2f} Ton")

# 3. Compare
diff = excel_actual - db_actual
pct = (diff / excel_actual * 100) if excel_actual > 0 else 0

print(f"\nDifference: {diff:+,.2f} Ton ({pct:.2f}%)")

# 4. Missing blocks
excel_set = set(df_excel['BLOCK'].unique())
db_set = set(df_dbe_2025['block_code'].unique())

missing = excel_set - db_set
extra = db_set - excel_set

if missing:
    print(f"\nMissing Blocks ({len(missing)}):")
    total_missing_val = 0
    missing_list = sorted(list(missing))
    
    for m in missing_list:
        val = df_excel[df_excel['BLOCK'] == m]['Realisasi'].sum()
        total_missing_val += val
        print(f"  - {m}: {val:.2f} Ton")
    
    print(f"\n  Total Missing Value: {total_missing_val:,.2f} Ton")
else:
    print("\nNo Missing Blocks!")

if abs(diff) < 0.1:
    print("\n✅ MATCH! DBE 2025 complete!")
else:
    print("\n⚠️ Discrepancy Detected!")

print("\nDONE")
