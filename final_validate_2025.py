import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Excel
df_excel = pd.read_excel('source/data_produksi_AME_2025.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)
df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])
excel_actual = df_excel['Realisasi'].sum()

print("FINAL VALIDATION AME 2025")
print("="*60)

# Supabase
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

df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], left_on='division_id', right_on='id', suffixes=('', '_d'), how='left')
df = df.merge(df_estates[['id', 'estate_code']], left_on='estate_id', right_on='id', suffixes=('', '_e'), how='left')

df_ame = df[(df['year'] == 2025) & (df['estate_code'] == 'AME')]
db_actual = df_ame['real_ton'].sum()

print(f"\nExcel: {excel_actual:,.2f} Ton")
print(f"Supabase: {db_actual:,.2f} Ton")
print(f"Diff: {abs(excel_actual - db_actual):,.2f} Ton")

if abs(excel_actual - db_actual) < 10:
    print("\n✅ MATCH! AME 2025 complete!")
else:
    print(f"\n⚠️ Diff: {abs(excel_actual - db_actual):,.2f} Ton")

print("\nDONE")
