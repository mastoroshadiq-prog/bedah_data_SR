"""
CHECK FOR DUPLICATE BLOCKS IN AME ESTATE
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("CHECKING FOR DUPLICATE BLOCKS - AME ESTATE")
print("="*80)

# Load all production data
print("\nLoading production_annual table...")
all_prod = []
page = 0
while True:
    start = page * 1000
    end = start + 999
    response = supabase.table('production_annual').select('*').range(start, end).execute()
    if not response.data:
        break
    all_prod.extend(response.data)
    if len(response.data) < 1000:
        break
    page += 1

df_prod = pd.DataFrame(all_prod)
print(f"Total production records: {len(df_prod)}")

# Load blocks
print("Loading blocks table...")
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
print(f"Total blocks: {len(df_blocks)}")

# Merge
df = df_prod.merge(df_blocks[['id', 'block_code']], 
                   left_on='block_id', right_on='id', 
                   suffixes=('', '_block'), how='left')

# Filter AME blocks
ame_blocks = df[df['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F'])].copy()
print(f"\nAME production records: {len(ame_blocks)}")

print("\n" + "="*80)
print("CHECKING FOR DUPLICATES (same block_id + year)")
print("="*80)

# Check for duplicates by block_id + year
ame_blocks['key'] = ame_blocks['block_id'].astype(str) + '_' + ame_blocks['year'].astype(str)
duplicate_keys = ame_blocks[ame_blocks.duplicated(subset='key', keep=False)]

if len(duplicate_keys) > 0:
    print(f"\n⚠️  FOUND {len(duplicate_keys)} DUPLICATE RECORDS!")
    
    # Group by key to see duplicates
    dup_groups = duplicate_keys.groupby('key')
    
    print(f"\nUnique block+year combinations with duplicates: {len(dup_groups)}")
    
    print("\nSample duplicates:")
    print("="*80)
    
    for i, (key, group) in enumerate(dup_groups):
        if i >= 10:  # Show first 10
            break
        
        block_code = group.iloc[0]['block_code']
        year = group.iloc[0]['year']
        count = len(group)
        
        print(f"\n{block_code} - {year}: {count} records")
        print(group[['id', 'block_code', 'year', 'real_ton', 'potensi_ton']].to_string(index=False))
    
    # Summary by year
    print("\n" + "="*80)
    print("DUPLICATES BY YEAR:")
    print("="*80)
    
    for year in [2023, 2024, 2025]:
        dup_year = duplicate_keys[duplicate_keys['year'] == year]
        unique_blocks = dup_year['block_code'].nunique()
        total_dup_records = len(dup_year)
        print(f"\n{year}:")
        print(f"  Duplicate records: {total_dup_records}")
        print(f"  Unique blocks affected: {unique_blocks}")
    
    # Export duplicates
    output_file = 'output/AME_duplicate_records.csv'
    duplicate_keys[['id', 'block_id', 'block_code', 'year', 'real_ton', 'potensi_ton']].to_csv(output_file, index=False)
    print(f"\n✓ Exported duplicates to: {output_file}")
    
    # Summary stats
    print("\n" + "="*80)
    print("IMPACT ON TOTALS:")
    print("="*80)
    
    for year in [2023, 2024, 2025]:
        # All AME records for this year
        all_year = ame_blocks[ame_blocks['year'] == year]
        
        # Unique records (no duplicates)
        unique_year = all_year.drop_duplicates(subset='key')
        
        # Duplicate records
        dup_year = duplicate_keys[duplicate_keys['year'] == year]
        
        total_with_dup = all_year['real_ton'].sum()
        total_no_dup = unique_year['real_ton'].sum()
        dup_contribution = dup_year['real_ton'].sum()
        
        print(f"\n{year} Actual Production:")
        print(f"  With duplicates: {total_with_dup:,.2f} Ton ({len(all_year)} records)")
        print(f"  Without duplicates: {total_no_dup:,.2f} Ton ({len(unique_year)} records)")
        print(f"  Duplicate contribution: {dup_contribution:,.2f} Ton")
        print(f"  Over-count: {total_with_dup - total_no_dup:,.2f} Ton")

else:
    print("\n✅ NO DUPLICATES FOUND!")
    print("Each block+year combination appears only once.")

# Also check: Are there blocks that appear in multiple years?
print("\n" + "="*80)
print("BLOCKS ACROSS YEARS (This is NORMAL):")
print("="*80)

block_year_count = ame_blocks.groupby('block_code')['year'].nunique()
print(f"\nBlocks appearing in 1 year: {(block_year_count == 1).sum()}")
print(f"Blocks appearing in 2 years: {(block_year_count == 2).sum()}")
print(f"Blocks appearing in 3 years: {(block_year_count == 3).sum()}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if len(duplicate_keys) > 0:
    print(f"\n⚠️  DUPLICATES FOUND: {len(duplicate_keys)} records")
    print(f"   Action required: Remove duplicate records")
    print(f"   File: output/AME_duplicate_records.csv")
else:
    print("\n✅ NO DUPLICATES - Database is clean!")

print("\nDONE")
