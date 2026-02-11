"""
Generate INSERT SQL statements from Excel source
to replace the 250 deleted problematic records
"""

import pandas as pd
import os

print("GENERATING INSERT STATEMENTS FROM EXCEL SOURCE")
print("="*80)

# Load problematic records list
df_problems = pd.read_csv('output/problematic_production_records.csv')
print(f"\nProblematic records to fix: {len(df_problems)}")

# Create a set of (block_id, year) tuples that need to be fixed
missing_keys = set()
for _, row in df_problems.iterrows():
    missing_keys.add((row['block_id'], row['year']))

print(f"Unique (block_id, year) combinations: {len(missing_keys)}")

# Try to load Excel source
excel_sources = [
    'output/normalized_realisasi_potensi.csv',
    'output/realisasi_cleaned.csv',
    'output/data_cleaned_latest.csv'
]

df_source = None

for source in excel_sources:
    if os.path.exists(source):
        print(f"\nTrying: {source}")
        try:
            df_source = pd.read_csv(source)
            print(f"  Loaded: {len(df_source)} rows")
            print(f"  Columns: {list(df_source.columns)[:15]}")
            
            # Check if it has required columns
            has_block = any('block' in str(c).lower() for c in df_source.columns)
            has_year = any('year' in str(c).lower() or 'tahun' in str(c).lower() for c in df_source.columns)
            has_prod = any('real' in str(c).lower() or 'potensi' in str(c).lower() for c in df_source.columns)
            
            if has_block and has_year and has_prod:
                print(f"  ✓ Has required columns!")
                break
            else:
                print(f"  Missing required columns")
                df_source = None
        except Exception as e:
            print(f"  Error: {e}")
            df_source = None

if df_source is None:
    print("\n❌ ERROR: Could not load Excel source with production data")
    print("\nPlease ensure one of these files exists with correct structure:")
    for src in excel_sources:
        print(f"  - {src}")
    exit(1)

print("\n" + "="*80)
print("MAPPING COLUMNS")
print("="*80)

# Identify column mappings
block_col = [c for c in df_source.columns if 'block_id' in str(c).lower()]
if not block_col:
    block_col = [c for c in df_source.columns if 'block' in str(c).lower() and 'code' not in str(c).lower()]

year_col = [c for c in df_source.columns if 'year' in str(c).lower() or 'tahun' in str(c).lower()]
real_col = [c for c in df_source.columns if 'real_ton' in str(c).lower() or 'realisasi' in str(c).lower()]
target_col = [c for c in df_source.columns if 'potensi_ton' in str(c).lower() or 'potensi' in str(c).lower() or 'target' in str(c).lower()]

if not all([block_col, year_col, real_col, target_col]):
    print("\n❌ ERROR: Could not identify all required columns")
    print(f"Block column: {block_col}")
    print(f"Year column: {year_col}")
    print(f"Real column: {real_col}")
    print(f"Target column: {target_col}")
    exit(1)

block_col = block_col[0]
year_col = year_col[0]
real_col = real_col[0]
target_col = target_col[0]

print(f"\nColumn mapping:")
print(f"  block_id: {block_col}")
print(f"  year: {year_col}")
print(f"  real_ton: {real_col}")
print(f"  potensi_ton: {target_col}")

# Generate INSERT statements
print("\n" + "="*80)
print("GENERATING INSERT STATEMENTS")
print("="*80)

inserts = []
matched = 0

for block_id, year in missing_keys:
    # Find row in source
    mask = (df_source[block_col] == block_id) & (df_source[year_col] == year)
    rows = df_source[mask]
    
    if len(rows) > 0:
        row = rows.iloc[0]
        real_val = row[real_col]
        target_val = row[target_col]
        
        # Skip if still NULL or ZERO
        if pd.notna(real_val) and pd.notna(target_val) and real_val > 0.01 and target_val > 0.01:
            sql = f"INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES ({block_id}, {year}, {real_val}, {target_val});"
            inserts.append(sql)
            matched += 1

print(f"\nGenerated {len(inserts)} INSERT statements")
print(f"Successfully matched: {matched}/{len(missing_keys)}")

if matched < len(missing_keys):
    print(f"\n⚠️  WARNING: Could not find data for {len(missing_keys) - matched} records")
    print("   These blocks may genuinely have no production data")

# Save to SQL file
output_file = 'fix_production_insert.sql'
with open(output_file, 'w') as f:
    f.write("-- INSERT statements to restore production data\n")
    f.write(f"-- Generated: {pd.Timestamp.now()}\n")
    f.write(f"-- Total statements: {len(inserts)}\n\n")
    
    for sql in inserts:
        f.write(sql + "\n")
    
    f.write(f"\n-- Total rows to insert: {len(inserts)}\n")
    
    # Add verification query
    f.write("\n-- VERIFY after running:\n")
    f.write("SELECT year, COUNT(*) as records, SUM(real_ton) as actual, SUM(potensi_ton) as target\n")
    f.write("FROM production_annual\n")
    f.write("GROUP BY year\n")
    f.write("ORDER BY year;\n")

print(f"\n✓ Saved to: {output_file}")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)
print("""
1. Review 'fix_production_insert.sql'
2. Execute in this order:
   a) Backup: CREATE TABLE production_annual_backup AS SELECT * FROM production_annual;
   b) Delete: Run 'fix_production_delete.sql'
   c) Insert: Run 'fix_production_insert.sql'
   d) Verify: Check totals match Boss's Excel
   
Target totals:
  2023: 141,630.61 Ton (actual) | 187,781.70 Ton (target)
  2024: 136,553.30 Ton (actual) | 190,482.30 Ton (target)
  2025: 143,382.80 Ton (actual) | 191,449.80 Ton (target)
""")

print("\nDONE")
