"""
ESTATE-BY-ESTATE DATABASE FIX
Process Excel files from Boss (one per estate) and generate SQL fix statements
"""

import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

def process_estate_file(estate_code, file_path):
    """
    Process a single estate Excel file and generate UPDATE/INSERT statements
    
    Expected Excel structure:
    - block_code (or block_id)
    - year (2023, 2024, 2025)
    - real_ton (realisasi)
    - potensi_ton (target)
    """
    
    print(f"\n{'='*80}")
    print(f"PROCESSING ESTATE: {estate_code}")
    print(f"File: {file_path}")
    print(f"{'='*80}")
    
    # Load Excel
    try:
        if file_path.endswith('.csv'):
            df_excel = pd.read_csv(file_path)
        else:
            df_excel = pd.read_excel(file_path)
        
        print(f"\nLoaded: {len(df_excel)} rows")
        print(f"Columns: {df_excel.columns.tolist()}")
        
    except Exception as e:
        print(f"ERROR loading file: {e}")
        return None
    
    # Auto-detect column names (flexible naming)
    col_map = {}
    
    for col in df_excel.columns:
        col_lower = str(col).lower()
        
        if 'block' in col_lower and 'code' in col_lower:
            col_map['block_code'] = col
        elif 'block' in col_lower and 'id' in col_lower:
            col_map['block_id'] = col
        elif 'year' in col_lower or 'tahun' in col_lower:
            col_map['year'] = col
        elif 'real' in col_lower or 'realisasi' in col_lower or 'aktual' in col_lower:
            col_map['real_ton'] = col
        elif 'potensi' in col_lower or 'target' in col_lower or 'potential' in col_lower:
            col_map['potensi_ton'] = col
    
    print(f"\nColumn mapping detected:")
    for key, val in col_map.items():
        print(f"  {key}: '{val}'")
    
    # Validate required columns
    required = ['year', 'real_ton', 'potensi_ton']
    if not all(k in col_map for k in required):
        print(f"\nERROR: Missing required columns")
        print(f"Required: {required}")
        print(f"Found: {list(col_map.keys())}")
        return None
    
    # Load current database for this estate
    print(f"\nLoading current database records for {estate_code}...")
    all_data = []
    page = 0
    while True:
        start = page * 1000
        end = start + 999
        response = supabase.table('production_annual').select('*').range(start, end).execute()
        if not response.data:
            break
        all_data.extend(response.data)
        if len(response.data) < 1000:
            break
        page += 1
    
    df_db = pd.DataFrame(all_data)
    
    # Load blocks table to get block_id from block_code
    blocks_data = supabase.table('blocks').select('*').execute()
    df_blocks = pd.DataFrame(blocks_data.data)
    
    # Filter for this estate
    df_db_estate = df_db.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', how='left')
    df_db_estate['estate_code'] = df_db_estate['block_code'].str[0]
    
    # Map estate codes
    estate_map = {'A': 'AME', 'O': 'OLE', 'D': 'DBE', 'B': 'AME', 
                  'E': 'AME', 'F': 'AME', 'K': 'OLE', 'L': 'OLE', 
                  'M': 'DBE', 'N': 'DBE'}
    df_db_estate['estate'] = df_db_estate['estate_code'].map(estate_map)
    df_db_estate = df_db_estate[df_db_estate['estate'] == estate_code]
    
    print(f"Database records for {estate_code}: {len(df_db_estate)}")
    
    # Check current totals
    print(f"\nCurrent database totals for {estate_code}:")
    for year in [2023, 2024, 2025]:
        dy = df_db_estate[df_db_estate['year'] == year]
        actual = dy['real_ton'].sum()
        target = dy['potensi_ton'].sum()
        print(f"  {year}: Actual={actual:,.2f}, Target={target:,.2f}")
    
    # Check Excel totals
    print(f"\nExcel file totals for {estate_code}:")
    for year in [2023, 2024, 2025]:
        dy = df_excel[df_excel[col_map['year']] == year]
        if len(dy) > 0:
            actual = dy[col_map['real_ton']].sum()
            target = dy[col_map['potensi_ton']].sum()
            print(f"  {year}: Actual={actual:,.2f}, Target={target:,.2f}")
    
    # Generate SQL statements
    sql_statements = []
    
    print(f"\nGenerating SQL statements...")
    
    for _, row in df_excel.iterrows():
        year = row[col_map['year']]
        real_ton = row[col_map['real_ton']]
        potensi_ton = row[col_map['potensi_ton']]
        
        # Get block_id
        if 'block_code' in col_map:
            block_code = row[col_map['block_code']]
            # Find block_id from blocks table
            block_row = df_blocks[df_blocks['block_code'] == block_code]
            if len(block_row) == 0:
                print(f"  WARNING: Block code '{block_code}' not found in blocks table")
                continue
            block_id = block_row.iloc[0]['id']
        else:
            block_id = row[col_map['block_id']]
        
        # Check if record exists in database
        existing = df_db_estate[(df_db_estate['block_id'] == block_id) & 
                                (df_db_estate['year'] == year)]
        
        if len(existing) > 0:
            # UPDATE
            rec_id = existing.iloc[0]['id']
            sql = f"UPDATE production_annual SET real_ton = {real_ton}, potensi_ton = {potensi_ton} WHERE id = {rec_id};"
            sql_statements.append(sql)
        else:
            # INSERT
            sql = f"INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES ({block_id}, {year}, {real_ton}, {potensi_ton});"
            sql_statements.append(sql)
    
    print(f"Generated {len(sql_statements)} SQL statements")
    
    return {
        'estate': estate_code,
        'sql_statements': sql_statements,
        'excel_rows': len(df_excel),
        'sql_count': len(sql_statements)
    }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

