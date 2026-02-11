"""
Check Blocks Columns
"""

from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECK BLOCKS COLUMNS")
print("="*60)

res = supabase.table('blocks').select('*').limit(1).execute()
if res.data:
    print("Columns:", list(res.data[0].keys()))
else:
    print("Table seems empty? Or select '*' failed.")

print("\nDONE")
