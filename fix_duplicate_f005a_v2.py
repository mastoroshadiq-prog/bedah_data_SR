"""
Fix Duplicate F005A (Version 2)
1. Revert existing block ID 112 to AME (Div 2)
2. Create NEW block F005A for OLE (Div 6)
3. Relink correct production record
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("FIX DUPLICATE F005A (V2)")
print("="*60)

BLOCK_CODE = 'F005A'

# 1. Revert Block 112 to AME (Div 2)
print("1. Reverting Block 112 to AME...")
res = supabase.table('blocks').update({'division_id': 2}).eq('id', 112).execute()
if res.data:
    print("   ✓ Success: ID 112 is AME (Div 2)")
else:
    print("   ✗ Failed or already reverted.")

# 2. Creating NEW Block for OLE (Div 6)
print("\n2. Creating NEW Block F005A for OLE (Div 6)...")

# Check existing
chk = supabase.table('blocks').select('*').eq('block_code', BLOCK_CODE).execute()
ole_block = None

for b in chk.data:
    if b['division_id'] in [5, 6, 7, 8]:  # OLE Divisions
        print(f"   ⚠️ Found existing OLE block! (ID: {b['id']})")
        ole_block = b
        break

if not ole_block:
    try:
        new_b = {
            'block_code': BLOCK_CODE,
            'division_id': 6,  # OLE Div 002
            'planted_area_ha': 0, # Default
            'sph': 0              # Default
        }
        res_ins = supabase.table('blocks').insert(new_b).execute()
        if res_ins.data:
            ole_block = res_ins.data[0]
            print(f"   ✓ Success: Created NEW Block ID {ole_block['id']} for OLE.")
        else:
            print("   ✗ Failed to create new block.")
    except Exception as e:
        print(f"   ✗ Error creating block: {e}")

# 3. Relink Production Record?
if ole_block:
    new_id = ole_block['id']
    print(f"\n3. Checking Production Records for OLE 2023...")
    
    # Cari record produksi F005A tahun 2023
    prod_recs = supabase.table('production_annual').select('*').eq('block_code', BLOCK_CODE).eq('year', 2023).execute()
    
    found_ole_prod = False
    
    for p in prod_recs.data:
        # Check integrity
        # Excel OLE: Real=353.29, Target=677.29
        
        diff_real = abs((p['real_ton'] or 0) - 353.29)
        
        if diff_real < 0.1:
            print(f"   Found OLE Production Record (ID: {p['id']}) currently linked to Block {p['block_id']}")
            found_ole_prod = True
            
            if p['block_id'] != new_id:
                print(f"   --> Relinking to NEW Block ID {new_id}...")
                upd = supabase.table('production_annual').update({'block_id': new_id}).eq('id', p['id']).execute()
                if upd.data:
                    print("       ✓ Relinked!")
                else:
                    print("       ✗ Failed to relink.")
            else:
                print("   --> Already correct.")
        
    if not found_ole_prod:
        print("   ⚠️ No OLE production record found! Need to INSERT.")
        # Insert if completely missing
        # ... logic to insert ...
        # But we assume the record exists from previous steps (just wrong block_id)

print("\nDONE")
