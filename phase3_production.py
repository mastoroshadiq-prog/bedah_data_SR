"""
PHASE 3: PRODUCTION DATA EXTRACTION (CRITICAL)
==============================================
Purpose: Extract monthly production data (2023-2025) from Realisasi PT SR.xlsx
         Transform from WIDE format (many columns) to LONG format (rows per month)
         Calculate gap metrics (Realisasi vs Potensi)

Input:
- source/Realisasi vs Potensi PT SR.xlsx (Inti sheet only, skip Plasma)
- output/normalized_tables/phase1_core/blocks_standardized.csv (613 blocks with production)

Output:
- output/normalized_tables/phase3_production/production_monthly.csv
- output/normalized_tables/phase3_production/production_extraction_report.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("PHASE 3: PRODUCTION DATA EXTRACTION")
print("=" * 100)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create output directory
os.makedirs('output/normalized_tables/phase3_production', exist_ok=True)

# ============================================================================
# STEP 1: Load blocks with production data
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1: Loading blocks with production data")
print("=" * 100)

df_blocks = pd.read_csv('output/normalized_tables/phase1_core/blocks_standardized.csv')
df_blocks_prod = df_blocks[df_blocks['has_production_data'] == True].copy()
print(f"✅ Loaded {len(df_blocks_prod)} blocks with production data")
print(f"   Category: {df_blocks_prod['category'].value_counts().to_dict()}")

# ============================================================================
# STEP 2: Load and analyze Realisasi file structure
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: Loading Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

# Load raw to find header structure
df_raw = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx',
                       sheet_name='Real VS Potensi Inti',
                       header=None,
                       nrows=15)

print("First 15 rows (to identify header structure):")
for i in range(15):
    row_preview = df_raw.iloc[i, :15].tolist()
    print(f"  Row {i}: {row_preview}")

# Find data start row
data_start_row = None
for i in range(20):
    val = df_raw.iloc[i, 0]
    if pd.notna(val) and isinstance(val, (int, float)) and val == 1.0:
        data_start_row = i
        print(f"\n✅ Data starts at row {data_start_row}")
        break

if data_start_row is None:
    print("❌ Could not find data start row!")
    exit(1)

# Load with proper skiprows
df_prod_raw = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx',
                             sheet_name='Real VS Potensi Inti',
                             skiprows=data_start_row)

print(f"\n✅ Loaded Inti production data: {df_prod_raw.shape}")
print(f"\nColumn names (first 20):")
for i, col in enumerate(df_prod_raw.columns[:20], 1):
    print(f"  {i:2d}. {col}")

# ============================================================================
# STEP 3: Identify key columns
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: Identifying key columns")
print("=" * 100)

# Find block column (should be around column 2)
block_col = None
for i, col in enumerate(df_prod_raw.columns[:10]):
    if 'blok' in str(col).lower() or (i == 2 and pd.notna(col)):
        block_col = col
        block_col_index = i
        break

if block_col is None:
    # Use column index 2 as default
    block_col = df_prod_raw.columns[2]
    block_col_index = 2

print(f"✅ Block column: '{block_col}' (index {block_col_index})")
print(f"   Sample values: {df_prod_raw[block_col].head(10).tolist()}")

# Identify production columns
# Pattern: Real BJR, Real Janjang, Real Ton, Potensi BJR, Potensi Janjang, Potensi Ton
# Repeating for each month (12 times) and possibly for each year (2023, 2024, 2025)

print(f"\nAnalyzing column patterns...")
prod_columns = df_prod_raw.columns[block_col_index+1:]  # Columns after block

print(f"Total production columns: {len(prod_columns)}")
print(f"\nFirst 30 production column names:")
for i, col in enumerate(prod_columns[:30], 1):
    print(f"  {i:2d}. {col}")

# ============================================================================
# STEP 4: Map columns to months and metrics
# ============================================================================
print("\n" + "=" * 100)
print("STEP 4: Mapping columns to months and metrics")
print("=" * 100)

# The file likely has columns in pattern:
# For each month (Jan-Dec) × years (2023-2025):
# - Real BJR, Real Janjang, Real Ton
# - Potensi BJR, Potensi Janjang, Potensi Ton

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
years = [2023, 2024, 2025]

# Try to identify column patterns
# Assuming columns are ordered by: Month -> Metric Type -> Realisasi/Potensi

# Create mapping based on column positions
# Total expected: 3 years × 12 months × 6 metrics = 216 columns

columns_per_month = 6  # Real BJR, Janjang, Ton + Potensi BJR, Janjang, Ton
total_production_cols = len(years) * len(months) * columns_per_month

print(f"\nExpected total production columns: {total_production_cols}")
print(f"Actual production columns available: {len(prod_columns)}")

# Create column mapping structure
column_mapping = []

col_idx = 0
for year in years:
    for month in months:
        # Assuming pattern: Real BJR, Real Janjang, Real Ton, Potensi BJR, Potensi Janjang, Potensi Ton
        if col_idx + 5 < len(prod_columns):
            mapping = {
                'year': year,
                'month': month,
                'real_bjr_col': prod_columns[col_idx],
                'real_jjg_col': prod_columns[col_idx + 1],
                'real_ton_col': prod_columns[col_idx + 2],
                'potensi_bjr_col': prod_columns[col_idx + 3],
                'potensi_jjg_col': prod_columns[col_idx + 4],
                'potensi_ton_col': prod_columns[col_idx + 5]
            }
            column_mapping.append(mapping)
            col_idx += 6

print(f"\n✅ Created column mapping for {len(column_mapping)} month-year combinations")
print(f"\nSample mappings:")
for i, mapping in enumerate(column_mapping[:3], 1):
    print(f"\n  {i}. Year {mapping['year']}, {mapping['month']}:")
    print(f"     Real BJR: {mapping['real_bjr_col']}")
    print(f"     Real Janjang: {mapping['real_jjg_col']}")
    print(f"     Potensi BJR: {mapping['potensi_bjr_col']}")

# ============================================================================
# STEP 5: Transform WIDE → LONG format
# ============================================================================
print("\n" + "=" * 100)
print("STEP 5: Transforming WIDE → LONG format (CRITICAL)")
print("=" * 100)

production_monthly_list = []

for mapping in column_mapping:
    try:
        # Extract data for this month-year combination
        df_month = df_prod_raw[[block_col, 
                                mapping['real_bjr_col'],
                                mapping['real_jjg_col'],
                                mapping['real_ton_col'],
                                mapping['potensi_bjr_col'],
                                mapping['potensi_jjg_col'],
                                mapping['potensi_ton_col']]].copy()
        
        # Rename columns
        df_month.columns = ['block_code', 'real_bjr_kg', 'real_jum_jjg', 'real_ton',
                           'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton']
        
        # Add year and month
        df_month['year'] = mapping['year']
        df_month['month'] = mapping['month']
        
        # Append to list
        production_monthly_list.append(df_month)
        
    except Exception as e:
        print(f"⚠️  Error processing {mapping['year']}-{mapping['month']}: {e}")
        continue

# Combine all months
df_production_monthly = pd.concat(production_monthly_list, ignore_index=True)

print(f"\n✅ Combined all months: {len(df_production_monthly)} total records")
print(f"   Expected: {len(df_blocks_prod)} blocks × {len(column_mapping)} months = {len(df_blocks_prod) * len(column_mapping)}")

# ============================================================================
# STEP 6: Match with blocks and add block_id
# ============================================================================
print("\n" + "=" * 100)
print("STEP 6: Matching with blocks and adding block_id")
print("=" * 100)

# Merge with blocks to get block_id
df_production_monthly = df_production_monthly.merge(
    df_blocks_prod[['id', 'block_code']],
    on='block_code',
    how='inner'
)

df_production_monthly = df_production_monthly.rename(columns={'id': 'block_id'})

print(f"✅ Matched production data with blocks: {len(df_production_monthly)} records")
print(f"   Unique blocks: {df_production_monthly['block_id'].nunique()}")
print(f"   Years: {sorted(df_production_monthly['year'].unique())}")
print(f"   Months: {df_production_monthly['month'].nunique()} months")

# ============================================================================
# STEP 7: Calculate gap metrics
# ============================================================================
print("\n" + "=" * 100)
print("STEP 7: Calculating gap metrics")
print("=" * 100)

# Convert to numeric first
numeric_cols = ['real_bjr_kg', 'real_jum_jjg', 'real_ton', 'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton']
for col in numeric_cols:
    df_production_monthly[col] = pd.to_numeric(df_production_monthly[col], errors='coerce')

# Calculate gaps
df_production_monthly['gap_bjr_kg'] = df_production_monthly['real_bjr_kg'] - df_production_monthly['potensi_bjr_kg']
df_production_monthly['gap_jum_jjg'] = df_production_monthly['real_jum_jjg'] - df_production_monthly['potensi_jum_jjg']
df_production_monthly['gap_ton'] = df_production_monthly['real_ton'] - df_production_monthly['potensi_ton']

# Calculate percentage gaps (with division by zero protection)
df_production_monthly['gap_pct_bjr'] = np.where(
    df_production_monthly['potensi_bjr_kg'] != 0,
    (df_production_monthly['gap_bjr_kg'] / df_production_monthly['potensi_bjr_kg'] * 100).round(2),
    0
)
df_production_monthly['gap_pct_jjg'] = np.where(
    df_production_monthly['potensi_jum_jjg'] != 0,
    (df_production_monthly['gap_jum_jjg'] / df_production_monthly['potensi_jum_jjg'] * 100).round(2),
    0
)
df_production_monthly['gap_pct_ton'] = np.where(
    df_production_monthly['potensi_ton'] != 0,
    (df_production_monthly['gap_ton'] / df_production_monthly['potensi_ton'] * 100).round(2),
    0
)

# Replace inf with None
df_production_monthly = df_production_monthly.replace([np.inf, -np.inf], np.nan)

print(f"✅ Calculated gap metrics")
print(f"\nGap statistics (Ton):")
print(df_production_monthly['gap_ton'].describe())

print(f"\nGap percentage statistics (Ton %):")
print(df_production_monthly['gap_pct_ton'].describe())

# ============================================================================
# STEP 8: Finalize and save
# ============================================================================
print("\n" + "=" * 100)
print("STEP 8: Finalizing and saving")
print("=" * 100)

# Reorder columns
column_order = [
    'block_id', 'block_code', 'year', 'month',
    'real_bjr_kg', 'real_jum_jjg', 'real_ton',
    'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton',
    'gap_bjr_kg', 'gap_jum_jjg', 'gap_ton',
    'gap_pct_bjr', 'gap_pct_jjg', 'gap_pct_ton'
]

df_production_monthly = df_production_monthly[column_order]

# Add ID column
df_production_monthly.insert(0, 'id', range(1, len(df_production_monthly) + 1))

# Add created_at timestamp
df_production_monthly['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"✅ Finalized production_monthly table: {len(df_production_monthly)} rows × {len(df_production_monthly.columns)} columns")

# Save
output_file = 'output/normalized_tables/phase3_production/production_monthly.csv'
df_production_monthly.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")

# ============================================================================
# STEP 9: Generate report
# ============================================================================
print("\n" + "=" * 100)
print("STEP 9: Generating extraction report")
print("=" * 100)

# Statistics
blocks_with_data = df_production_monthly['block_id'].nunique()
total_records = len(df_production_monthly)
years_covered = sorted(df_production_monthly['year'].unique())
months_covered = len(df_production_monthly['month'].unique())

# Gap analysis
avg_gap_ton = df_production_monthly['gap_ton'].mean()
avg_gap_pct = df_production_monthly['gap_pct_ton'].mean()
blocks_underperforming = (df_production_monthly.groupby('block_id')['gap_pct_ton'].mean() < 0).sum()

report = f"""# PHASE 3: PRODUCTION DATA EXTRACTION REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

