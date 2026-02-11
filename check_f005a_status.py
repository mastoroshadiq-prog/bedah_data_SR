from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECK F005A STATE")
print("="*60)

res = supabase.table('blocks').select('*').eq('block_code', 'F005A').execute()

if res.data:
    for b in res.data:
        div_id = b['division_id']
        # check division details
        d_res = supabase.table('divisions').select('*').eq('id', div_id).execute()
        est_name = "Unknown"
        if d_res.data:
            d = d_res.data[0]
            est_id = d['estate_id']
            e_res = supabase.table('estates').select('*').eq('id', est_id).execute()
            if e_res.data:
                est_name = e_res.data[0]['estate_name']
        
        print(f"Block ID: {b['id']}")
        print(f"  Division ID: {div_id}")
        print(f"  Estate: {est_name}")
else:
    print("No F005A found!")

print("DONE")
