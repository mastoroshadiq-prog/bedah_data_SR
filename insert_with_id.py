"""
INSERT with EXPLICIT ID values (workaround for no auto-increment)
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("INSERT MISSING BLOCKS - With Explicit IDs")
print("="*60)

# Get max id first
max_id_result = supabase.table('production_annual').select('id').order('id', desc=True).limit(1).execute()
max_id = max_id_result.data[0]['id'] if max_id_result.data else 0
next_id = max_id + 1

print(f"\nCurrent max id: {max_id}")
print(f"Starting from id: {next_id}")

# Data
blocks = [
    {'block_id': 1, 'block_code': 'A001A', 'real': 181.76, 'potensi': 175.17},
    {'block_id': 3, 'block_code': 'A002A', 'real': 464.79, 'potensi': 539.51},
    {'block_id': 2, 'block_code': 'C006A', 'real': 587.74, 'potensi': 658.04}
]

success = 0

for i, block in enumerate(blocks):
    record_id = next_id + i
    gap = block['real'] - block['potensi']
    gap_pct = (gap / block['potensi'] * 100) if block['potensi'] > 0 else 0
    
    data = {
        'id': record_id,
        'block_id': block['block_id'],
        'year': 2023,
        'real_ton': block['real'],
        'potensi_ton': block['potensi'],
        'gap_ton': gap,
        'gap_pct_ton': gap_pct
    }
    
    try:
        print(f"\n{block['block_code']}:")
        print(f"  id: {record_id}")
        print(f"  actual: {block['real']:.2f} Ton")
        
        result = supabase.table('production_annual').insert(data).execute()
        
        if result.data:
            print(f"  ✓ SUCCESS")
            success += 1
        else:
            print(f"  ✗ FAILED")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")

print(f"\n{'='*60}")
print(f"RESULT: {success}/3 inserted")
print(f"{'='*60}")
print("\nDONE")
