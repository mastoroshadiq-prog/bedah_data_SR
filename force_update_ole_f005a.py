"""
Force Update F005A for OLE 2023
Ensure correct tonnage is set.
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("FORCE UPDATE F005A - OLE 2023")
print("="*60)

BLOCK_CODE = 'F005A'
YEAR = 2023
TARGET_REAL = 353.29
TARGET_POTENSI = 677.29

# 1. Check existing
records = supabase.table('production_annual').select('*').eq('year', YEAR).eq('block_code', BLOCK_CODE).execute()

if not records.data:
    print(f"❌ Record not found for {BLOCK_CODE} {YEAR}!")
    # Insert logic would go here, maybe getting block_id first
    # But let's assume it exists based on previous checks
else:
    for rec in records.data:
        print(f"Update record id {rec['id']}...")
        print(f"  Old Real: {rec['real_ton']}")
        
        gap = TARGET_REAL - TARGET_POTENSI
        gap_pct = (gap / TARGET_POTENSI * 100) if TARGET_POTENSI > 0 else 0

        update_data = {
            'real_ton': TARGET_REAL,
            'potensi_ton': TARGET_POTENSI,
            'gap_ton': gap,
            'gap_pct_ton': gap_pct
        }
        
        res = supabase.table('production_annual').update(update_data).eq('id', rec['id']).execute()
        
        if res.data:
            print("  ✓ UPDATED SUCCESSFULLY")
            print(f"  New Real: {res.data[0]['real_ton']}")
        else:
            print("  ✗ UPDATE FAILED")

print("\nDONE")