print("="*80)
print("ESTATE-BY-ESTATE DATABASE FIX")
print("="*80)

print("""
INSTRUCTIONS:

Boss will provide 3 Excel files (one per estate):

1. TAHAP 1 - AME Estate:
   Upload to: source/estate_fix/AME_production.xlsx (or .csv)
   
2. TAHAP 2 - OLE Estate:
   Upload to: source/estate_fix/OLE_production.xlsx (or .csv)
   
3. TAHAP 3 - DBE Estate:
   Upload to: source/estate_fix/DBE_production.xlsx (or .csv)

Expected columns in each file:
  - block_code (or block_id)
  - year (2023, 2024, 2025)
  - real_ton (realisasi)
  - potensi_ton (target)

After ALL 3 files are ready, run this script to generate SQL fix statements.
""")

# Check which files are ready
estates = {
    'AME': ['source/estate_fix/AME_production.xlsx', 'source/estate_fix/AME_production.csv'],
    'OLE': ['source/estate_fix/OLE_production.xlsx', 'source/estate_fix/OLE_production.csv'],
    'DBE': ['source/estate_fix/DBE_production.xlsx', 'source/estate_fix/DBE_production.csv']
}

ready_estates = {}

print("\nChecking for files...")
for estate, paths in estates.items():
    for path in paths:
        if os.path.exists(path):
            ready_estates[estate] = path
            print(f"  ✓ {estate}: {path}")
            break
    else:
        print(f"  ✗ {estate}: Not uploaded yet")

if len(ready_estates) == 0:
    print("\n⏳ Waiting for Boss to upload files...")
    print("\nFolder ready at: source/estate_fix/")
    exit(0)

# Process available estates
print(f"\n{'='*80}")
print(f"PROCESSING {len(ready_estates)} ESTATES")
print(f"{'='*80}")

all_sql = []
results = []

for estate, file_path in ready_estates.items():
    result = process_estate_file(estate, file_path)
    if result:
        results.append(result)
        all_sql.extend(result['sql_statements'])

# Save combined SQL
if len(all_sql) > 0:
    output_file = 'fix_production_complete.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- DATABASE FIX - Estate by Estate\n")
        f.write(f"-- Generated: {pd.Timestamp.now()}\n")
        f.write(f"-- Total statements: {len(all_sql)}\n\n")
        
        f.write("-- BACKUP FIRST (IMPORTANT!):\n")
        f.write("-- CREATE TABLE production_annual_backup AS SELECT * FROM production_annual;\n\n")
        
        for estate, file_path in ready_estates.items():
            f.write(f"\n-- {estate} Estate\n")
            estate_sql = [r['sql_statements'] for r in results if r['estate'] == estate]
            if estate_sql:
                for sql in estate_sql[0]:
                    f.write(sql + "\n")
        
        f.write("\n-- VERIFICATION QUERY:\n")
        f.write("SELECT year, COUNT(*) as records, SUM(real_ton) as actual, SUM(potensi_ton) as target\n")
        f.write("FROM production_annual\n")
        f.write("GROUP BY year\n")
        f.write("ORDER BY year;\n")
    
    print(f"\n{'='*80}")
    print(f"SQL GENERATED!")
    print(f"{'='*80}")
    print(f"  File: {output_file}")
    print(f"  Total statements: {len(all_sql)}")
    
    for result in results:
        print(f"\n  {result['estate']}:")
        print(f"    Excel rows: {result['excel_rows']}")
        print(f"    SQL statements: {result['sql_count']}")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review 'fix_production_complete.sql'")
    print("2. Backup: CREATE TABLE production_annual_backup AS SELECT * FROM production_annual;")
    print("3. Execute the SQL file in Supabase")
    print("4. Verify totals match Boss's Excel")
    print("="*80)

else:
    print("\n⚠️  No SQL statements generated. Check file formats.")

print("\nDONE")
