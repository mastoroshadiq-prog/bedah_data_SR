import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("QUICK VALIDATION - AME 2023")
print("="*60)

# Excel
df_excel = pd.read_excel('source/data_produksi_AME_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

excel_blocks = len(df_excel)
excel_actual = df_excel['Realisasi'].sum()
excel_target = df_excel['Potensi'].sum()

print(f"\nEXCEL (Source of Truth):")
print(f"  Blocks: {excel_blocks}")
print(f"  Actual: {excel_actual:,.2f} Ton")
print(f"  Target: {excel_target:,.2f} Ton")

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

df = df_prod.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df_ame = df[(df['year'] == 2023) & (df['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F']))]

db_blocks = len(df_ame)
db_actual = df_ame['real_ton'].sum()
db_target = df_ame['potensi_ton'].sum()

print(f"\nSUPABASE (Current):")
print(f"  Blocks: {db_blocks}")
print(f"  Actual: {db_actual:,.2f} Ton")
print(f"  Target: {db_target:,.2f} Ton")

print(f"\nDISCREPANCY:")
print(f"  Blocks: {excel_blocks - db_blocks:+d}")
print(f"  Actual: {excel_actual - db_actual:+,.2f} Ton")
print(f"  Target: {excel_target - db_target:+,.2f} Ton")

if abs(excel_actual - db_actual) < 100:
    print(f"\n✅ MATCH! Data sudah sync")
else:
    print(f"\n⚠️  DISCREPANCY! Need to update Supabase")

print("\nDONE")
