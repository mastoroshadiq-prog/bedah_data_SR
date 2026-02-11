from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Check if A001A, A002A, C006A already have 2024 data
result = supabase.table('production_annual').select('*').eq('year', 2024).in_('block_code', ['A001A', 'A002A', 'C006A']).execute()

print(f"Existing 2024 records for A001A/A002A/C006A: {len(result.data)}")
for r in result.data:
    print(f"  id {r['id']}: {r['block_code']} - {r['real_ton']} Ton")

if len(result.data) > 0:
    print("\n⚠️ Records already exist! Need to UPDATE, not INSERT")
else:
    print("\n✓ No existing records, safe to INSERT")
