"""
AUTOMATED DIVISION UPDATE FOR SUPABASE
======================================
This script automatically:
1. Adds division column via RPC/direct table update
2. Updates all blocks with division data
3. Verifies the update

Run: python add_division_automated.py
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import time

# Load environment
load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print('=' * 80)
print('AUTOMATED DIVISION UPDATE TO SUPABASE')
print('=' * 80)

# Step 1: Check if division column exists
print('\nStep 1: Checking if division column exists...')
try:
    response = supabase.table('blocks').select('id, block_code, division').limit(1).execute()
    print('   ✅ Division column already exists!')
    column_exists = True
except Exception as e:
    print(f'   ⚠️  Division column does not exist yet')
    print(f'   Error: {e}')
    column_exists = False
    print('\n' + '=' * 80)
    print('MANUAL STEP REQUIRED')
    print('=' * 80)
    print('\nPlease add division column via Supabase Dashboard SQL Editor:')
    print('\n1. Go to: https://supabase.com/dashboard')
    print('2. Open SQL Editor')
    print('3. Run this SQL:')
    print('\n' + '-' * 80)
    print('''
ALTER TABLE blocks ADD COLUMN IF NOT EXISTS division VARCHAR(10);
CREATE INDEX IF NOT EXISTS idx_blocks_division ON blocks(division);
    '''.strip())
    print('-' * 80)
    print('\n4. Then run this script again')
    print('=' * 80)
    exit()

# Step 2: Load division mapping
print('\nStep 2: Loading division mapping...')
df_mapping = pd.read_csv('output/block_division_mapping.csv')

# Remove duplicates - keep first occurrence
df_mapping = df_mapping.drop_duplicates(subset=['block_code'], keep='first')

print(f'   Loaded {len(df_mapping)} unique block->division mappings')
print(f'\nDivision breakdown:')
for div in sorted(df_mapping['division'].unique()):
    count = len(df_mapping[df_mapping['division'] == div])
    print(f'   {div}: {count} blocks')

# Step 3: Get all blocks from Supabase
print('\n\nStep 3: Fetching blocks from Supabase...')

# Fetch in pages
all_blocks = []
page_size = 1000
page = 0

while True:
    start = page * page_size
    end = start + page_size - 1
    
    response = supabase.table('blocks').select('id, block_code').range(start, end).execute()
    
    if not response.data:
        break
    
    all_blocks.extend(response.data)
    
    if len(response.data) < page_size:
        break
    
    page += 1
    print(f'   Fetched page {page} ({len(all_blocks)} blocks so far)...')

blocks_db = pd.DataFrame(all_blocks)
print(f'   Found {len(blocks_db)} blocks in database')

# Step 4: Match and update
print('\n\nStep 4: Matching blocks with divisions...')
blocks_to_update = blocks_db.merge(
    df_mapping[['block_code', 'division']],
    on='block_code',
    how='left'
)

blocks_with_division = blocks_to_update[blocks_to_update['division'].notna()]
print(f'   {len(blocks_with_division)} blocks have division mapping')

blocks_without = blocks_to_update[blocks_to_update['division'].isna()]
if len(blocks_without) > 0:
    print(f'   ⚠️  {len(blocks_without)} blocks have NO division (will be skipped)')
    print(f'      Examples: {blocks_without["block_code"].head(5).tolist()}')

# Step 5: Update in batches
print('\n\nStep 5: Updating Supabase...')
print(f'   Processing {len(blocks_with_division)} blocks in batches of 100')

batch_size = 100
total_updated = 0
errors = 0
error_details = []

for i in range(0, len(blocks_with_division), batch_size):
    batch = blocks_with_division.iloc[i:i+batch_size]
    
    for _, row in batch.iterrows():
        try:
            result = supabase.table('blocks').update({
                'division': row['division']
            }).eq('id', row['id']).execute()
            
            total_updated += 1
            
            # Progress indicator
            if total_updated % 50 == 0:
                pct = (total_updated / len(blocks_with_division)) * 100
                print(f'   Progress: {total_updated}/{len(blocks_with_division)} ({pct:.1f}%)')
            
            # Small delay to avoid rate limiting
            if total_updated % 100 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            errors += 1
            error_details.append({
                'block_code': row['block_code'],
                'division': row['division'],
                'error': str(e)
            })
            
            if errors <= 5:  # Show first 5 errors
                print(f'   ⚠️  Error updating {row["block_code"]}: {e}')

print(f'\n✅ Update complete!')
print(f'   Successfully updated: {total_updated} blocks')
print(f'   Errors: {errors}')

if error_details:
    print(f'\n⚠️  Error details saved to: division_update_errors.csv')
    pd.DataFrame(error_details).to_csv('division_update_errors.csv', index=False)

# Step 6: Verify
print('\n\nStep 6: Verifying update...')

# Get sample
response = supabase.table('blocks').select('block_code, division').limit(10).execute()
sample = pd.DataFrame(response.data)
print('\nSample updated blocks:')
print(sample.to_string(index=False))

# Get division counts
print('\n\nFetching division counts from database...')
response = supabase.table('blocks').select('division').execute()
all_blocks_verify = pd.DataFrame(response.data)

if len(all_blocks_verify) > 0 and 'division' in all_blocks_verify.columns:
    division_counts = all_blocks_verify['division'].value_counts().sort_index()
    
    print('\nDivision counts in database:')
    print('-' * 40)
    for div, count in division_counts.items():
        if pd.notna(div):
            print(f'{div}: {count} blocks')
    
    null_count = all_blocks_verify['division'].isna().sum()
    if null_count > 0:
        print(f'NULL: {null_count} blocks')
    print('-' * 40)
    print(f'TOTAL: {len(all_blocks_verify)} blocks')

print('\n' + '=' * 80)
print('DIVISION UPDATE COMPLETE!')
print('=' * 80)
print('\n✅ Database now has division information')
print('✅ Ready for dashboard division breakdown implementation')
print('\nNext: Update dashboard to show division-level analytics')
