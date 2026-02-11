"""
INSERT OLE 2024 - F005A_OLE block data
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT OLE 2024 - F005A_OLE")
print("="*60)

# 1. Load Excel Data for F005A
file_path = 'source/data_produksi_OLE_2024.xlsx'
df_excel = pd.read_excel(file_path)
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')

f005a_row = df_excel[df_excel['BLOCK'] == 'F005A'].iloc[0]

actual = float(f005a_row['Realisasi'])
target = float(f005a_row['Potensi'])

print(f"Data Source (F005A):")
print(f"  Actual: {actual:.2f} Ton")
print(f"  Target: {target:.2f} Ton")

# 2. Get Block ID for F005A_OLE
res = supabase.table('blocks').select('id').eq('block_code', 'F005A_OLE').execute()
if not res.data:
    print("❌ Block F005A_OLE not found! Did we create it?")
    exit(1)

block_id = int(res.data[0]['id'])
print(f"  Block ID: {block_id}")

# 3. Check if record exists
chk = supabase.table('production_annual').select('*').eq('block_id', block_id).eq('year', 2024).execute()
if chk.data:
    print("⚠️ Record already exists! Checking values...")
    curr_actual = chk.data[0]['real_ton']
    if abs(curr_actual - actual) > 0.1:
         print(f"   Mismatch! DB: {curr_actual}, Excel: {actual}. Proceed to UPDATE.")
         # Logic to update could go here
    else:
         print("   Values match. Nothing to do.")
         exit(0)

# 4. Insert Data
print("Inserting data...")

# Get Max ID
mx = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
next_id = mx.data[0]['id'] + 1 if mx.data else 3000

gap = actual - target
gap_pct = (gap / target * 100) if target > 0 else 0

new_record = {
    'id': next_id, # Manual ID
    'block_id': block_id,
    'block_code': 'F005A_OLE',
    'year': 2024,
    'real_ton': actual,
    'potensi_ton': target,
    'gap_ton': gap,
    'gap_pct_ton': gap_pct
}

try:
    res = supabase.table('production_annual').insert(new_record).execute()
    if res.data:
        print("✅ Success! Data inserted.")
    else:
        print("❌ Insert failed.")
except Exception as e:
    print(f"❌ Error: {e}")

print("DONE")
