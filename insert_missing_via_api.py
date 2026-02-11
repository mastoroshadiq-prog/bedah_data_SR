"""
INSERT MISSING BLOCKS via Supabase API
This avoids SQL id auto-increment issues
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("INSERT MISSING AME 2023 BLOCKS - Via API")
print("="*80)

# Data to insert
blocks_to_insert = [
    {'block_id': 1, 'block_code': 'A001A', 'real_ton': 181.76, 'potensi_ton': 175.17},
    {'block_id': 3, 'block_code': 'A002A', 'real_ton': 464.79, 'potensi_ton': 539.51},
    {'block_id': 2, 'block_code': 'C006A', 'real_ton': 587.74, 'potensi_ton': 658.04}
]

year = 2023

print(f"\nInserting {len(blocks_to_insert)} blocks for year {year}...")
print("="*80)

success_count = 0
errors = []

for block_data in blocks_to_insert:
    block_id = block_data['block_id']
    block_code = block_data['block_code']
    real_ton = block_data['real_ton']
    potensi_ton = block_data['potensi_ton']
    
    # Calculate gaps
    gap_ton = real_ton - potensi_ton
    gap_pct_ton = (gap_ton / potensi_ton * 100) if potensi_ton > 0 else 0
    
    # Prepare insert data
    insert_data = {
        'block_id': block_id,
        'year': year,
        'real_ton': real_ton,
        'potensi_ton': potensi_ton,
        'gap_ton': gap_ton,
        'gap_pct_ton': gap_pct_ton
    }
    
    try:
        print(f"\nInserting {block_code}...")
        print(f"  block_id: {block_id}")
        print(f"  real_ton: {real_ton:.2f}")
        print(f"  potensi_ton: {potensi_ton:.2f}")
        print(f"  gap_ton: {gap_ton:.2f}")
        print(f"  gap_pct_ton: {gap_pct_ton:.2f}%")
        
        result = supabase.table('production_annual').insert(insert_data).execute()
        
        if result.data:
            print(f"  ✓ SUCCESS - Record inserted with id: {result.data[0]['id']}")
            success_count += 1
        else:
            print(f"  ✗ FAILED - No data returned")
            errors.append(f"{block_code}: No data returned")
            
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")
        errors.append(f"{block_code}: {str(e)}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Successful inserts: {success_count}/{len(blocks_to_insert)}")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for err in errors:
        print(f"  - {err}")
else:
    print("\n✓ All blocks inserted successfully!")

# Verify
if success_count > 0:
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    # Load and check
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
    blocks_data = supabase.table('blocks').select('*').execute()
    df_blocks = pd.DataFrame(blocks_data.data)
    
    df = df_prod.merge(df_blocks[['id', 'block_code']], 
                       left_on='block_id', right_on='id', 
                       suffixes=('', '_block'), how='left')
    
    # Check for inserted blocks
    inserted_blocks = [b['block_code'] for b in blocks_to_insert]
    df_check = df[(df['year'] == 2023) & (df['block_code'].isin(inserted_blocks))]
    
    print(f"\nFound {len(df_check)} records for inserted blocks:")
    if len(df_check) > 0:
        print(df_check[['block_code', 'year', 'real_ton', 'potensi_ton', 'gap_ton']].to_string(index=False))
    
    # Re-check AME 2023 totals
    divisions_data = supabase.table('divisions').select('*').execute()
    df_divisions = pd.DataFrame(divisions_data.data)
    estates_data = supabase.table('estates').select('*').execute()
    df_estates = pd.DataFrame(estates_data.data)
    
    df_full = df.merge(df_divisions[['id', 'estate_id']], 
                       left_on='division_id', right_on='id', 
                       suffixes=('', '_div'), how='left')
    df_full = df_full.merge(df_estates[['id', 'estate_code']], 
                            left_on='estate_id', right_on='id', 
                            suffixes=('', '_estate'), how='left')
    
    df_ame_2023 = df_full[(df_full['year'] == 2023) & (df_full['estate_code'] == 'AME')]
    
    total_actual = df_ame_2023['real_ton'].sum()
    total_target = df_ame_2023['potensi_ton'].sum()
    
    print(f"\n" + "="*80)
    print("NEW AME 2023 TOTALS (After Insert):")
    print("="*80)
    print(f"Blocks: {len(df_ame_2023)}")
    print(f"Actual: {total_actual:,.2f} Ton")
    print(f"Target: {total_target:,.2f} Ton")
    
    # Compare with Excel
    excel_actual = 42880.24
    excel_target = 51480.38
    
    print(f"\nExpected (from Excel):")
    print(f"Actual: {excel_actual:,.2f} Ton")
    print(f"Target: {excel_target:,.2f} Ton")
    
    print(f"\nRemaining discrepancy:")
    print(f"Actual: {abs(total_actual - excel_actual):,.2f} Ton")
    print(f"Target: {abs(total_target - excel_target):,.2f} Ton")

print("\nDONE")
