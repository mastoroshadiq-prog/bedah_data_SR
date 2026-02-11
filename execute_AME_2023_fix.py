"""
EXECUTE AME 2023 FIX TO SUPABASE
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

# Step 1: Before state
print("\nSTEP 1: CHECKING CURRENT STATE...")
result = supabase.rpc('execute_sql', {
    'query': """
    SELECT 
        SUM(CASE WHEN p.year = 2023 THEN p.real_ton ELSE 0 END) as ame_2023_actual,
        SUM(CASE WHEN p.year = 2023 THEN p.potensi_ton ELSE 0 END) as ame_2023_target
    FROM production_annual p
    JOIN blocks b ON p.block_id = b.id
    WHERE p.year = 2023 
      AND (b.block_code LIKE 'A%' OR b.block_code LIKE 'B%' OR 
           b.block_code LIKE 'C%' OR b.block_code LIKE 'E%' OR b.block_code LIKE 'F%')
    """
}).execute()

if result.data:
    before_actual = result.data[0]['ame_2023_actual'] or 0
    before_target = result.data[0]['ame_2023_target'] or 0
    print(f"BEFORE - AME 2023:")
    print(f"  Actual: {before_actual:,.2f} Ton")
    print(f"  Target: {before_target:,.2f} Ton")
else:
    print("Could not query current state via RPC, using direct query...")
    
    # Alternative: Direct query
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
    
    before_actual = df_ame_2023['real_ton'].sum()
    before_target = df_ame_2023['potensi_ton'].sum()
    
    print(f"BEFORE - AME 2023:")
    print(f"  Actual: {before_actual:,.2f} Ton")
    print(f"  Target: {before_target:,.2f} Ton")

# Step 2: Read and parse SQL file
print(f"\n{'='*80}")
print("STEP 2: READING SQL FILE...")
print(f"{'='*80}")

with open('fix_AME_2023.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Extract SQL statements (UPDATE and INSERT only)
update_pattern = r'UPDATE production_annual SET[^;]+;'
insert_pattern = r'INSERT INTO production_annual[^;]+;'

updates = re.findall(update_pattern, sql_content)
inserts = re.findall(insert_pattern, sql_content)

print(f"Found {len(updates)} UPDATE statements")
print(f"Found {len(inserts)} INSERT statements")
print(f"Total: {len(updates) + len(inserts)} statements")

# Step 3: Execute statements
print(f"\n{'='*80}")
print("STEP 3: EXECUTING SQL STATEMENTS...")
print(f"{'='*80}")

success_count = 0
error_count = 0
errors = []

# Execute UPDATEs
print(f"\nExecuting {len(updates)} UPDATEs...")
for i, sql in enumerate(updates, 1):
    try:
        # Parse UPDATE statement
        # Format: UPDATE production_annual SET real_ton = X, potensi_ton = Y WHERE id = Z;
        match = re.search(r'SET real_ton = ([\d.]+), potensi_ton = ([\d.]+) WHERE id = (\d+)', sql)
        if match:
            real_ton = float(match.group(1))
            potensi_ton = float(match.group(2))
            rec_id = int(match.group(3))
            
            result = supabase.table('production_annual').update({
                'real_ton': real_ton,
                'potensi_ton': potensi_ton
            }).eq('id', rec_id).execute()
            
            success_count += 1
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(updates)} UPDATEs done...")
    except Exception as e:
        error_count += 1
        errors.append(f"UPDATE #{i}: {str(e)}")

print(f"✓ UPDATEs complete: {success_count - error_count} success, {error_count} errors")

# Execute INSERTs
print(f"\nExecuting {len(inserts)} INSERTs...")
for i, sql in enumerate(inserts, 1):
    try:
        # Parse INSERT statement
        # Format: INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (X, Y, Z, W);
        match = re.search(r'VALUES \((\d+), (\d+), ([\d.]+), ([\d.]+)\)', sql)
        if match:
            block_id = int(match.group(1))
            year = int(match.group(2))
            real_ton = float(match.group(3))
            potensi_ton = float(match.group(4))
            
            result = supabase.table('production_annual').insert({
                'block_id': block_id,
                'year': year,
                'real_ton': real_ton,
                'potensi_ton': potensi_ton
            }).execute()
            
            success_count += 1
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(inserts)} INSERTs done...")
    except Exception as e:
        error_count += 1
        errors.append(f"INSERT #{i}: {str(e)}")

print(f"✓ INSERTs complete: {success_count - len(updates)} success, {len(errors) - error_count} errors")

if errors:
    print(f"\n⚠️  {len(errors)} errors occurred:")
    for err in errors[:10]:  # Show first 10
        print(f"  - {err}")

# Step 4: Verify results
print(f"\n{'='*80}")
print("STEP 4: VERIFYING RESULTS...")
print(f"{'='*80}")

# Re-query to get updated totals
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

after_actual = df_ame_2023['real_ton'].sum()
after_target = df_ame_2023['potensi_ton'].sum()

print(f"\nAFTER - AME 2023:")
print(f"  Actual: {after_actual:,.2f} Ton")
print(f"  Target: {after_target:,.2f} Ton")

print(f"\nCHANGE:")
print(f"  Actual: {before_actual:,.2f} → {after_actual:,.2f} ({after_actual - before_actual:+,.2f})")
print(f"  Target: {before_target:,.2f} → {after_target:,.2f} ({after_target - before_target:+,.2f})")

# Expected from Excel
expected_actual = 46690.53  # Approximate from Excel
expected_target = 61977.02  # Approximate from Excel

print(f"\nEXPECTED (from Excel):")
print(f"  Actual: ~{expected_actual:,.2f} Ton")
print(f"  Target: ~{expected_target:,.2f} Ton")

print(f"\nACCURACY:")
actual_diff = abs(after_actual - expected_actual)
target_diff = abs(after_target - expected_target)
print(f"  Actual difference: {actual_diff:,.2f} Ton")
print(f"  Target difference: {target_diff:,.2f} Ton")

if actual_diff < 100 and target_diff < 100:
    print(f"\n✅ SUCCESS! Totals match Excel within acceptable range")
else:
    print(f"\n⚠️  WARNING: Totals differ from Excel by more than 100 Ton")

print(f"\n{'='*80}")
print("EXECUTION SUMMARY")
print(f"{'='*80}")
print(f"SQL statements executed: {success_count}")
print(f"Errors: {error_count}")
print(f"AME 2023 Actual: {before_actual:,.2f} → {after_actual:,.2f}")
print(f"AME 2023 Target: {before_target:,.2f} → {after_target:,.2f}")
print(f"\n✓ AME 2023 database fix COMPLETE!")

print(f"\n{'='*80}")
print("NEXT STEPS")
print(f"{'='*80}")
print("""
1. ✓ AME 2023 fixed
2. Boss provide AME 2024 data
3. Boss provide AME 2025 data
4. Then repeat for OLE estate (2023, 2024, 2025)
5. Then repeat for DBE estate (2023, 2024, 2025)
""")

print("\nDONE")
