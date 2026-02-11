"""
Simple retry for AME 2024 insert with better error handling
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
import time

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT AME 2024 - Retry")
print("="*60)

# Data
blocks_data = [
    {'block_id': 1, 'block_code': 'A001A', 'real': 141.91, 'potensi': 184.82},
    {'block_id': 3, 'block_code': 'A002A', 'real': 326.33, 'potensi': 545.96},
    {'block_id': 2, 'block_code': 'C006A', 'real': 581.71, 'potensi': 666.20}
]

# Get next id
max_id = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
next_id = max_id.data[0]['id'] + 1 if max_id.data else 1924

success = 0

for i, block in enumerate(blocks_data):
    record_id = next_id + i
    gap = block['real'] - block['potensi']
    gap_pct = (gap / block['potensi'] * 100) if block['potensi'] > 0 else 0
    
    data = {
        'id': record_id,
        'block_id': block['block_id'],
        'block_code': block['block_code'],
        'year': 2024,
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
            print("FAILED (no data)")
            
    except Exception as e:
        print(f"ERROR: {str(e)[:100]}")
    
    time.sleep(0.5)  # Small delay between inserts

print(f"\n{'='*60}")
print(f"Result: {success}/3")

if success == 3:
    print("\n✓ All inserted! Verifying...")
    verify = supabase.table('production_annual').select('block_code,real_ton').eq('year', 2024).in_('block_code', ['A001A','A002A','C006A']).execute()
    print(f"  Found {len(verify.data)}/3 records")
    if verify.data:
        total = sum([r['real_ton'] for r in verify.data])
        print(f"  Total: {total:.2f} Ton (expected: 1049.95)")

print("\nDONE")
