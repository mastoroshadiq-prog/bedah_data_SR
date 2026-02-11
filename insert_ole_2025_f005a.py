"""
INSERT OLE 2025 - F005A_OLE
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT OLE 2025 - F005A_OLE")
print("="*60)

# 1. Excel Data
df = pd.read_excel('source/data_produksi_OLE_2025.xlsx')
if df.iloc[0].isna().any():
    df = df.iloc[1:].reset_index(drop=True)

row = df[df['BLOCK'] == 'F005A'].iloc[0]
actual = float(row['Realisasi'])
target = float(row['Potensi'])

print(f"Data to Insert (F005A):")
print(f"  Year: 2025")
print(f"  Actual: {actual:.2f}")
print(f"  Target: {target:.2f}")

# 2. Get Block ID
res = supabase.table('blocks').select('id').eq('block_code', 'F005A_OLE').execute()
if not res.data:
    print("❌ Block F005A_OLE not found!")
    exit(1)
block_id = res.data[0]['id']

# 3. Insert
mx = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
next_id = mx.data[0]['id'] + 1 if mx.data else 4000

gap = actual - target
gap_pct = (gap / target * 100) if target > 0 else 0

new_record = {
    'id': next_id, # Manual
    'block_id': block_id,
    'block_code': 'F005A_OLE',
    'year': 2025,
    'real_ton': actual,
    'potensi_ton': target,
    'gap_ton': gap,
    'gap_pct_ton': gap_pct
}

try:
    res = supabase.table('production_annual').insert(new_record).execute()
    if res.data:
        print("✅ Success! Inserted.")
    else:
        print("❌ Failed.")
except Exception as e:
    print(f"❌ Error: {e}")

print("DONE")
