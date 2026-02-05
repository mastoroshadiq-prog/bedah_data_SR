"""
PHASE 3 FINAL: EXTRACT ANNUAL PRODUCTION 2023-2025
===================================================
Purpose: Extract annual production data from data_gabungan.xlsx
         Columns EU-FU (Excel columns 125-151)

Input:
- source/data_gabungan.xlsx
- output/normalized_tables/phase1_core/blocks_standardized.csv

Output:
- output/normalized_tables/phase3_production/production_annual.csv
- Updated report
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("PHASE 3 FINAL: EXTRACT ANNUAL PRODUCTION 2023-2025")
print("=" * 100)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create output directory
os.makedirs('output/normalized_tables/phase3_production', exist_ok=True)

# ============================================================================
# STEP 1: Load blocks
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1: Loading blocks")
print("=" * 100)

df_blocks = pd.read_csv('output/normalized_tables/phase1_core/blocks_standardized.csv')
print(f"✅ Loaded {len(df_blocks)} blocks")

# ============================================================================
# STEP 2: Load data_gabungan.xlsx with proper header
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: Loading data_gabungan.xlsx")
print("=" * 100)

# Find data start row
df_raw = pd.read_excel('source/data_gabungan.xlsx', sheet_name='Lembar1', header=None, nrows=20)

print("Finding data start row...")
data_start_row = None
for i in range(20):
    # Look for first numeric ID in column 0
    val = df_raw.iloc[i, 0]
    if pd.notna(val):
        try:
            if int(val) == 1:
                data_start_row = i
                print(f"✅ Data starts at row {data_start_row}")
                break
        except:
            pass

if data_start_row is None:
    print("❌ Could not find data start row!")
    # Try default
    data_start_row = 9
    print(f"⚠️  Using default row {data_start_row}")

# Load full data
df_full = pd.read_excel('source/data_gabungan.xlsx', 
                        sheet_name='Lembar1',
                        skiprows=data_start_row)

print(f"✅ Loaded data: {df_full.shape}")
print(f"   Total columns: {len(df_full.columns)}")

# ============================================================================
# STEP 3: Extract production columns by Excel column positions
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: Extracting production columns EU-FU")
print("=" * 100)

# Excel column letters to indices (0-indexed)
# EU = column 125 (0-indexed: 124)
# FC = column 133 (0-indexed: 132)
# FD = column 134 (0-indexed: 133)
# FL = column 142 (0-indexed: 141)
# FM = column 143 (0-indexed: 142)
# FU = column 151 (0-indexed: 150)

def excel_col_to_index(col_letter):
    """Convert Excel column letter to 0-indexed column number"""
    result = 0
    for i, char in enumerate(reversed(col_letter.upper())):
        result += (ord(char) - ord('A') + 1) * (26 ** i)
    return result - 1

# Calculate column indices
col_2023_start = excel_col_to_index('EU')  # 124
col_2023_end = excel_col_to_index('FC')    # 132
col_2024_start = excel_col_to_index('FD')  # 133
col_2024_end = excel_col_to_index('FL')    # 141
col_2025_start = excel_col_to_index('FM')  # 142
col_2025_end = excel_col_to_index('FU')    # 150

print(f"\nColumn indices:")
print(f"  2023: {col_2023_start}-{col_2023_end} (EU-FC)")
print(f"  2024: {col_2024_start}-{col_2024_end} (FD-FL)")
print(f"  2025: {col_2025_start}-{col_2025_end} (FM-FU)")

# Check if we have enough columns
if len(df_full.columns) <= col_2025_end:
    print(f"⚠️  Warning: File only has {len(df_full.columns)} columns")
    print(f"   Need at least {col_2025_end + 1} columns")

# Find block code column (should be early in the file)
block_col = None
for col in df_full.columns[:20]:
    if df_full[col].dtype == 'object':
        # Check if values look like block codes (e.g., A001A, B005A)
        sample = df_full[col].dropna().astype(str).head(10)
        if any(len(str(v)) == 5 for v in sample):
            block_col = col
            print(f"\n✅ Found block column: '{col}'")
            print(f"   Sample values: {sample.tolist()[:5]}")
            break

if block_col is None:
    # Try column at index 1 or 2
    for idx in [1, 2, 3]:
        if idx < len(df_full.columns):
            col = df_full.columns[idx]
            print(f"⚠️  Trying column '{col}' at index {idx} as block column")
            block_col = col
            break

# ============================================================================
# STEP 4: Extract production data for each year
# ============================================================================
print("\n" + "=" * 100)
print("STEP 4: Extracting annual production data")
print("=" * 100)

production_annual_list = []

for year, start_col, end_col in [
    (2023, col_2023_start, col_2023_end),
    (2024, col_2024_start, col_2024_end),
    (2025, col_2025_start, col_2025_end)
]:
    print(f"\nProcessing year {year} (columns {start_col}-{end_col})...")
    
    # Check if columns exist
    if end_col >= len(df_full.columns):
        print(f"  ⚠️  Columns beyond file range, skipping {year}")
        continue
    
    # Extract columns for this year (9 columns)
    year_cols = df_full.iloc[:, start_col:end_col+1]
    
    print(f"  Extracted {len(year_cols.columns)} columns")
    print(f"  Column names: {list(year_cols.columns)}")
    
    # Create dataframe for this year
    df_year = pd.DataFrame()
    df_year['block_code'] = df_full[block_col]
    df_year['year'] = year
    
    # Assign columns based on expected structure:
    # 0-2: Real (BJR, JJg, Ton)
    # 3-5: Potensi (BJR, JJg, Ton)
    # 6-8: Gap (BJR, JJg, Ton)
    
    if len(year_cols.columns) >= 9:
        df_year['real_bjr_kg'] = year_cols.iloc[:, 0]
        df_year['real_jum_jjg'] = year_cols.iloc[:, 1]
        df_year['real_ton'] = year_cols.iloc[:, 2]
        df_year['potensi_bjr_kg'] = year_cols.iloc[:, 3]
        df_year['potensi_jum_jjg'] = year_cols.iloc[:, 4]
        df_year['potensi_ton'] = year_cols.iloc[:, 5]
        df_year['gap_bjr_kg'] = year_cols.iloc[:, 6]
        df_year['gap_jum_jjg'] = year_cols.iloc[:, 7]
        df_year['gap_ton'] = year_cols.iloc[:, 8]
        
        print(f"  ✅ Mapped all 9 metrics for {year}")
    else:
        print(f"  ⚠️  Only {len(year_cols.columns)} columns available")
    
    production_annual_list.append(df_year)

# Combine all years
df_production_annual = pd.concat(production_annual_list, ignore_index=True)
print(f"\n✅ Combined all years: {len(df_production_annual)} records")

# ============================================================================
# STEP 5: Match with blocks
# ============================================================================
print("\n" + "=" * 100)
print("STEP 5: Matching with blocks")
print("=" * 100)

# Merge with blocks
df_production_annual = df_production_annual.merge(
    df_blocks[['id', 'block_code']],
    on='block_code',
    how='inner'
)

df_production_annual = df_production_annual.rename(columns={'id': 'block_id'})

print(f"✅ Matched with blocks: {len(df_production_annual)} records")
print(f"   Unique blocks: {df_production_annual['block_id'].nunique()}")
print(f"   Years: {sorted(df_production_annual['year'].unique())}")

# ============================================================================
# STEP 6: Calculate gap percentages
# ============================================================================
print("\n" + "=" * 100)
print("STEP 6: Calculating gap percentages")
print("=" * 100)

# Convert to numeric
numeric_cols = ['real_bjr_kg', 'real_jum_jjg', 'real_ton', 
                'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton',
                'gap_bjr_kg', 'gap_jum_jjg', 'gap_ton']

for col in numeric_cols:
    if col in df_production_annual.columns:
        df_production_annual[col] = pd.to_numeric(df_production_annual[col], errors='coerce')

# Calculate gap percentages
df_production_annual['gap_pct_bjr'] = np.where(
    df_production_annual['potensi_bjr_kg'] != 0,
    (df_production_annual['gap_bjr_kg'] / df_production_annual['potensi_bjr_kg'] * 100).round(2),
    0
)
df_production_annual['gap_pct_jjg'] = np.where(
    df_production_annual['potensi_jum_jjg'] != 0,
    (df_production_annual['gap_jum_jjg'] / df_production_annual['potensi_jum_jjg'] * 100).round(2),
    0
)
df_production_annual['gap_pct_ton'] = np.where(
    df_production_annual['potensi_ton'] != 0,
    (df_production_annual['gap_ton'] / df_production_annual['potensi_ton'] * 100).round(2),
    0
)

# Replace inf with nan
df_production_annual = df_production_annual.replace([np.inf, -np.inf], np.nan)

print(f"✅ Calculated gap percentages")
print(f"\nGap statistics (Ton %):")
print(df_production_annual['gap_pct_ton'].describe())

# ============================================================================
# STEP 7: Finalize and save
# ============================================================================
print("\n" + "=" * 100)
print("STEP 7: Finalizing and saving")
print("=" * 100)

# Reorder columns
column_order = [
    'block_id', 'block_code', 'year',
    'real_bjr_kg', 'real_jum_jjg', 'real_ton',
    'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton',
    'gap_bjr_kg', 'gap_jum_jjg', 'gap_ton',
    'gap_pct_bjr', 'gap_pct_jjg', 'gap_pct_ton'
]

df_production_annual = df_production_annual[column_order]

# Add ID and timestamp
df_production_annual.insert(0, 'id', range(1, len(df_production_annual) + 1))
df_production_annual['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"✅ Finalized: {len(df_production_annual)} rows × {len(df_production_annual.columns)} columns")

# Save
output_file = 'output/normalized_tables/phase3_production/production_annual.csv'
df_production_annual.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")

# ============================================================================
# STEP 8: Generate summary
# ============================================================================
print("\n" + "=" * 100)
print("STEP 8: Summary")
print("=" * 100)

blocks_with_data = df_production_annual['block_id'].nunique()
records_per_year = df_production_annual.groupby('year').size()

print(f"\n📊 Production Annual Table:")
print(f"  Total records: {len(df_production_annual)}")
print(f"  Unique blocks: {blocks_with_data}")
print(f"  Years: {sorted(df_production_annual['year'].unique())}")
print(f"\n  Records per year:")
for year, count in records_per_year.items():
    print(f"    {year}: {count} blocks")

# Performance analysis
avg_gap_by_year = df_production_annual.groupby('year')['gap_pct_ton'].mean()
print(f"\n  Average gap % by year (Ton):")
for year, gap in avg_gap_by_year.items():
    print(f"    {year}: {gap:.2f}%")

# ============================================================================
# PHASE 3 FINAL COMPLETE
# ============================================================================
print("\n" + "=" * 100)
print("✅ PHASE 3 FINAL COMPLETE!")
print("=" * 100)
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📊 COMPLETE PRODUCTION DATA:")
print(f"  1. Annual (2023-2025): {len(df_production_annual)} records ⭐ NEW")
print(f"  2. Monthly (2023-2024): 11,034 records (existing)")
print(f"\n✅ Ready for Phase 4: Integration & SQL Schema!")
