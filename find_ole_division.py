"""
Find OLE Divisions
"""

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("FIND OLE DIVISIONS")
print("="*60)

# 1. Start from Estate
e_res = supabase.table('estates').select('*').eq('estate_code', 'OLE').execute()
if not e_res.data:
    print("❌ Estate OLE not found!")
    exit(1)

ole_id = e_res.data[0]['id']
print(f"OLE Estate ID: {ole_id}")

# 2. Get Divisions
d_res = supabase.table('divisions').select('*').eq('estate_id', ole_id).execute()
if not d_res.data:
    print("❌ No divisions found for OLE!")
else:
    print(f"\nFound {len(d_res.data)} divisions for OLE:")
    for d in d_res.data:
        print(f"  id: {d['id']}, code: {d['division_code']}, name: {d['division_name']}")

print("\nDONE")
