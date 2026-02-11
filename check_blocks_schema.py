"""
Check Blocks Table Schema
Does it have estate_id column?
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECK BLOCKS SCHEMA")
print("="*60)

res = supabase.table('blocks').select('*').limit(1).execute()
if res.data:
    keys = res.data[0].keys()
    print("Columns:", list(keys))
    
    if 'estate_id' in keys:
        print("✅ Has estate_id column")
    else:
        print("❌ NO estate_id column (use division_id only)")
else:
    print("Table empty?")

print("\nDONE")
