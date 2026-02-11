"""
Check Sample Blocks for OLE Estate
Find where other blocks with prefix F are located.
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECK SAMPLE BLOCKS OLE (Prefix F)")
print("="*60)

# Get sample blocks
blocks = supabase.table('blocks').select('*').like('block_code', 'F%').limit(10).execute()

if not blocks.data:
    print("❌ No blocks with prefix F found!")
else:
    print(f"Found {len(blocks.data)} sample blocks:")
    for b in blocks.data:
        div_id = b['division_id']
        # check division details
        d_res = supabase.table('divisions').select('*').eq('id', div_id).execute()
        if d_res.data:
            d = d_res.data[0]
            print(f"  Block {b['block_code']} -> Division {div_id} ({d['division_name']})")
        else:
            print(f"  Block {b['block_code']} -> Division {div_id} (UNKNOWN)")

print("\nDONE")
