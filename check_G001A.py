from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("Checking block_id 236 (G001A)...")
gano = supabase.table('block_pest_disease').select('*').eq('block_id', 236).execute()

print(f'\nTotal records for block_id 236: {len(gano.data)}')

for i, rec in enumerate(gano.data):
    print(f'\nRecord {i+1}:')
    print(f'  id: {rec["id"]}')
    print(f'  block_id: {rec["block_id"]}')
    print(f'  pct_serangan: {rec["pct_serangan"]}')
    print(f'  Display: {rec["pct_serangan"]*100:.4f}%')
    print(f'  Expected: 0.3396%')
    
if len(gano.data) == 0:
    print('\n❌ NO DATA FOUND!')
