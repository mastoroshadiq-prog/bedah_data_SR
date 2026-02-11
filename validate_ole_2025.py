"""
VALIDATE OLE 2025
Includes check for F005A -> F005A_OLE
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("VALIDATION OLE 2025")
print("="*60)

# 1. Excel
file_path = 'source/data_produksi_OLE_2025.xlsx'
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

# Filter OLE 2025
df_ole_2025 = df[(df['year'] == 2025) & (df['estate_code'] == 'OLE')]

db_blocks = len(df_ole_2025)
db_actual = df_ole_2025['real_ton'].sum()

print(f"\nSupabase:")
print(f"  Blocks: {db_blocks}")
print(f"  Actual: {db_actual:,.2f} Ton")

# 3. Compare
diff = excel_actual - db_actual
print(f"\nDifference: {diff:+,.2f} Ton")

# 4. Check Missing
excel_set = set(df_excel['BLOCK'].unique())
db_set = set(df_ole_2025['block_code'].unique())

# Normalize F005A_OLE -> F005A for check
normalized_db_set = {b.replace('F005A_OLE', 'F005A') for b in db_set}

missing = excel_set - normalized_db_set
extra = normalized_db_set - excel_set

if missing:
    print(f"\nMissing Blocks ({len(missing)}):")
    for m in missing:
        val = df_excel[df_excel['BLOCK'] == m]['Realisasi'].sum()
        print(f"  - {m}: {val:.2f} Ton")
else:
    print("\nNo Missing Blocks!")

print("\nDONE")
