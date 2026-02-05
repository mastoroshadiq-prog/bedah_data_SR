"""
PHASE 3 REVISED: COMPLETE PRODUCTION DATA EXTRACTION (2023-2025)
=================================================================
Purpose: Extract FULL 3-year monthly production data from data_gabungan.xlsx
         via normalized_production_data_COMPLETE.csv
         Years: 2023, 2024, 2025 (36 months total)

Input:
- output/normalized_production_data_COMPLETE.csv (already has all data)
- output/normalized_tables/phase1_core/blocks_standardized.csv

Output:
- output/normalized_tables/phase3_production/production_monthly_COMPLETE.csv
- output/normalized_tables/phase3_production/production_extraction_report_v2.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import re

print("=" * 100)
print("PHASE 3 REVISED: COMPLETE PRODUCTION DATA EXTRACTION (2023-2025)")
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
# STEP 2: Load normalized_production_data_COMPLETE.csv
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: Loading normalized_production_data_COMPLETE.csv")
print("=" * 100)

df_complete = pd.read_csv('output/normalized_production_data_COMPLETE.csv')
print(f"✅ Loaded complete data: {df_complete.shape}")
print(f"   Total columns: {len(df_complete.columns)}")

# ============================================================================
# STEP 3: Identify production columns by year
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: Identifying production columns for 2023, 2024, 2025")
print("=" * 100)

# Pattern to find: columns with 'real', 'potensi', 'bjr', 'jjg', 'ton' and year
production_keywords = ['real', 'potensi', 'bjr', 'jjg', 'jum_jjg', 'ton']
years_needed = [2023, 2024, 2025]

production_cols_by_year = {year: [] for year in years_needed}

for col in df_complete.columns:
    col_lower = str(col).lower()
    
    # Check if it's a production column
    is_production = any(keyword in col_lower for keyword in production_keywords)
    
    if is_production:
        # Check which year it belongs to
        for year in years_needed:
            if str(year) in col:
                production_cols_by_year[year].append(col)
                break

# Display findings
for year in years_needed:
    cols = production_cols_by_year[year]
    print(f"\n{year}: Found {len(cols)} production columns")
    if cols:
        print(f"  Sample columns:")
        for col in cols[:5]:
            print(f"    - {col}")

# ============================================================================
# STEP 4: Extract month patterns from column names
# ============================================================================
print("\n" + "=" * 100)
print("STEP 4: Extracting month patterns from columns")
print("=" * 100)

# For each year, group columns by month
month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
               'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
month_full = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
              'juli', 'agustus', 'september', 'oktober', 'november', 'desember']

production_data_monthly = []

for year in years_needed:
    year_cols = production_cols_by_year[year]
    
    # Group by month
    for month_idx, (month_short, month_long) in enumerate(zip(month_names, month_full), 1):
        # Find columns for this month
        month_cols = [c for c in year_cols if month_short in str(c).lower() or month_long in str(c).lower()]
        
        if month_cols:
            # Try to identify real vs potensi columns
            real_bjr = [c for c in month_cols if 'real' in str(c).lower() and 'bjr' in str(c).lower()]
            real_jjg = [c for c in month_cols if 'real' in str(c).lower() and ('jjg' in str(c).lower() or 'janjang' in str(c).lower())]
            real_ton = [c for c in month_cols if 'real' in str(c).lower() and 'ton' in str(c).lower()]
            
            potensi_bjr = [c for c in month_cols if 'potensi' in str(c).lower() and 'bjr' in str(c).lower()]
            potensi_jjg = [c for c in month_cols if 'potensi' in str(c).lower() and ('jjg' in str(c).lower() or 'janjang' in str(c).lower())]
            potensi_ton = [c for c in month_cols if 'potensi' in str(c).lower() and 'ton' in str(c).lower()]
            
            month_data = {
                'year': year,
                'month_num': month_idx,
                'month_name': month_short.capitalize(),
                'real_bjr_col': real_bjr[0] if real_bjr else None,
                'real_jjg_col': real_jjg[0] if real_jjg else None,
                'real_ton_col': real_ton[0] if real_ton else None,
                'potensi_bjr_col': potensi_bjr[0] if potensi_bjr else None,
                'potensi_jjg_col': potensi_jjg[0] if potensi_jjg else None,
                'potensi_ton_col': potensi_ton[0] if potensi_ton else None
            }
            
            # Only add if we have at least some data
            if any([month_data['real_bjr_col'], month_data['real_ton_col'], 
                   month_data['potensi_bjr_col'], month_data['potensi_ton_col']]):
                production_data_monthly.append(month_data)

print(f"\n✅ Identified {len(production_data_monthly)} month-year combinations with production data")
print(f"\nSample mappings:")
for mapping in production_data_monthly[:3]:
    print(f"\n  {mapping['year']}-{mapping['month_name']}:")
    print(f"    Real BJR: {mapping['real_bjr_col']}")
    print(f"    Real Ton: {mapping['real_ton_col']}")
    print(f"    Potensi Ton: {mapping['potensi_ton_col']}")

# ============================================================================
# STEP 5: Transform to LONG format
# ============================================================================
print("\n" + "=" * 100)
print("STEP 5: Transforming WIDE → LONG format")
print("=" * 100)

# If month-based extraction didn't work well, try alternative approach
# Extract by column patterns for each year sequentially

if len(production_data_monthly) < 30:  # Expect ~36 months
    print(f"⚠️  Only found {len(production_data_monthly)} months via name matching")
    print("   Trying alternative sequential extraction approach...")
    
    # Alternative: extract columns sequentially based on position
    # Since we know columns are ordered by year-month
    
    production_list = []
    
    # Get block_code column
    block_col = 'block_code' if 'block_code' in df_complete.columns else df_complete.columns[1]
    
    # Extract all production columns
    all_prod_cols = [c for c in df_complete.columns 
                     if any(k in str(c).lower() for k in ['real', 'potensi']) 
                     and any(m in str(c).lower() for m in ['bjr', 'jjg', 'ton'])]
    
    print(f"\n   Found {len(all_prod_cols)} total production columns")
    print(f"   Will extract columns for years 2023-2025")
    
    # Filter for 2023-2025 only
    cols_2023_2025 = [c for c in all_prod_cols if any(str(y) in c for y in [2023, 2024, 2025])]
    
    print(f"   Filtered to {len(cols_2023_2025)} columns for 2023-2025")
    
    # Extract data using these columns
    if cols_2023_2025:
        df_prod_extract = df_complete[[block_col] + cols_2023_2025].copy()
        
        # Manually map known columns from normalized_production_data_COMPLETE.csv
        # Based on inspection, create month-year mappings
        
        # Let's use a simpler approach: just get the columns and organize by position
        # Assume groups of 6: real_bjr, real_jjg, real_ton, potensi_bjr, potensi_jjg, potensi_ton
        
        production_list = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for year in [2023, 2024, 2025]:
            year_cols = [c for c in cols_2023_2025 if str(year) in c]
            print(f"\n   {year}: {len(year_cols)} columns")
            
            # Group by metrics (groups of 6 or 3)
            # Try to identify by column names
            for month in months:
                month_cols = [c for c in year_cols if month.lower() in str(c).lower()]
                
                if month_cols:
                    # Extract this month's data
                    real_cols = [c for c in month_cols if 'real' in str(c).lower()]
                    potensi_cols = [c for c in month_cols if 'potensi' in str(c).lower()]
                    
                    month_data = df_complete[[block_col]].copy()
                    month_data['year'] = year
                    month_data['month'] = month
                    
                    # Add available metrics
                    if real_cols:
                        for col in real_cols:
                            if 'bjr' in col.lower():
                                month_data['real_bjr_kg'] = df_complete[col]
                            elif 'jjg' in col.lower() or 'janjang' in col.lower():
                                month_data['real_jum_jjg'] = df_complete[col]
                            elif 'ton' in col.lower():
                                month_data['real_ton'] = df_complete[col]
                    
                    if potensi_cols:
                        for col in potensi_cols:
                            if 'bjr' in col.lower():
                                month_data['potensi_bjr_kg'] = df_complete[col]
                            elif 'jjg' in col.lower() or 'janjang' in col.lower():
                                month_data['potensi_jum_jjg'] = df_complete[col]
                            elif 'ton' in col.lower():
                                month_data['potensi_ton'] = df_complete[col]
                    
                    # Only add if we have at least real_ton or potensi_ton
                    if 'real_ton' in month_data.columns or 'potensi_ton' in month_data.columns:
                        production_list.append(month_data)

else:
    # Use the month mappings we found
    production_list = []
    block_col = 'block_code' if 'block_code' in df_complete.columns else df_complete.columns[1]
    
    for mapping in production_data_monthly:
        # Extract this month's data
        month_df = df_complete[[block_col]].copy()
        month_df['year'] = mapping['year']
        month_df['month'] = mapping['month_name']
        
        # Add metrics if columns exist
        if mapping['real_bjr_col'] and mapping['real_bjr_col'] in df_complete.columns:
            month_df['real_bjr_kg'] = df_complete[mapping['real_bjr_col']]
        if mapping['real_jjg_col'] and mapping['real_jjg_col'] in df_complete.columns:
            month_df['real_jum_jjg'] = df_complete[mapping['real_jjg_col']]
        if mapping['real_ton_col'] and mapping['real_ton_col'] in df_complete.columns:
            month_df['real_ton'] = df_complete[mapping['real_ton_col']]
        if mapping['potensi_bjr_col'] and mapping['potensi_bjr_col'] in df_complete.columns:
            month_df['potensi_bjr_kg'] = df_complete[mapping['potensi_bjr_col']]
        if mapping['potensi_jjg_col'] and mapping['potensi_jjg_col'] in df_complete.columns:
            month_df['potensi_jum_jjg'] = df_complete[mapping['potensi_jjg_col']]
        if mapping['potensi_ton_col'] and mapping['potensi_ton_col'] in df_complete.columns:
            month_df['potensi_ton'] = df_complete[mapping['potensi_ton_col']]
        
        production_list.append(month_df)

# Combine all months
if production_list:
    df_production_monthly = pd.concat(production_list, ignore_index=True)
    print(f"\n✅ Combined all months: {len(df_production_monthly)} records")
else:
    print("❌ No production data extracted!")
    exit(1)

# ============================================================================
# STEP 6: Add block_id and clean data
# ============================================================================
print("\n" + "=" * 100)
print("STEP 6: Adding block_id and cleaning data")
print("=" * 100)

# Merge with blocks
df_production_monthly = df_production_monthly.merge(
    df_blocks[['id', 'block_code']],
    on='block_code',
    how='inner'
)

df_production_monthly = df_production_monthly.rename(columns={'id': 'block_id'})

print(f"✅ Matched with blocks: {len(df_production_monthly)} records")
print(f"   Unique blocks: {df_production_monthly['block_id'].nunique()}")
print(f"   Years: {sorted(df_production_monthly['year'].unique())}")
print(f"   Unique months: {df_production_monthly['month'].nunique()}")

# ============================================================================
# STEP 7: Calculate gap metrics
# ============================================================================
print("\n" + "=" * 100)
print("STEP 7: Calculating gap metrics")
print("=" * 100)

# Ensure numeric columns exist, if not create them
for col in ['real_bjr_kg', 'real_jum_jjg', 'real_ton', 'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton']:
    if col not in df_production_monthly.columns:
        df_production_monthly[col] = np.nan
    else:
        df_production_monthly[col] = pd.to_numeric(df_production_monthly[col], errors='coerce')

# Calculate gaps
df_production_monthly['gap_bjr_kg'] = df_production_monthly['real_bjr_kg'] - df_production_monthly['potensi_bjr_kg']
df_production_monthly['gap_jum_jjg'] = df_production_monthly['real_jum_jjg'] - df_production_monthly['potensi_jum_jjg']
df_production_monthly['gap_ton'] = df_production_monthly['real_ton'] - df_production_monthly['potensi_ton']

# Calculate percentage gaps with zero division protection
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

# Replace inf with nan
df_production_monthly = df_production_monthly.replace([np.inf, -np.inf], np.nan)

print(f"✅ Calculated gap metrics")
print(f"\nGap statistics (Ton):")
print(df_production_monthly['gap_ton'].describe())

# ============================================================================
# STEP 8: Finalize and save
# ============================================================================
print("\n" + "=" * 100)
print("STEP 8: Finalizing and saving")
print("=" * 100)

# Reorder columns
base_cols = ['block_id', 'block_code', 'year', 'month']
metric_cols = [
    'real_bjr_kg', 'real_jum_jjg', 'real_ton',
    'potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton',
    'gap_bjr_kg', 'gap_jum_jjg', 'gap_ton',
    'gap_pct_bjr', 'gap_pct_jjg', 'gap_pct_ton'
]

df_production_monthly = df_production_monthly[base_cols + metric_cols]

# Add ID and timestamp
df_production_monthly.insert(0, 'id', range(1, len(df_production_monthly) + 1))
df_production_monthly['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"✅ Finalized table: {len(df_production_monthly)} rows × {len(df_production_monthly.columns)} columns")

# Save
output_file = 'output/normalized_tables/phase3_production/production_monthly_COMPLETE.csv'
df_production_monthly.to_csv(output_file, index=False)
print(f"✅ Saved: {output_file}")

# ============================================================================
# STEP 9: Generate report
# ============================================================================
print("\n" + "=" * 100)
print("STEP 9: Generating extraction report")
print("=" * 100)

blocks_with_data = df_production_monthly['block_id'].nunique()
total_records = len(df_production_monthly)
years_covered = sorted(df_production_monthly['year'].unique())
months_per_year = df_production_monthly.groupby('year')['month'].nunique()

# Gap analysis
avg_gap_ton = df_production_monthly['gap_ton'].mean()
avg_gap_pct = df_production_monthly['gap_pct_ton'].mean()
blocks_underperforming = (df_production_monthly.groupby('block_id')['gap_pct_ton'].mean() < 0).sum()

report = f"""# PHASE 3 REVISED: COMPLETE PRODUCTION DATA EXTRACTION REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

