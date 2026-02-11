"""
Revert F005A back to AME (Division 2)
And create new F005A for OLE.
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("FIX DUPLICATE BLOCK F005A")
print("="*60)

BLOCK_CODE = 'F005A'

# 1. Revert existing block (ID 112) to AME (Division 2)
print("1. Reverting Block ID 112 to AME...")
res = supabase.table('blocks').update({'division_id': 2}).eq('id', 112).execute()
if res.data:
    print("   ✓ Success: ID 112 is back to AME.")
else:
    print("   ✗ Failed to revert ID 112.")

# 2. Create NEW Block F005A for OLE (Division 6)
print("\n2. Creating NEW Block F005A for OLE (Division 6)...")

# Check if maybe already created duplicates?
chk = supabase.table('blocks').select('*').eq('block_code', BLOCK_CODE).execute()
ole_block = None

for b in chk.data:
    if b['division_id'] in [5, 6, 7, 8]: # OLE divisions
        print(f"   ⚠️ Block F005A for OLE already exists! (ID: {b['id']})")
        ole_block = b
        break

if not ole_block:
    # Insert new block
    # Need to check constraints (block_code unique?) -> usually block_code is NOT unique constraint globally but per division?
    # Let's try insert
    try:
        new_b = {
            'block_code': BLOCK_CODE,
            'division_id': 6,  # OLE Div 2
            'estate_id': 2     # OLE Estate ID
            # add other fields if necessary (area_ha, etc. default 0)
        }
        res_ins = supabase.table('blocks').insert(new_b).execute()
        if res_ins.data:
            ole_block = res_ins.data[0]
            print(f"   ✓ Success: Created NEW Block ID {ole_block['id']} for OLE.")
        else:
            print("   ✗ Failed to create new block.")
    except Exception as e:
        print(f"   ✗ Error creating block: {e}")

# 3. Relink Production Data OLE 2023 to NEW Block ID
if ole_block:
    new_id = ole_block['id']
    print(f"\n3. Updating Production Data OLE 2023 to use Block ID {new_id}...")
    
    # Cari record produksi F005A tahun 2023 (yang tadi kita insert pake ID 112 saat ID 112 masih OLE)
    # Sekarang ID 112 sudah jadi AME. Jadi record produksi itu SALAH estate.
    # Kita harus update record tsb supaya pakai block_id = new_id.
    
    # Find the record: block_code='F005A', year=2023
    # Note: might be tricky if there is also AME data for 2023?
    # But boss said F005A exists in OLE excel.
    # Let's check production records for F005A 2023
    
    prod_recs = supabase.table('production_annual').select('*').eq('block_code', BLOCK_CODE).eq('year', 2023).execute()
    
    for p in prod_recs.data:
        # Check values to identify if it is OLE data or AME data?
        # OLE Excel: Real=353.29, Target=677.29
        
        if abs(p['real_ton'] - 353.29) < 0.1:
            print(f"   Found OLE Production Record (ID: {p['id']}) attached to Block {p['block_id']}")
            
            if p['block_id'] != new_id:
                # Update to new block ID
                upd = supabase.table('production_annual').update({'block_id': new_id}).eq('id', p['id']).execute()
                if upd.data:
                    print("   ✓ Relinked to NEW OLE Block ID.")
                else:
                    print("   ✗ Failed to relink.")
            else:
                print("   (Already linked correctly)")
        else:
            print(f"   Found OTHER Production Record (ID: {p['id']}) - Real: {p['real_ton']} (AME?) -> Keeping as is.")

print("\nDONE")
