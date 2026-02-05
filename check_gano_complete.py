from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print('=' * 80)
print('CHECKING ALL TABLES FOR GANODERMA DATA')
print('=' * 80)

# List all tables by querying a known table structure
tables_to_check = [
    'estates',
    'blocks', 
    'block_land_infrastructure',
    'block_pest_disease',
    'block_disease_pest',
    'production_annual',
    'block_health',
    'ganoderma'
]

found_tables = []

for table in tables_to_check:
    try:
        response = sb.table(table).select('*').limit(1).execute()
        if response.data is not None:
            df = pd.DataFrame(response.data)
            found_tables.append(table)
            
            # Check for ganoderma-related columns
            gano_cols = [c for c in df.columns if 'gano' in c.lower() or 
                        'disease' in c.lower() or 'pest' in c.lower() or 
                        'attack' in c.lower() or 'health' in c.lower()]
            
            if gano_cols:
                print(f'\n✅ TABLE: {table}')
                print(f'   Ganoderma-related columns: {gano_cols}')
                
                # Get sample data
                r = sb.table(table).select('*').limit(5).execute()
                df_sample = pd.DataFrame(r.data)
                if gano_cols:
                    print(f'   Sample data:')
                    for col in gano_cols[:3]:  # Show first 3 columns
                        print(f'   - {col}: {df_sample[col].tolist()[:5]}')
    except Exception as e:
        pass

print(f'\n\n' + '=' * 80)
print(f'FOUND TABLES: {found_tables}')
print('=' * 80)

# Check if there's a specific pest/disease table
print('\n\nChecking for pest/disease related tables...')
for table in found_tables:
    try:
        r = sb.table(table).select('*').limit(1).execute()
        df = pd.DataFrame(r.data)
        print(f'\n{table} columns:')
        print(df.columns.tolist())
    except:
        pass