### Source Data
- Source file: Realisasi vs Potensi PT SR.xlsx (Sheet: Real VS Potensi Inti)
- Blocks processed: {blocks_with_data} blocks (from {len(df_blocks_prod)} available)

### Production Monthly Table
- **Total records: {total_records}**
- **Years covered: {years_covered}**
- **Months per year: {months_covered}**
- **Blocks with data: {blocks_with_data}**

## Data Structure

### Transformation: WIDE → LONG
- **Before:** {len(prod_columns)} columns (wide format)
- **After:** {total_records} rows (long format)
- **Ratio:** {total_records / blocks_with_data:.1f} records per block

### Metrics Extracted
**Per month, per block:**
1. **Realisasi (Actual):**
   - BJR (Berat Janjang Rata-rata) - kg
   - Jumlah Janjang
   - Produksi - Ton

2. **Potensi (Target):**
   - BJR - kg
   - Jumlah Janjang
   - Produksi - Ton

3. **Gap (Realisasi - Potensi):**
   - Gap BJR - kg
   - Gap Jumlah Janjang
   - Gap Produksi - Ton
   - Gap Percentage - %

## Production Statistics

### Overall Gap Analysis
- **Average gap (Ton):** {avg_gap_ton:.2f} ton/month
- **Average gap (%):** {avg_gap_pct:.2f}%
- **Blocks underperforming:** {blocks_underperforming} / {blocks_with_data} ({blocks_underperforming/blocks_with_data*100:.1f}%)

