"""
Check Block F005A Relation
Is it correctly linked to OLE Estate?
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECK F005A RELATION")
print("="*60)

# Check Blocks Table
b_res = supabase.table('blocks').select('*').eq('block_code', 'F005A').execute()
if not b_res.data:
    print("❌ Block F005A NOT FOUND in blocks table!")
else:
    b_data = b_res.data[0]
    print("Block F005A Found:")
    print(f"  id: {b_data['id']}")
    print(f"  division_id: {b_data['division_id']}")
    
    div_id = b_data['division_id']
    if div_id:
        # Check Division
        d_res = supabase.table('divisions').select('*').eq('id', div_id).execute()
        if d_res.data:
            d_data = d_res.data[0]
            print("Division Found:")
            print(f"  id: {d_data['id']}")
            print(f"  division_name: {d_data['division_name']}")
            print(f"  estate_id: {d_data['estate_id']}")
            
            est_id = d_data['estate_id']
            if est_id:
                # Check Estate
                e_res = supabase.table('estates').select('*').eq('id', est_id).execute()
                if e_res.data:
                    e_data = e_res.data[0]
                    print("Estate Found:")
                    print(f"  id: {e_data['id']}")
                    print(f"  estate_code: {e_data['estate_code']}")
                    print(f"  estate_name: {e_data['estate_name']}")
                    
                    if e_data['estate_code'] == 'OLE':
                        print("\n✅ Estate is CORRECT (OLE)")
                    else:
                        print(f"\n❌ FALSE ESTATE! Is {e_data['estate_code']}, Should be OLE")

print("\nDONE")
