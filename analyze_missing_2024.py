import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Excel
df_excel = pd.read_excel('source/data_produksi_AME_2024.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)
df_excel = df_excel.dropna(subset=['BLOCK'])
df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')

excel_blocks = set(df_excel['BLOCK'])

# Blocks table
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
all_blocks = set(df_blocks['block_code'])

# Supabase AME 2024
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
divisions_data = supabase.table('divisions').select('*').execute()
df_divisions = pd.DataFrame(divisions_data.data)
estates_data = supabase.table('estates').select('*').execute()
df_estates = pd.DataFrame(estates_data.data)

df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], left_on='division_id', right_on='id', suffixes=('', '_d'), how='left')
df = df.merge(df_estates[['id', 'estate_code']], left_on='estate_id', right_on='id', suffixes=('', '_e'), how='left')

df_ame_2024 = df[(df['year'] == 2024) & (df['estate_code'] == 'AME')]
db_blocks_2024 = set(df_ame_2024['block_code'])

# Find missing
missing = excel_blocks - db_blocks_2024
not_in_blocks_table = missing - all_blocks
in_blocks_but_no_data = missing & all_blocks

print("AME 2024 MISSING ANALYSIS")
print("="*60)
print(f"\nTotal missing: {len(missing)}")
print(f"\n1. Not in blocks table (TYPOS): {len(not_in_blocks_table)}")
for b in sorted(not_in_blocks_table):
    print(f"   - {b}")

print(f"\n2. In blocks table but no 2024 data: {len(in_blocks_but_no_data)}")
for b in sorted(in_blocks_but_no_data):
    excel_data = df_excel[df_excel['BLOCK'] == b].iloc[0]
    print(f"   - {b}: {excel_data['Realisasi']:.2f} Ton")

if len(in_blocks_but_no_data) > 0:
    total_missing = df_excel[df_excel['BLOCK'].isin(in_blocks_but_no_data)]['Realisasi'].sum()
    print(f"\n   Total: {total_missing:,.2f} Ton")

print("\nDONE")
