"""
Extract Block-Division Mapping from data_gabungan.xlsx
Using BARU (new) columns as source of truth
"""
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 80)
print("EXTRACTING BLOCK-DIVISION MAPPING FROM SOURCE")
print("=" * 80)

# Read Excel with header at row 6 (0-indexed row 6 = row 7 in Excel)
df = pd.read_excel('source/data_gabungan.xlsx', header=6)

print(f"\nTotal rows in source: {len(df)}")

# Get column names to identify BARU columns
print("\nFirst 10 column names:")
for i, col in enumerate(df.columns[:10]):
    print(f"{i}: {col}")

# Based on screenshot:
# - Estate BARU should be around column 1 (C002 in Excel)
# - Divisi BARU should be around column 3 (C004 in Excel)
# - Blok BARU should be around column 5 (C006 in Excel)

# Find columns with 'C00' pattern (these seem to be the BARU columns)
baru_cols = [col for col in df.columns if isinstance(col, str) and col.startswith('C00')]
print(f"\nColumns starting with C00: {baru_cols[:10]}")

# Based on header image: C002=Estate, C004=Divisi, C006=Blok
if 'C002' in df.columns and 'C004' in df.columns and 'C006' in df.columns:
    print("\n✅ Found BARU columns!")
    
    # Extract mapping
    df_mapping = df[['C006', 'C004']].copy()
    df_mapping.columns = ['block_code', 'division_code']
    
    # Remove NaN
    df_mapping = df_mapping.dropna()
    
    # Remove duplicates
    df_mapping = df_mapping.drop_duplicates()
    
    print(f"\nUnique block-division mappings: {len(df_mapping)}")
    
    # Show sample
    print("\nSample mappings (first 20):")
    print(df_mapping.head(20).to_string(index=False))
    
    # Show division distribution
    print("\nBlocks per division:")
    div_counts = df_mapping['division_code'].value_counts().sort_index()
    for div, count in div_counts.items():
        print(f"  {div}: {count} blocks")
    
    # Save to CSV for verification
    df_mapping.to_csv('block_division_mapping.csv', index=False)
    print("\n✅ Saved to block_division_mapping.csv")
    
    # Now update Supabase
    print("\n" + "=" * 80)
    print("UPDATING SUPABASE")
    print("=" * 80)
    
    # Get divisions table to map division_code to division_id
    divs = supabase.table('divisions').select('id, division_code').execute()
    div_map = {d['division_code']: d['id'] for d in divs.data}
    
    # Get blocks table
    blocks = supabase.table('blocks').select('id, block_code').execute()
    block_map = {b['block_code']: b['id'] for b in blocks.data}
    
    # Update each block
    update_count = 0
    not_found = []
    
    for _, row in df_mapping.iterrows():
        block_code = row['block_code']
        division_code = row['division_code']
        
        # Get IDs
        block_id = block_map.get(block_code)
        division_id = div_map.get(division_code)
        
        if block_id and division_id:
            try:
                supabase.table('blocks').update({
                    'division_id': division_id
                }).eq('id', block_id).execute()
                update_count += 1
                
                if update_count % 50 == 0:
                    print(f"  Updated {update_count} blocks...")
            except Exception as e:
                print(f"  Error updating {block_code}: {e}")
        else:
            if not block_id:
                not_found.append(f"{block_code} (block not in DB)")
            if not division_id:
                not_found.append(f"{division_code} (division not in DB)")
    
    print(f"\n✅ Updated {update_count} blocks with division assignments")
    
    if not_found:
        print(f"\nWarning: {len(not_found)} items not found in DB (first 10):")
        for item in not_found[:10]:
            print(f"  {item}")
    
    print("\n✅ MAPPING COMPLETE!")
    
else:
    print("\n❌ BARU columns not found!")
    print("Available columns:", df.columns.tolist()[:20])
