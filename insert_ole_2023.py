"""
INSERT OLE 2023 - F005A block
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT OLE 2023 - F005A")
print("="*60)

# Load Excel
df_excel = pd.read_excel('source/data_produksi_OLE_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

# Get F005A data
row = df_excel[df_excel['BLOCK'] == 'F005A']
if len(row) == 0:
    print("❌ F005A not found in Excel!")
    exit(1)

row = row.iloc[0]
real = float(row['Realisasi'])
potensi = float(row['Potensi'])

print(f"Excel data:")
print(f"  Actual: {real:.2f} Ton")
print(f"  Target: {potensi:.2f} Ton")

# Get block_id
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

block_row = df_blocks[df_blocks['block_code'] == 'F005A']
if len(block_row) == 0:
    print("\n❌ F005A not in blocks table!")
    exit(1)

block_id = int(block_row.iloc[0]['id'])
print(f"  block_id: {block_id}")

# Get next id
max_id = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
next_id = max_id.data[0]['id'] + 1 if max_id.data else 1930

gap = real - potensi
gap_pct = (gap / potensi * 100) if potensi > 0 else 0

data = {
    'id': next_id,
    'block_id': block_id,
    'block_code': 'F005A',
    'year': 2023,
    'real_ton': real,
    'potensi_ton': potensi,
    'gap_ton': gap,
    'gap_pct_ton': gap_pct
}

print(f"\nInserting (id {next_id})...", end=' ')

try:
    result = supabase.table('production_annual').insert(data).execute()
    
    if result.data:
        print("✓ SUCCESS")
        
        # Verify
        verify = supabase.table('production_annual').select('*').eq('year', 2023).eq('block_code', 'F005A').execute()
        if verify.data:
            print(f"\n✓ Verified: {verify.data[0]['real_ton']:.2f} Ton")
    else:
        print("✗ FAILED")
        
except Exception as e:
    print(f"✗ ERROR: {str(e)}")

print("\nDONE")
