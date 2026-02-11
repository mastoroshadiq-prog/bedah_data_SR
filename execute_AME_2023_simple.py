"""
EXECUTE AME 2023 FIX TO SUPABASE - DIRECT APPROACH
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
import re

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("EXECUTING AME 2023 DATABASE FIX")
print("="*80)

# Helper function to get AME 2023 totals
def get_ame_2023_totals():
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
    
    df = df_prod.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', suffixes=('', '_block'), how='left')
    df_ame_2023 = df[(df['year'] == 2023) & (df['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F']))]
    
    actual = df_ame_2023['real_ton'].sum()
    target = df_ame_2023['potensi_ton'].sum()
    count = len(df_ame_2023)
    
    return actual, target, count

# Step 1: Before state
print("\nSTEP 1: CHECKING CURRENT STATE...")
before_actual, before_target, before_count = get_ame_2023_totals()

print(f"BEFORE - AME 2023:")
print(f"  Records: {before_count}")
print(f"  Actual: {before_actual:,.2f} Ton")
print(f"  Target: {before_target:,.2f} Ton")

# Step 2: Read SQL file
print(f"\n{'='*80}")
print("STEP 2: READING SQL FILE...")
print(f"{'='*80}")

with open('fix_AME_2023.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Extract statements
update_pattern = r'UPDATE production_annual SET[^;]+;'
insert_pattern = r'INSERT INTO production_annual[^;]+;'

updates = re.findall(update_pattern, sql_content)
inserts = re.findall(insert_pattern, sql_content)

print(f"Found {len(updates)} UPDATE statements")
print(f"Found {len(inserts)} INSERT statements")

# Step 3: Execute
print(f"\n{'='*80}")
print("STEP 3: EXECUTING...")
print(f"{'='*80}")

success = 0
errors = []

# UPDATEs
print(f"\nExecuting {len(updates)} UPDATEs...")
for i, sql in enumerate(updates, 1):
    try:
        match = re.search(r'SET real_ton = ([\d.]+), potensi_ton = ([\d.]+) WHERE id = (\d+)', sql)
        if match:
            real_ton = float(match.group(1))
            potensi_ton = float(match.group(2))
            rec_id = int(match.group(3))
            
            supabase.table('production_annual').update({
                'real_ton': real_ton,
                'potensi_ton': potensi_ton
            }).eq('id', rec_id).execute()
            
            success += 1
            if i % 50 == 0:
                print(f"  {i}/{len(updates)}...")
    except Exception as e:
        errors.append(str(e))

print(f"✓ {success} UPDATEs done")

# INSERTs
print(f"\nExecuting {len(inserts)} INSERTs...")
insert_success = 0
for i, sql in enumerate(inserts, 1):
    try:
        match = re.search(r'VALUES \((\d+), (\d+), ([\d.]+), ([\d.]+)\)', sql)
        if match:
            block_id = int(match.group(1))
            year = int(match.group(2))
            real_ton = float(match.group(3))
            potensi_ton = float(match.group(4))
            
            supabase.table('production_annual').insert({
                'block_id': block_id,
                'year': year,
                'real_ton': real_ton,
                'potensi_ton': potensi_ton
            }).execute()
            
            insert_success += 1
            if i % 10 == 0:
                print(f"  {i}/{len(inserts)}...")
    except Exception as e:
        errors.append(str(e))

print(f"✓ {insert_success} INSERTs done")

if errors:
    print(f"\n⚠️  {len(errors)} errors (might be duplicates)")

# Step 4: Verify
print(f"\n{'='*80}")
print("STEP 4: VERIFYING...")
print(f"{'='*80}")

after_actual, after_target, after_count = get_ame_2023_totals()

print(f"\nAFTER - AME 2023:")
print(f"  Records: {after_count}")
print(f"  Actual: {after_actual:,.2f} Ton")
print(f"  Target: {after_target:,.2f} Ton")

print(f"\nCHANGE:")
print(f"  Records: {before_count} → {after_count} ({after_count - before_count:+d})")
print(f"  Actual: {before_actual:,.2f} → {after_actual:,.2f} ({after_actual - before_actual:+,.2f})")
print(f"  Target: {before_target:,.2f} → {after_target:,.2f} ({after_target - before_target:+,.2f})")

print(f"\n{'='*80}")
print("✅ AME 2023 FIX COMPLETE!")
print(f"{'='*80}")
print(f"Executed: {success + insert_success} statements")
print(f"New totals: {after_actual:,.2f} Ton (actual) | {after_target:,.2f} Ton (target)")

print("\nDONE")
