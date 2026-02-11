"""
INSERT AME 2024 MISSING BLOCKS
Same 3 blocks as 2023: A001A, A002A, C006A
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT AME 2024 MISSING BLOCKS")
print("="*60)

# Excel data
df_excel = pd.read_excel('source/data_produksi_AME_2024.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)
df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

# Get max id
max_id_result = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
max_id = max_id_result.data[0]['id'] if max_id_result.data else 0
next_id = max_id + 1

print(f"Starting from id: {next_id}")

# Blocks to insert
blocks_to_insert = ['A001A', 'A002A', 'C006A']

# Get block_ids
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

success = 0

for i, block_code in enumerate(blocks_to_insert):
    # Get data from Excel
    excel_row = df_excel[df_excel['BLOCK'] == block_code]
    if len(excel_row) == 0:
        print(f"\n{block_code}: NOT in Excel!")
        continue
    
    excel_row = excel_row.iloc[0]
    real = excel_row['Realisasi']
    potensi = excel_row['Potensi']
    
    # Get block_id
    block_row = df_blocks[df_blocks['block_code'] == block_code]
    if len(block_row) == 0:
        print(f"\n{block_code}: NOT in blocks table!")
        continue
    
    block_id = block_row.iloc[0]['id']
    
    # Calculate gaps
    gap = real - potensi
    gap_pct = (gap / potensi * 100) if potensi > 0 else 0
    
    # Insert
    record_id = next_id + i
    data = {
        'id': int(record_id),
        'block_id': int(block_id),
        'block_code': block_code,
        'year': 2024,
        'real_ton': float(real),
        'potensi_ton': float(potensi),
        'gap_ton': float(gap),
        'gap_pct_ton': float(gap_pct)
    }
    
    try:
        print(f"\n{block_code}:")
        print(f"  id: {record_id}")
        print(f"  actual: {real:.2f} Ton")
        print(f"  target: {potensi:.2f} Ton")
        
        result = supabase.table('production_annual').insert(data).execute()
        
        if result.data:
            print(f"  ✓ SUCCESS")
            success += 1
        else:
            print(f"  ✗ FAILED")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print(f"RESULT: {success}/3 inserted")

if success == 3:
    print("\n✅ All blocks inserted!")
    print("\nVerifying...")
    
    # Quick verify
    verify = supabase.table('production_annual').select('*').eq('year', 2024).in_('block_code', blocks_to_insert).execute()
    
    if len(verify.data) == 3:
        print("✓ Verification passed - 3 records found for 2024")
        
        total_actual = sum([r['real_ton'] for r in verify.data])
        print(f"  Total: {total_actual:,.2f} Ton")
    else:
        print(f"⚠️ Verification: Found {len(verify.data)}/3 records")

print("\nDONE")
