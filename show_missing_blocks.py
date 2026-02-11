"""
Show MISSING BLOCKS - blocks in Excel but not in Supabase
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("MISSING BLOCKS IN SUPABASE - AME 2023")
print("="*80)

# Load Excel
df_excel = pd.read_excel('source/data_produksi_AME_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

# Load Supabase
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
divisions_data = supabase.table('divisions').select('*').execute()
df_divisions = pd.DataFrame(divisions_data.data)
estates_data = supabase.table('estates').select('*').execute()
df_estates = pd.DataFrame(estates_data.data)

# Build hierarchy
df = df_prod.merge(df_blocks[['id', 'block_code', 'division_id']], 
                   left_on='block_id', right_on='id', suffixes=('', '_block'), how='left')
df = df.merge(df_divisions[['id', 'estate_id']], 
              left_on='division_id', right_on='id', suffixes=('', '_div'), how='left')
df = df.merge(df_estates[['id', 'estate_code']], 
              left_on='estate_id', right_on='id', suffixes=('', '_estate'), how='left')

df_ame_2023 = df[(df['year'] == 2023) & (df['estate_code'] == 'AME')]

# Find missing
excel_blocks = set(df_excel['BLOCK'].unique())
db_blocks = set(df_ame_2023['block_code'].unique())
missing = excel_blocks - db_blocks

print(f"\nMISSING BLOCKS: {len(missing)}")
print("="*80)

if missing:
    # Get data from Excel for missing blocks
    df_missing = df_excel[df_excel['BLOCK'].isin(missing)].copy()
    df_missing = df_missing.sort_values('BLOCK')
    
    print("\nBlocks in Excel but NOT in Supabase:")
    print("\n{:<10} {:>15} {:>15} {:>15}".format(
        "Block", "Divisi", "Realisasi (Ton)", "Potensi (Ton)"))
    print("-"*80)
    
    total_missing_actual = 0
    total_missing_target = 0
    
    for _, row in df_missing.iterrows():
        block = row['BLOCK']
        divisi = row['DIVISI'] if 'DIVISI' in df_missing.columns else 'N/A'
        actual = row['Realisasi']
        target = row['Potensi']
        
        print("{:<10} {:>15} {:>15,.2f} {:>15,.2f}".format(
            block, str(divisi), actual, target))
        
        total_missing_actual += actual
        total_missing_target += target
    
    print("-"*80)
    print("{:<10} {:>15} {:>15,.2f} {:>15,.2f}".format(
        "TOTAL", "", total_missing_actual, total_missing_target))
    
    print("\n" + "="*80)
    print("IMPACT OF MISSING BLOCKS:")
    print("="*80)
    print(f"\nProduction lost due to missing blocks:")
    print(f"  Actual: {total_missing_actual:,.2f} Ton")
    print(f"  Target: {total_missing_target:,.2f} Ton")
    
    excel_total_actual = df_excel['Realisasi'].sum()
    excel_total_target = df_excel['Potensi'].sum()
    
    print(f"\nPercentage of total Excel data:")
    print(f"  Actual: {total_missing_actual/excel_total_actual*100:.2f}%")
    print(f"  Target: {total_missing_target/excel_total_target*100:.2f}%")
    
    # Check if these blocks exist in blocks table at all
    print("\n" + "="*80)
    print("CHECK: Do these blocks exist in blocks table?")
    print("="*80)
    
    all_block_codes = set(df_blocks['block_code'].unique())
    
    for block in sorted(missing):
        if block in all_block_codes:
            # Block exists but not in AME 2023
            block_info = df_blocks[df_blocks['block_code'] == block].iloc[0]
            div_id = block_info['division_id']
            
            # Check which estate
            if pd.notna(div_id):
                div_info = df_divisions[df_divisions['id'] == div_id]
                if len(div_info) > 0:
                    estate_id = div_info.iloc[0]['estate_id']
                    estate_info = df_estates[df_estates['id'] == estate_id]
                    if len(estate_info) > 0:
                        estate_code = estate_info.iloc[0]['estate_code']
                        print(f"  {block}: EXISTS in blocks table (Estate: {estate_code})")
                    else:
                        print(f"  {block}: EXISTS in blocks table (estate_id {estate_id} not found)")
                else:
                    print(f"  {block}: EXISTS in blocks table (division not found)")
            else:
                print(f"  {block}: EXISTS in blocks table (no division)")
        else:
            print(f"  {block}: NOT in blocks table at all!")
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("="*80)
    
    not_in_blocks = [b for b in missing if b not in all_block_codes]
    exists_but_no_data = [b for b in missing if b in all_block_codes]
    
    if not_in_blocks:
        print(f"\n{len(not_in_blocks)} blocks need to be ADDED to blocks table first:")
        for block in sorted(not_in_blocks):
            print(f"  - {block}")
    
    if exists_but_no_data:
        print(f"\n{len(exists_but_no_data)} blocks exist but missing 2023 production data:")
        for block in sorted(exists_but_no_data):
            excel_data = df_missing[df_missing['BLOCK'] == block].iloc[0]
            print(f"  - {block}: Need to INSERT ({excel_data['Realisasi']:.2f} Ton actual)")

else:
    print("\nNo missing blocks - all Excel blocks are in Supabase!")

print("\nDONE")
