"""
DIRECT DATABASE FIX - Update NULL/ZERO records
Since we know the missing amounts, we'll fix the problematic records directly
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("DATABASE FIX - Finding and Exporting Problematic Records")
print("="*80)

# Load all data
print("\nLoading database...")
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

df = pd.DataFrame(all_data)
print(f"Total records: {len(df)}")

# Find problematic records
print("\nFinding problematic records...")
df_problems = df[
    (df['real_ton'].isna()) | 
    (df['potensi_ton'].isna()) |
    (df['real_ton'] == 0) | 
    (df['potensi_ton'] == 0) |
    (df['real_ton'] < 0.01) |
    (df['potensi_ton'] < 0.01)
].copy()

print(f"Found {len(df_problems)} problematic records")

# Summary
print("\nBreakdown:")
print(f"  NULL real_ton: {df['real_ton'].isna().sum()}")
print(f"  NULL potensi_ton: {df['potensi_ton'].isna().sum()}")
print(f"  ZERO real_ton: {(df['real_ton'] == 0).sum()}")
print(f"  ZERO potensi_ton: {(df['potensi_ton'] == 0).sum()}")

# Export problematic records
if len(df_problems) > 0:
    # Create output directory if not exists
    os.makedirs('output', exist_ok=True)
    
    # Export to CSV
    csv_path = 'output/problematic_production_records.csv'
    df_problems.to_csv(csv_path, index=False)
    print(f"\n✓ Exported to: {csv_path}")
    
    # Show sample
    print("\nSample problematic records:")
    print(df_problems[['id', 'block_id', 'year', 'real_ton', 'potensi_ton']].head(10))
    
    # By year
    print("\nBy year:")
    for year in [2023, 2024, 2025]:
        count = len(df_problems[df_problems['year'] == year])
        print(f"  {year}: {count} records")

# Check if we can load Excel to get correct values
print("\n" + "="*80)
print("ATTEMPTING TO LOAD EXCEL SOURCE FOR CORRECT VALUES")
print("="*80)

excel_files = [
    ('output/realisasi_cleaned.xlsx', 'Cleaned'),
    ('output/normalized_realisasi_potensi.csv', 'Normalized CSV'),
    ('source/Realisasi vs Potensi PT SR.xlsx', 'Original')
]

for file_path, desc in excel_files:
    if os.path.exists(file_path):
        print(f"\nTrying {desc}: {file_path}")
        try:
            if file_path.endswith('.csv'):
                df_excel = pd.read_csv(file_path)
            else:
                df_excel = pd.read_excel(file_path)
            
            print(f"  Loaded: {len(df_excel)} rows")
            print(f"  Columns ({len(df_excel.columns)}): {df_excel.columns.tolist()[:15]}")
            
            # Check totals if we can identify year column
            year_cols = [c for c in df_excel.columns if 'year' in str(c).lower() or 'tahun' in str(c).lower()]
            
            if len(year_cols) > 0:
                print(f"\n  Found year column: {year_cols[0]}")
                
                # Try to identify production columns
                real_cols = [c for c in df_excel.columns if 'real' in str(c).lower()]
                target_cols = [c for c in df_excel.columns if 'potensi' in str(c).lower() or 'target' in str(c).lower()]
                
                if len(real_cols) > 0 and len(target_cols) > 0:
                    print(f"  Real column: {real_cols[0]}")
                    print(f"  Target column: {target_cols[0]}")
                    
                    print("\n  Excel totals:")
                    for year in [2023, 2024, 2025]:
                        dy = df_excel[df_excel[year_cols[0]] == year]
                        if len(dy) > 0:
                            actual = dy[real_cols[0]].sum()
                            target = dy[target_cols[0]].sum()
                            print(f"    {year}: actual={actual:,.2f}, target={target:,.2f}")
                    
                    print(f"\n  ✓ This file has production data!")
                    print(f"  Can be used to fix database records")
                    break
        except Exception as e:
            print(f"  Error: {e}")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)
print("""
1. Review 'output/problematic_production_records.csv'
2. These records have NULL or ZERO values
3. Options:
   a) Find correct values from Excel and UPDATE
   b) DELETE these records and re-INSERT from Excel
   c) Full table re-upload from clean Excel source

Recommended: Option (b) - Delete problematic rows, re-insert from Excel
""")

print("\nDONE")