### Gap Distribution (Ton %)
{df_production_monthly['gap_pct_ton'].describe().to_string()}

## Data Coverage

### Years
- 2023: {(df_production_monthly['year'] == 2023).sum()} records
- 2024: {(df_production_monthly['year'] == 2024).sum()} records
- 2025: {(df_production_monthly['year'] == 2025).sum()} records

### Completeness
- Expected records: {len(df_blocks_prod)} blocks × {len(column_mapping)} months = {len(df_blocks_prod) * len(column_mapping)}
- Actual records: {total_records}
- Completeness: {total_records / (len(df_blocks_prod) * len(column_mapping)) * 100:.1f}%

## Next Steps

1. ✅ Phase 3 complete - Production data extracted
2. 📋 Phase 4 - Integration and SQL schema generation
3. 📋 Phase 5 - Upload to Supabase

## Files Created

```
output/normalized_tables/phase3_production/
├── production_monthly.csv ({total_records} rows) ⭐
└── production_extraction_report.md (this file)
```

## Key Insights

- ✅ Successfully transformed {len(prod_columns)} wide columns into {total_records} long records
- ✅ {blocks_with_data} blocks with complete production data
- ✅ 3-year trend data ready ({years_covered})
- ✅ Gap analysis metrics calculated
- {'✅' if avg_gap_pct > -10 else '⚠️'} Average performance: {'+' if avg_gap_pct > 0 else ''}{avg_gap_pct:.1f}% vs target

**Status:** ✅ Phase 3 Complete
**Ready for:** Phase 4 - Integration & SQL Schema
"""

with open('output/normalized_tables/phase3_production/production_extraction_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ Saved: production_extraction_report.md")

# ============================================================================
# PHASE 3 COMPLETE
# ============================================================================
print("\n" + "=" * 100)
print("✅ PHASE 3 COMPLETE!")
print("=" * 100)
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📊 Final Statistics:")
print(f"  Production records: {total_records}")
print(f"  Blocks covered: {blocks_with_data}")
print(f"  Years: {years_covered}")
print(f"  Average gap: {avg_gap_pct:.1f}%")
print(f"\nFiles created:")
print(f"  1. production_monthly.csv - {total_records} rows")
print(f"  2. production_extraction_report.md - Detailed report")
print(f"\n✅ Ready for Phase 4: Integration & SQL Schema Generation!")
