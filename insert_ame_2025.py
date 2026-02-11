"""
INSERT AME 2025 - Same 3 blocks
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
import time

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT AME 2025")
print("="*60)

# Load Excel to get exact values
df_excel = pd.read_excel('source/data_produksi_AME_2025.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

# Get data for 3 blocks
blocks_to_insert = []
for block_code in ['A001A', 'A002A', 'C006A']:
    row = df_excel[df_excel['BLOCK'] == block_code]
    if len(row) > 0:
        row = row.iloc[0]
        blocks_to_insert.append({
            'block_code': block_code,
            'block_id': 1 if block_code == 'A001A' else (3 if block_code == 'A002A' else 2),
            'real': float(row['Realisasi']),
            'potensi': float(row['Potensi'])
        })
        print(f"{block_code}: {row['Realisasi']:.2f} Ton")

# Get next id
max_id = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
next_id = max_id.data[0]['id'] + 1 if max_id.data else 1927

print(f"\nStarting from id: {next_id}")

success = 0

for i, block in enumerate(blocks_to_insert):
    record_id = next_id + i
    gap = block['real'] - block['potensi']
    gap_pct = (gap / block['potensi'] * 100) if block['potensi'] > 0 else 0
    
    data = {
        'id': record_id,
        'block_id': block['block_id'],
        'block_code': block['block_code'],
        'year': 2025,
        'real_ton': block['real'],
        'potensi_ton': block['potensi'],
        'gap_ton': gap,
        'gap_pct_ton': gap_pct
    }
    
    print(f"\n{block['block_code']}: ", end='')
    
    try:
        result = supabase.table('production_annual').insert(data).execute()
        
        if result.data:
            print(f"OK (id {record_id})")
            success += 1
        else:
            print("FAILED")
            
    except Exception as e:
        print(f"ERROR: {str(e)[:80]}")
    
    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"Result: {success}/3")

if success == 3:
    print("\n✓ All inserted! Verifying...")
    verify = supabase.table('production_annual').select('block_code,real_ton').eq('year', 2025).in_('block_code', ['A001A','A002A','C006A']).execute()
    if verify.data:
        total = sum([r['real_ton'] for r in verify.data])
        print(f"  Found {len(verify.data)}/3 records")
        print(f"  Total: {total:.2f} Ton")

print("\nDONE")
