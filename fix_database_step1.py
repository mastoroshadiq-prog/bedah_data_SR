"""
DATABASE FIX SCRIPT - Step 1: Identify Missing/Corrupted Records
Compare Excel source with database to find exact discrepancies
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("STEP 1: IDENTIFYING MISSING/CORRUPTED RECORDS")
print("="*80)

# Target values from Boss's Excel
EXCEL_TOTALS = {
    2023: {'actual': 141630.61, 'target': 187781.70},
    2024: {'actual': 136553.30, 'target': 190482.30},
    2025: {'actual': 143382.80, 'target': 191449.80}
}

# Step 1: Load current database
print("\n1. Loading current database...")
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
print(f"   Database records: {len(df_db)}")

# Step 2: Current DB totals
print("\n2. Current database totals:")
for year in [2023, 2024, 2025]:
    dy = df_db[df_db['year'] == year]
    actual = dy['real_ton'].sum()
    target = dy['potensi_ton'].sum()
    
    expected_actual = EXCEL_TOTALS[year]['actual']
    expected_target = EXCEL_TOTALS[year]['target']
    
    diff_actual = expected_actual - actual
    diff_target = expected_target - target
    
    print(f"\n   {year}:")
    print(f"      DB Actual: {actual:,.2f} | Expected: {expected_actual:,.2f} | Missing: {diff_actual:,.2f}")
    print(f"      DB Target: {target:,.2f} | Expected: {expected_target:,.2f} | Missing: {diff_target:,.2f}")

# Step 3: Load Excel source files
print("\n3. Checking Excel source files...")

excel_files = [
    'source/data_gabungan.xlsx',
    'source/Realisasi vs Potensi PT SR.xlsx',
    'output/realisasi_cleaned.xlsx'
]

df_excel = None

for file_path in excel_files:
    if os.path.exists(file_path):
        print(f"\n   Trying: {file_path}")
        try:
            df_temp = pd.read_excel(file_path)
            print(f"      Loaded: {len(df_temp)} rows, {len(df_temp.columns)} columns")
            print(f"      Columns: {df_temp.columns.tolist()[:10]}...")
            
            # Check if this looks like production data
            if any('real' in str(col).lower() or 'potensi' in str(col).lower() for col in df_temp.columns):
                df_excel = df_temp
                print(f"      ✓ This looks like production data!")
                break
        except Exception as e:
            print(f"      Error: {e}")

if df_excel is None:
    print("\n   ⚠️  Could not load Excel source file with production data")
    print("   We'll identify problematic records in database instead...")
    
    # Alternative approach: Find NULL/ZERO records
    print("\n4. Identifying problematic records in database:")
    
    # Find records with NULL or ZERO values
    df_problems = df_db[
        (df_db['real_ton'].isna()) | 
        (df_db['potensi_ton'].isna()) |
        (df_db['real_ton'] == 0) | 
        (df_db['potensi_ton'] == 0) |
        (df_db['real_ton'] < 0.01) |
        (df_db['potensi_ton'] < 0.01)
    ]
    
    print(f"\n   Found {len(df_problems)} problematic records:")
    print(f"      NULL real_ton: {df_db['real_ton'].isna().sum()}")
    print(f"      NULL potensi_ton: {df_db['potensi_ton'].isna().sum()}")
    print(f"      ZERO real_ton: {(df_db['real_ton'] == 0).sum()}")
    print(f"      ZERO potensi_ton: {(df_db['potensi_ton'] == 0).sum()}")
    print(f"      Very small (< 0.01): {((df_db['real_ton'] < 0.01) | (df_db['potensi_ton'] < 0.01)).sum()}")
    
    # Show details
    if len(df_problems) > 0:
        print("\n   Sample problematic records:")
        print(df_problems[['id', 'block_id', 'year', 'real_ton', 'potensi_ton']].head(20).to_string())
        
        # Export to CSV for manual review
        df_problems.to_csv('output/problematic_records.csv', index=False)
        print(f"\n   ✓ Exported all problematic records to: output/problematic_records.csv")
        
        # Summary by year
        print("\n   Problematic records by year:")
        for year in [2023, 2024, 2025]:
            count = len(df_problems[df_problems['year'] == year])
            print(f"      {year}: {count} records")

else:
    print("\n4. Excel file loaded successfully!")
    print("   Will proceed with Excel-to-DB comparison...")
    # This will be implemented in next step

print("\n" + "="*80)
print("STEP 2: GENERATING FIX STRATEGY")
print("="*80)

print("""
Based on the analysis, we have 2 approaches to fix:

APPROACH 1: Fix NULL/ZERO records
   - We identified records with NULL/ZERO values
   - Need to find correct values from Excel for these specific records
   
APPROACH 2: Re-upload entire production table
   - Clean truncate and re-upload from Excel
   - Safest but more invasive

RECOMMENDATION: 
   First try APPROACH 1 (fix specific records)
   If that doesn't fully resolve, use APPROACH 2

Next steps:
1. Review 'output/problematic_records.csv'
2. Match these records with Excel source
3. Generate UPDATE SQL statements
4. Execute and verify
""")

print("\n" + "="*80)
print("DONE - Check output/problematic_records.csv for details")
print("="*80)
