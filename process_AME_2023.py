"""
Process AME 2023 production data and generate SQL fix statements
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("PROCESSING AME 2023 PRODUCTION DATA")
print("="*80)

# Load Excel
df = pd.read_excel('source/data_produksi_AME_2023.xlsx')
print(f"\nLoaded: {len(df)} rows")

# Remove header row if present (first row is NaN)
if df.iloc[0]['DIVISI'] is pd.NA or pd.isna(df.iloc[0]['DIVISI']):
    print("Removing header row...")
    df = df.iloc[1:].reset_index(drop=True)

# Convert to proper types
df['Realisasi'] = pd.to_numeric(df['Realisasi'], errors='coerce')
df['Potensi'] = pd.to_numeric(df['Potensi'], errors='coerce')

# Remove any remaining NaN rows
df = df.dropna(subset=['BLOCK', 'Realisasi', 'Potensi'])

print(f"After cleaning: {len(df)} rows")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nSample data:")
print(df[['DIVISI', 'BLOCK', 'Realisasi', 'Potensi']].head(10))

# Calculate totals
total_real = df['Realisasi'].sum()
total_potensi = df['Potensi'].sum()

print(f"\n{'='*80}")
print("TOTALS FROM EXCEL")
print(f"{'='*80}")
print(f"Total Realisasi: {total_real:,.2f} Ton")
print(f"Total Potensi: {total_potensi:,.2f} Ton")
print(f"Gap: {total_real - total_potensi:,.2f} Ton")

# Load blocks table to get block IDs
print(f"\n{'='*80}")
print("LOADING DATABASE BLOCKS")
print(f"{'='*80}")

blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

print(f"Blocks in database: {len(df_blocks)}")

# Map block codes to IDs
block_map = dict(zip(df_blocks['block_code'], df_blocks['id']))

# Add block_id to dataframe
df['block_id'] = df['BLOCK'].map(block_map)

# Check for missing blocks
missing_blocks = df[df['block_id'].isna()]['BLOCK'].unique()
if len(missing_blocks) > 0:
    print(f"\n⚠️  WARNING: {len(missing_blocks)} blocks not found in database:")
    for block in missing_blocks[:10]:
        print(f"  - {block}")
    
    # Remove rows with missing block IDs
    df = df.dropna(subset=['block_id'])
    print(f"\nAfter removing missing blocks: {len(df)} rows")

# Load current production data for AME 2023
print(f"\n{'='*80}")
print("LOADING CURRENT DATABASE (AME 2023)")
print(f"{'='*80}")

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

df_db = pd.DataFrame(all_prod)

# Filter for AME blocks 2023
df_db_ame = df_db[df_db['year'] == 2023]
df_db_ame = df_db_ame.merge(df_blocks[['id', 'block_code']], 
                             left_on='block_id', right_on='id',suffixes=('', '_block'), 
                             how='left')
df_db_ame['estate_code'] = df_db_ame['block_code'].str[0]

# Map to estate
estate_map = {'A': 'AME', 'B': 'AME', 'C': 'AME', 'E': 'AME', 'F': 'AME'}
df_db_ame['estate'] = df_db_ame['estate_code'].map(estate_map)
df_db_ame = df_db_ame[df_db_ame['estate'] == 'AME']

print(f"Current AME 2023 records in DB: {len(df_db_ame)}")
print(f"Current AME 2023 Realisasi: {df_db_ame['real_ton'].sum():,.2f} Ton")
print(f"Current AME 2023 Potensi: {df_db_ame['potensi_ton'].sum():,.2f} Ton")

# Generate SQL statements
print(f"\n{'='*80}")
print("GENERATING SQL STATEMENTS")
print(f"{'='*80}")

sql_statements = []
update_count = 0
insert_count = 0

for _, row in df.iterrows():
    block_id = int(row['block_id'])
    block_code = row['BLOCK']
    real_ton = row['Realisasi']
    potensi_ton = row['Potensi']
    year = 2023
    
    # Check if exists
    existing = df_db_ame[df_db_ame['block_id'] == block_id]
    
    if len(existing) > 0:
        # UPDATE
        rec_id = existing.iloc[0]['id']
        sql = f"UPDATE production_annual SET real_ton = {real_ton}, potensi_ton = {potensi_ton} WHERE id = {rec_id}; -- {block_code}"
        sql_statements.append(sql)
        update_count += 1
    else:
        # INSERT
        sql = f"INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES ({block_id}, {year}, {real_ton}, {potensi_ton}); -- {block_code}"
        sql_statements.append(sql)
        insert_count += 1

print(f"\nGenerated {len(sql_statements)} SQL statements:")
print(f"  UPDATE: {update_count}")
print(f"  INSERT: {insert_count}")

# Save to file
output_file = 'fix_AME_2023.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("-- FIX AME 2023 PRODUCTION DATA\n")
    f.write(f"-- Generated from: source/data_produksi_AME_2023.xlsx\n")
    f.write(f"-- Total statements: {len(sql_statements)}\n")
    f.write(f"-- UPDATE: {update_count} | INSERT: {insert_count}\n\n")
    
    f.write("-- TARGET TOTALS:\n")
    f.write(f"-- Realisasi: {total_real:,.2f} Ton\n")
    f.write(f"-- Potensi: {total_potensi:,.2f} Ton\n\n")
    
    f.write("-- BACKUP FIRST (RECOMMENDED):\n")
    f.write("-- CREATE TABLE production_annual_backup AS SELECT * FROM production_annual;\n\n")
    
    for sql in sql_statements:
        f.write(sql + "\n")
    
    f.write("\n-- VERIFICATION QUERY:\n")
    f.write("-- Check AME 2023 totals after running:\n")
    f.write("""
SELECT 
    b.block_code,
    p.year,
    p.real_ton,
    p.potensi_ton
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND (b.block_code LIKE 'A%' OR b.block_code LIKE 'B%' OR 
       b.block_code LIKE 'C%' OR b.block_code LIKE 'E%' OR b.block_code LIKE 'F%')
ORDER BY b.block_code;

-- Summary:
SELECT 
    SUM(p.real_ton) as total_realisasi,
    SUM(p.potensi_ton) as total_potensi
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND (b.block_code LIKE 'A%' OR b.block_code LIKE 'B%' OR 
       b.block_code LIKE 'C%' OR b.block_code LIKE 'E%' OR b.block_code LIKE 'F%');
""")

print(f"\n✓ Saved to: {output_file}")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"Excel rows processed: {len(df)}")
print(f"SQL statements: {len(sql_statements)} (UPDATE: {update_count}, INSERT: {insert_count})")
print(f"Target Realisasi: {total_real:,.2f} Ton")
print(f"Target Potensi: {total_potensi:,.2f} Ton")

print(f"\n{'='*80}")
print("NEXT STEPS")
print(f"{'='*80}")
print("""
1. Review 'fix_AME_2023.sql'
2. Backup database (recommended):
   CREATE TABLE production_annual_backup AS SELECT * FROM production_annual;
3. Execute the SQL file in Supabase
4. Run verification query to confirm totals
5. Boss provides 2024 & 2025 data for AME
""")

print("\nDONE")
