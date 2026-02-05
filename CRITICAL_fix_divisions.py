"""
CRITICAL FIX: Division Data Corruption in Supabase
===================================================
Issue: Division column in blocks table contains mixed/wrong estate assignments
Impact: CRITICAL - affects all executive reporting and decision making

This script:
1. Extracts correct division mapping from source file (data_gabungan.xlsx)
2. Validates current Supabase data
3. Fixes division assignments
4. Re-validates after fix
"""
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 100)
print("CRITICAL FIX: Division Data Corruption")
print("=" * 100)
print(f"Started: {datetime.now()}")

# STEP 1: Extract correct division mapping from source
print("\n" + "=" * 100)
print("STEP 1: Extract Correct Division Mapping from Source")
print("=" * 100)

source_file = 'source/data_gabungan.xlsx'
print(f"\nReading source file: {source_file}")

df_source = pd.read_excel(source_file)
print(f"Source records: {len(df_source)}")
print(f"Columns: {df_source.columns.tolist()[:10]}...")  # Show first 10

# Extract block code and division from source
# Assuming columns: KODE_BLOK and DIVISI (adjust if different)
if 'KODE_BLOK' in df_source.columns and 'DIVISI' in df_source.columns:
    df_mapping = df_source[['KODE_BLOK', 'DIVISI']].drop_duplicates()
elif 'kode_blok' in df_source.columns and 'divisi' in df_source.columns:
    df_mapping = df_source[['kode_blok', 'divisi']].drop_duplicates()
    df_mapping.columns = ['KODE_BLOK', 'DIVISI']
else:
    print("\nERROR: Cannot find block code and division columns!")
    print("Available columns:", df_source.columns.tolist())
    exit(1)

print(f"\nUnique block-division mappings: {len(df_mapping)}")
print("\nSample mapping:")
print(df_mapping.head(20))

# Validate mapping per estate
df_mapping['estate_letter'] = df_mapping['KODE_BLOK'].str[0]
estate_map = {
    'A': 'AME', 'B': 'AME', 'E': 'AME', 'F': 'AME',
    'O': 'OLE', 'C': 'OLE', 'K': 'OLE', 'L': 'OLE',
    'D': 'DBE', 'M': 'DBE', 'N': 'DBE'
}
df_mapping['estate'] = df_mapping['estate_letter'].map(estate_map)

print("\nDivisions per estate in SOURCE:")
for estate in ['AME', 'OLE', 'DBE']:
    divisions = df_mapping[df_mapping['estate'] == estate]['DIVISI'].unique()
    print(f"  {estate}: {len(divisions)} divisions - {sorted(divisions)}")

# STEP 2: Check current Supabase data
print("\n" + "=" * 100)
print("STEP 2: Validate Current Supabase Data (BEFORE FIX)")
print("=" * 100)

blocks_response = supabase.table('blocks').select('id, block_code, division').execute()
df_blocks = pd.DataFrame(blocks_response.data)

print(f"\nTotal blocks in Supabase: {len(df_blocks)}")
print(f"Blocks with division: {df_blocks['division'].notna().sum()}")

# Check division distribution
df_blocks['estate_letter'] = df_blocks['block_code'].str[0]
df_blocks['estate'] = df_blocks['estate_letter'].map(estate_map)

print("\nDivisions per estate in SUPABASE (CURRENT - CORRUPTED):")
corruption_count = 0
for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df_blocks[df_blocks['estate'] == estate]
    divisions = df_estate[df_estate['division'].notna()]['division'].unique()
    print(f"  {estate}: {len(divisions)} divisions - {sorted(divisions)}")
    
    # Check for foreign divisions
    source_divs = set(df_mapping[df_mapping['estate'] == estate]['DIVISI'].unique())
    current_divs = set(divisions)
    foreign_divs = current_divs - source_divs
    if foreign_divs:
        print(f"    ❌ CORRUPT: {len(foreign_divs)} foreign divisions: {sorted(foreign_divs)}")
        corruption_count += len(df_estate[df_estate['division'].isin(foreign_divs)])

print(f"\n❌ Total corrupted records: {corruption_count}")

# STEP 3: Create fix mapping
print("\n" + "=" * 100)
print("STEP 3: Create Correct Division Mapping")
print("=" * 100)

# Merge source mapping with current blocks
df_blocks_fix = df_blocks[['id', 'block_code']].merge(
    df_mapping[['KODE_BLOK', 'DIVISI']],
    left_on='block_code',
    right_on='KODE_BLOK',
    how='left'
)

# Count how many will be updated
updates_needed = df_blocks_fix[df_blocks_fix['DIVISI'] != df_blocks.set_index('id').loc[df_blocks_fix['id'].values, 'division'].values]
print(f"\nRecords needing update: {len(updates_needed)}")

if len(updates_needed) > 0:
    print("\nSample updates:")
    for idx in updates_needed.head(10).index:
        old = df_blocks.loc[df_blocks['id'] == df_blocks_fix.loc[idx, 'id'], 'division'].values[0]
        new = df_blocks_fix.loc[idx, 'DIVISI']
        code = df_blocks_fix.loc[idx, 'block_code']
        print(f"  {code}: {old} -> {new}")

# STEP 4: Execute fix  
print("\n" + "=" * 100)
print("STEP 4: Execute Fix in Supabase")
print("=" * 100)

proceed = input("\n⚠️ This will UPDATE division data in Supabase. Proceed? (yes/no): ")

if proceed.lower() == 'yes':
    print("\nUpdating divisions...")
    update_count = 0
    error_count = 0
    
    for idx, row in df_blocks_fix.iterrows():
        try:
            result = supabase.table('blocks').update({
                'division': row['DIVISI']
            }).eq('id', row['id']).execute()
            
            update_count += 1
            if update_count % 100 == 0:
                print(f"  Updated {update_count} records...")
        except Exception as e:
            print(f"  ERROR updating block {row['block_code']}: {e}")
            error_count += 1
    
    print(f"\n✅ Update complete!")
    print(f"  Updated: {update_count}")
    print(f"  Errors: {error_count}")
    
    # STEP 5: Re-validate
    print("\n" + "=" * 100)
    print("STEP 5: Validate After Fix")
    print("=" * 100)
    
    blocks_after = supabase.table('blocks').select('id, block_code, division').execute()
    df_after = pd.DataFrame(blocks_after.data)
    df_after['estate_letter'] = df_after['block_code'].str[0]
    df_after['estate'] = df_after['estate_letter'].map(estate_map)
    
    print("\nDivisions per estate AFTER FIX:")
    all_correct = True
    for estate in ['AME', 'OLE', 'DBE']:
        df_estate = df_after[df_after['estate'] == estate]
        divisions = df_estate[df_estate['division'].notna()]['division'].unique()
        expected_divs = df_mapping[df_mapping['estate'] == estate]['DIVISI'].unique()
        
        print(f"  {estate}: {len(divisions)} divisions - {sorted(divisions)}")
        print(f"    Expected: {len(expected_divs)} divisions - {sorted(expected_divs)}")
        
        if set(divisions) == set(expected_divs):
            print(f"    ✅ CORRECT!")
        else:
            print(f"    ❌ MISMATCH!")
            all_correct = False
    
    if all_correct:
        print("\n" + "=" * 100)
        print("✅ FIX SUCCESSFUL - ALL DIVISIONS CORRECT")
        print("=" * 100)
    else:
        print("\n" + "=" * 100)
        print("⚠️ VERIFICATION FAILED - MANUAL REVIEW NEEDED")
        print("=" * 100)
else:
    print("\n❌ Fix cancelled by user")

print(f"\nCompleted: {datetime.now()}")
