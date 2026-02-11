import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("ANALYZING NULL AND ZERO VALUES IN DATABASE")
print("="*80)

# Load all production data
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

# Identify problem records
df_null = df[df['real_ton'].isna() | df['potensi_ton'].isna()]
df_zero = df[(df['real_ton'] == 0) | (df['potensi_ton'] == 0)]

print(f"\nTotal records: {len(df)}")
print(f"NULL records: {len(df_null)}")
print(f"ZERO records: {len(df_zero)}")

# Show NULL records
if len(df_null) > 0:
    print("\n" + "="*80)
    print("NULL VALUE RECORDS:")
    print("="*80)
    print(df_null[['id', 'block_id', 'year', 'real_ton', 'potensi_ton']].head(20))
    
    # Count by year
    print("\nNULL records by year:")
    for year in [2023, 2024, 2025]:
        count = len(df_null[df_null['year'] == year])
        print(f"  {year}: {count} records")

# Show ZERO records
if len(df_zero) > 0:
    print("\n" + "="*80)
    print("ZERO VALUE RECORDS:")
    print("="*80)
    print(df_zero[['id', 'block_id', 'year', 'real_ton', 'potensi_ton']].head(20))
    
    # Count by year
    print("\nZERO records by year:")
    for year in [2023, 2024, 2025]:
        count = len(df_zero[df_zero['year'] == year])
        print(f"  {year}: {count} records")

# Calculate impact on totals
print("\n" + "="*80)
print("IMPACT ANALYSIS")
print("="*80)

for year in [2023, 2024, 2025]:
    df_year = df[df['year'] == year]
    df_year_valid = df_year[(df_year['real_ton'].notna()) & (df_year['potensi_ton'].notna()) & 
                            (df_year['real_ton'] > 0) & (df_year['potensi_ton'] > 0)]
    
    total_all = df_year['real_ton'].sum()
    total_valid = df_year_valid['real_ton'].sum()
    
    print(f"\n{year}:")
    print(f"  All records: {len(df_year)}")
    print(f"  Valid records: {len(df_year_valid)}")
    print(f"  Invalid: {len(df_year) - len(df_year_valid)}")
    print(f"  Total (all): {total_all:,.2f} Ton")
    print(f"  Total (valid only): {total_valid:,.2f} Ton")

# Get block IDs with issues
print("\n" + "="*80)
print("BLOCKS WITH NULL/ZERO VALUES (2023):")
print("="*80)

df_2023_issues = df[(df['year'] == 2023) & 
                     ((df['real_ton'].isna()) | (df['potensi_ton'].isna()) | 
                      (df['real_ton'] == 0) | (df['potensi_ton'] == 0))]

if len(df_2023_issues) > 0:
    print(f"Found {len(df_2023_issues)} problematic records in 2023")
    print("\nBlock IDs with issues:")
    problem_blocks = df_2023_issues['block_id'].unique()
    print(f"  {len(problem_blocks)} unique blocks")
    print(f"  Block IDs: {sorted(problem_blocks)[:20]}...")  # Show first 20

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
print("""
There are 2 options:

1. FIX DATABASE:
   - Re-upload production data from Excel source
   - Or manually update the NULL/ZERO records
   
2. USE EXCEL AS SOURCE OF TRUTH:
   - Update dashboard calculations with Boss's manual numbers:
     2023: 141,984 Ton (actual), 188,208 Ton (target)
     2024: Need Boss to provide
     2025: Need Boss to provide
     
RECOMMENDED: Option 1 (Fix database for accuracy)
""")

print("DONE")