### Source Data
- Source: data_gabungan.xlsx (via normalized_production_data_COMPLETE.csv)
- Years extracted: 2023, 2024, 2025

### Production Monthly Table (COMPLETE)
- **Total records: {total_records}**
- **Years covered: {years_covered}**
- **Blocks with data: {blocks_with_data}**

## Data Coverage by Year

{months_per_year.to_string()}

## Overall Statistics

- **Expected records (max):** {len(df_blocks)} blocks × 36 months = {len(df_blocks) * 36}
- **Actual records:** {total_records}
- **Coverage:** {total_records / (len(df_blocks) * 36) * 100:.1f}%

## Gap Analysis

### Overall Performance
- Average gap (Ton): {avg_gap_ton:.2f} ton/month
- Average gap (%): {avg_gap_pct:.2f}%
- Blocks underperforming: {blocks_underperforming} / {blocks_with_data} ({blocks_underperforming/blocks_with_data*100:.1f}%)

### Gap Distribution (Ton)
{df_production_monthly['gap_ton'].describe().to_string()}

## Key Improvements vs Previous Version

### Previous (INCORRECT):
- ❌ Source: Realisasi PT SR.xlsx
- ❌ Records: 11,034 (18 months only)
- ❌ Years: 2023-2024 only

### Current (CORRECT):
- ✅ Source: data_gabungan.xlsx  
- ✅ Records: {total_records}
- ✅ Years: {years_covered}
- ✅ Improvement: {total_records - 11034:,} additional records!

