from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

data = supabase.table('block_pest_disease').select('block_code').limit(30).execute()

print("Sample block codes:")
for item in data.data[:30]:
    code = item['block_code']
    print(f"{code}")
