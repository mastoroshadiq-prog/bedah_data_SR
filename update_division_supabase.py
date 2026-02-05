"""
UPDATE SUPABASE WITH DIVISION DATA
===================================
This script:
1. Adds division column to blocks and estates tables
2. Updates all blocks with their division info
3. Verifies the update
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment
load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print('=' * 80)
print('ADDING DIVISION COLUMN TO SUPABASE')
print('=' * 80)

# Step 1: Execute SQL to add column
print('\nStep 1: Adding division column to tables...')
with open('output/sql_schema/add_division_column.sql', 'r') as f:
    sql_commands = f.read().split(';')
    
for sql in sql_commands:
    sql = sql.strip()
    if sql and not sql.startswith('--') and not sql.startswith('COMMENT'):
        try:
            # Note: Supabase Python client doesn't support raw SQL execution
            # We'll update via API instead
            print(f'  SQL command prepared: {sql[:50]}...')
        except Exception as e:
            print(f'  Note: {e}')

print('\n⚠️  Note: Column addition must be done via Supabase Dashboard SQL Editor')
print('   Please run: output/sql_schema/add_division_column.sql')
print('\n   OR we can proceed with data update assuming column exists.')

proceed = input('\nHas division column been added? (y/n): ').lower()

if proceed != 'y':
    print('\n❌ Please add division column first via Supabase Dashboard')
    print('   Then run this script again.')
    exit()

# Step 2: Load division mapping
print('\n\nStep 2: Loading division mapping...')
df_mapping = pd.read_csv('output/block_division_mapping.csv')
print(f'   Loaded {len(df_mapping)} block->division mappings')

# Step 3: Update blocks in Supabase
print('\n\nStep 3: Updating blocks with division info...')

# Get all blocks from Supabase
response = supabase.table('blocks').select('id, block_code').execute()
blocks_db = pd.DataFrame(response.data)
print(f'   Found {len(blocks_db)} blocks in database')

# Merge with division mapping
blocks_to_update = blocks_db.merge(
    df_mapping[['block_code', 'division']],
    on='block_code',
    how='left'
)

# Filter blocks that have division
blocks_with_division = blocks_to_update[blocks_to_update['division'].notna()]
print(f'   {len(blocks_with_division)} blocks have division mapping')

# Update in batches
batch_size = 100
total_updated = 0
errors = 0

for i in range(0, len(blocks_with_division), batch_size):
    batch = blocks_with_division.iloc[i:i+batch_size]
    
    for _, row in batch.iterrows():
        try:
            supabase.table('blocks').update({
                'division': row['division']
            }).eq('id', row['id']).execute()
            
            total_updated += 1
            
            if total_updated % 50 == 0:
                print(f'   Updated {total_updated}/{len(blocks_with_division)} blocks...')
                
        except Exception as e:
            print(f'   Error updating block {row["block_code"]}: {e}')
            errors += 1

print(f'\n✅ Update complete!')
print(f'   Successfully updated: {total_updated} blocks')
print(f'   Errors: {errors}')

# Step 4: Verify
print('\n\nStep 4: Verifying update...')
response = supabase.table('blocks').select('block_code, division').limit(10).execute()
sample = pd.DataFrame(response.data)
print('\nSample updated blocks:')
print(sample)

# Count by division
response = supabase.table('blocks').select('division').execute()
all_blocks = pd.DataFrame(response.data)
if len(all_blocks) > 0:
    division_counts = all_blocks['division'].value_counts()
    print('\n\nDivision counts in database:')
    print(division_counts)

print('\n' + '=' * 80)
print('DIVISION UPDATE COMPLETE!')
print('=' * 80)
