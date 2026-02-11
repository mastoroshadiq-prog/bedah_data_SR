from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CREATE OLE BLOCK F005A (MANUAL ID)")
print("="*60)

# 1. Get Max ID
mx = supabase.table('blocks').select('id').order('id', desc=True).limit(1).execute()
next_id = mx.data[0]['id'] + 1 if mx.data else 1000
print(f"Next Block ID: {next_id}")

# 2. Create Block
new_block = {
    'id': next_id,
    'block_code': 'F005A',
    'division_id': 6, # OLE Div 2
    # 'category': 'LIGHT', # Optional?
    # 'has_production_data': True # Optional?
}

print("Creating block...")
try:
    res = supabase.table('blocks').insert(new_block).execute()
    if res.data:
        print(f"✓ Created Block {res.data[0]['id']} (OLE)")
        new_block_id = res.data[0]['id']
        
        # 3. Link Production 2023
        print("Linking OLE 2023 production...")
        # Find the record with year 2023, block_code F005A
        # It currently likely points to block 112 (AME)
        
        prod = supabase.table('production_annual').select('*').eq('year', 2023).eq('block_code', 'F005A').execute()
        
        for p in prod.data:
            # We assume the one with 353.29 is OLE
            if abs(p['real_ton'] - 353.29) < 0.1:
                print(f"  Found OLE record (ID {p['id']})")
                
                upd = supabase.table('production_annual').update({'block_id': new_block_id}).eq('id', p['id']).execute()
                if upd.data:
                    print("  ✓ Linked to new OLE block!")
                else:
                    print("  ✗ Failed to link.")
            else:
                 print(f"  Skipping record {p['id']} (Real: {p['real_ton']}) - likely AME")
                 
    else:
        print("✗ Failed to create block (no data returned)")

except Exception as e:
    print(f"✗ Error: {e}")

print("DONE")
