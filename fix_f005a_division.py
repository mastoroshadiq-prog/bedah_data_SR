"""
Fix Block F005A Division
Move from AME (2) to OLE (6).
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("FIX F005A DIVISION -> OLE (6)")
print("="*60)

# 1. Update Block
res = supabase.table('blocks').update({'division_id': 6}).eq('block_code', 'F005A').execute()

if res.data:
    print("✓ SUCCESS: Moved F005A to Division 6 (OLE)")
    print(f"  New division_id: {res.data[0]['division_id']}")
else:
    print("✗ FAILED to update block F005A")

print("\nDONE")
