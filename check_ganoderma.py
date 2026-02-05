from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print('=== CHECKING GANODERMA DATA ===')

# Check disease/pest table
try:
    r = sb.table('block_disease_pest').select('*').limit(5).execute()
    if r.data:
        df = pd.DataFrame(r.data)
        print('\nblock_disease_pest columns:')
        print(df.columns.tolist())
        print('\nSample data:')
        print(df.head())
        
        # Check if ganoderma column exists
        gano_cols = [c for c in df.columns if 'gano' in c.lower()]
        print(f'\nGanoderma columns: {gano_cols}')
except Exception as e:
    print(f'Error: {e}')

# Check infrastructure table
try:
    r = sb.table('block_land_infrastructure').select('*').limit(3).execute()
    if r.data:
        df = pd.DataFrame(r.data)
        relevant_cols = [c for c in df.columns if 'gano' in c.lower() or 'disease' in c.lower() or 'pest' in c.lower()]
        if relevant_cols:
            print(f'\nblock_land_infrastructure has: {relevant_cols}')
except Exception as e:
    print(f'Infra error: {e}')
