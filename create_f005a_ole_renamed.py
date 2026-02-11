"""
Create F005A_OLE block (Renamed to avoid unique constraint)
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CREATE F005A_OLE BLOCK")
print("="*60)

# 1. Get Max ID
mx = supabase.table('blocks').select('id').order('id', desc=True).limit(1).execute()
next_id = mx.data[0]['id'] + 1 if mx.data else 1000
print(f"Next Block ID: {next_id}")

NEW_CODE = 'F005A_OLE'

# 2. Create Block
new_block = {
    'id': next_id,
    'block_code': NEW_CODE,
    'division_id': 6, # OLE Div 2
}

print(f"Creating block {NEW_CODE}...")
try:
    res = supabase.table('blocks').insert(new_block).execute()
    if res.data:
        print(f"✓ Created Block {res.data[0]['id']} ({NEW_CODE})")
        new_block_id = res.data[0]['id']
        
        # 3. Link Production 2023
        print("Linking OLE 2023 production...")
        # Search for the record with 353.29 Ton (OLE value)
        # It currently has block_code='F005A' (string) and block_id=112 (AME)
        
        prod = supabase.table('production_annual').select('*').eq('year', 2023).eq('block_code', 'F005A').execute()
        
        found = False
        for p in prod.data:
            if abs(p['real_ton'] - 353.29) < 0.1:
                print(f"  Found record (ID {p['id']})")
                
                # Update block_id AND block_code string in production table to match new block
                upd_data = {
                    'block_id': new_block_id,
                    'block_code': NEW_CODE 
                }
                
                upd = supabase.table('production_annual').update(upd_data).eq('id', p['id']).execute()
                if upd.data:
                    print("  ✓ Linked to F005A_OLE!")
                    found = True
                else:
                    print("  ✗ Failed to link.")
        
        if not found:
            print("  ⚠️ Could not find exact OLE production record to link.")

    else:
        print("✗ Failed to create block (no data returned)")

except Exception as e:
    print(f"✗ Error: {e}")

print("DONE")
