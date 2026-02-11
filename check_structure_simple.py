import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECKING DATABASE STRUCTURE")
print("="*60)

# Blocks
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
print(f"\nBlocks table: {len(df_blocks)}")
print(f"Columns: {df_blocks.columns.tolist()}")

# Divisions
try:
    divisions_data = supabase.table('divisions').select('*').execute()
    df_divisions = pd.DataFrame(divisions_data.data)
    print(f"\nDivisions table: {len(df_divisions)}")
    print(f"Columns: {df_divisions.columns.tolist()}")
    print("\nSample:")
    print(df_divisions.head())
except Exception as e:
    print(f"\nDivisions error: {e}")
    df_divisions = None

# Estates
try:
    estates_data = supabase.table('estates').select('*').execute()
    df_estates = pd.DataFrame(estates_data.data)
    print(f"\nEstates table: {len(df_estates)}")
    print(f"Columns: {df_estates.columns.tolist()}")
    print("\nAll estates:")
    print(df_estates)
except Exception as e:
    print(f"\nEstates error: {e}")
    df_estates = None

print("\n" + "="*60)
print("Sample blocks with division:")
print(df_blocks[['id', 'block_code', 'division', 'division_id']].head(10))

# Try to get estate from division name
if df_divisions is not None:
    print("\n" + "="*60)
    print("Joining blocks with divisions...")
    
    df_joined = df_blocks.merge(df_divisions, left_on='division_id', right_on='id', suffixes=('', '_div'), how='left')
    
    # Show available columns after join
    print(f"Columns after join: {df_joined.columns.tolist()}")
    
    # Sample with division info
    print("\nSample with division info:")
    cols = ['block_code', 'division']
    if 'name' in df_joined.columns:
        cols.append('name')
    if 'estate_code' in df_joined.columns:
        cols.append('estate_code')
    
    print(df_joined[cols].head(10))

print("\nDONE")
