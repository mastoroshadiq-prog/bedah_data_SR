"""
Debug Blocks Insert
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("DEBUG BLOCKS INSERT")
print("="*60)

try:
    new_b = {
        'block_code': 'F005A_TEST', # Temporary name
        'division_id': 6,
        'planted_area_ha': 0,
        'sph': 0,
        'created_at': 'now()', # try explicit
        # Maybe check other required fields?
    }
    
    print("Attempting insert...")
    res = supabase.table('blocks').insert(new_b).execute()
    
    if res.data:
        print("✓ SUCCESS INSERT!")
        print(res.data)
        # Delete test block
        print("Cleaning up...")
        supabase.table('blocks').delete().eq('id', res.data[0]['id']).execute()
    else:
        print("✗ Insert returned no data.")

except Exception as e:
    print(f"✗ ERROR: {e}")
    # Print full details if possible

print("\nDONE")