## Next Steps

1. ✅ Phase 3 REVISED complete - Full 3-year production data!
2. 📋 Phase 4 - Integration and SQL schema generation
3. 📋 Phase 5 - Upload to Supabase

## Files Created

```
output/normalized_tables/phase3_production/
├── production_monthly.csv (11,034 rows) - OLD
├── production_monthly_COMPLETE.csv ({total_records} rows) ⭐ NEW
└── production_extraction_report_v2.md (this file)
```

**Status:** ✅ Phase 3 REVISED Complete - Full 2023-2025 data!
**Ready for:** Phase 4 - Integration & SQL Schema
"""

with open('output/normalized_tables/phase3_production/production_extraction_report_v2.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ Saved: production_extraction_report_v2.md")

# ============================================================================
# PHASE 3 REVISED COMPLETE 
# ============================================================================
print("\n" + "=" * 100)
print("✅ PHASE 3 REVISED COMPLETE!")
print("=" * 100)
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📊 Final Statistics:")
print(f"  Total records: {total_records:,}")
print(f"  Blocks: {blocks_with_data}")
print(f"  Years: {years_covered}")
print(f"  Improvement: +{total_records - 11034:,} records vs previous version!")
print(f"\nFiles created:")
print(f"  1. production_monthly_COMPLETE.csv - {total_records:,} rows ⭐")
print(f"  2. production_extraction_report_v2.md - Detailed report")
print(f"\n✅ Ready for Phase 4: Integration & SQL Schema Generation!")
