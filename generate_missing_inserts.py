"""
Generate SQL INSERT for 3 missing blocks
A001A, A002A, C006A - these exist in blocks table but missing 2023 production data
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("GENERATE SQL INSERT FOR MISSING BLOCKS")
print("="*80)

# Load Excel
df_excel = pd.read_excel('source/data_produksi_AME_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)

df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel['Potensi'] = pd.to_numeric(df_excel['Potensi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

# Load blocks table
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

# Blocks that exist in blocks table but missing production data
missing_with_data = ['A001A', 'A002A', 'C006A']

print(f"\nBlocks to INSERT: {len(missing_with_data)}")
print("="*80)

sql_statements = []

for block_code in missing_with_data:
    # Get data from Excel
    excel_row = df_excel[df_excel['BLOCK'] == block_code]
    
    if len(excel_row) == 0:
        print(f"\n⚠️  {block_code}: Not found in Excel!")
        continue
    
    excel_row = excel_row.iloc[0]
    real_ton = excel_row['Realisasi']
    potensi_ton = excel_row['Potensi']
    
    # Get block_id from blocks table
    block_row = df_blocks[df_blocks['block_code'] == block_code]
    
    if len(block_row) == 0:
        print(f"\n⚠️  {block_code}: Not in blocks table!")
        continue
    
    block_id = block_row.iloc[0]['id']
    
    # Generate SQL
    sql = f"INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES ({block_id}, 2023, {real_ton}, {potensi_ton}); -- {block_code}"
    sql_statements.append(sql)
    
    print(f"\n✓ {block_code}:")
    print(f"  block_id: {block_id}")
    print(f"  Actual: {real_ton:.2f} Ton")
    print(f"  Target: {potensi_ton:.2f} Ton")

# Calculate totals
total_actual = sum([df_excel[df_excel['BLOCK'] == b]['Realisasi'].iloc[0] for b in missing_with_data if len(df_excel[df_excel['BLOCK'] == b]) > 0])
total_target = sum([df_excel[df_excel['BLOCK'] == b]['Potensi'].iloc[0] for b in missing_with_data if len(df_excel[df_excel['BLOCK'] == b]) > 0])

print("\n" + "="*80)
print("TOTALS FOR 3 BLOCKS:")
print("="*80)
print(f"Actual: {total_actual:,.2f} Ton")
print(f"Target: {total_target:,.2f} Ton")

# Save to file
if sql_statements:
    output_file = 'insert_missing_ame_2023.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- INSERT MISSING AME 2023 BLOCKS\n")
        f.write("-- Blocks: A001A, A002A, C006A\n")
        f.write(f"-- Total: {len(sql_statements)} records\n")
        f.write(f"-- Actual: {total_actual:.2f} Ton\n")
        f.write(f"-- Target: {total_target:.2f} Ton\n\n")
        
        for sql in sql_statements:
            f.write(sql + "\n")
        
        f.write("\n-- VERIFY after running:\n")
        f.write("-- Check that these 3 blocks now appear in AME 2023 data\n")
        f.write("""
SELECT b.block_code, p.year, p.real_ton, p.potensi_ton
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND b.block_code IN ('A001A', 'A002A', 'C006A')
ORDER BY b.block_code;
""")
    
    print(f"\n✓ SQL saved to: {output_file}")
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print(f"1. Review '{output_file}'")
    print(f"2. Execute SQL in Supabase")
    print(f"3. Run verification query")
    print(f"4. Discrepancy should reduce from 1,234 Ton to ~0 Ton")

else:
    print("\n⚠️  No SQL generated!")

print("\nDONE")
