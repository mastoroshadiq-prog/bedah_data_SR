"""
Preview Merged Data: Gabungan + Realisasi
Tujuan: Generate preview untuk review sebelum upload ke Supabase
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 100)
print("PREVIEW MERGED DATA: Data Gabungan + Realisasi vs Potensi")
print("=" * 100)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 1: LOADING DATA")
print("=" * 100)

# Load data gabungan
print("\nLoading data_cleaned_latest.csv...")
df_gabungan = pd.read_csv('output/data_cleaned_latest.csv')
print(f"✓ Loaded: {df_gabungan.shape[0]} rows × {df_gabungan.shape[1]} columns")

# Load realisasi
print("\nLoading realisasi_cleaned.csv...")
df_realisasi = pd.read_csv('output/realisasi_cleaned.csv')
print(f"✓ Loaded: {df_realisasi.shape[0]} rows × {df_realisasi.shape[1]} columns")

# ============================================================================
# STEP 2: ANALYZE JOIN KEYS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: ANALYZING JOIN KEYS")
print("=" * 100)

# Extract block codes from both files
print("\n🔍 Analyzing block code columns...")

# From gabungan (k001)
if 'k001' in df_gabungan.columns:
    gabungan_blocks = df_gabungan['k001'].dropna().unique()
    print(f"\n  Data Gabungan - Column 'k001':")
    print(f"    Total unique blocks: {len(gabungan_blocks)}")
    print(f"    Sample blocks: {list(gabungan_blocks[:20])}")
else:
    print("\n  ⚠️ Warning: 'k001' not found in data_gabungan")
    gabungan_blocks = []

# From realisasi (column 3, which should be 'blok' based on structure)
# Let's check column names first
print(f"\n  Realisasi - First 5 column names:")
realisasi_cols = list(df_realisasi.columns[:5])
print(f"    {realisasi_cols}")

# The structure is: id, 1, ame001, c006a, 30, ...
# Column index 3 contains block codes
block_col_idx = 3
realisasi_blocks = df_realisasi.iloc[:, block_col_idx].dropna().unique()
print(f"\n  Realisasi - Column index {block_col_idx}:")
print(f"    Total unique blocks: {len(realisasi_blocks)}")
print(f"    Sample blocks: {list(realisasi_blocks[:20])}")

# Find overlap
overlap = set(str(x).upper().strip() for x in gabungan_blocks if pd.notna(x)).intersection(
    set(str(x).upper().strip() for x in realisasi_blocks if pd.notna(x))
)

print(f"\n📊 JOIN KEY ANALYSIS:")
print(f"  Gabungan blocks: {len(gabungan_blocks)}")
print(f"  Realisasi blocks: {len(realisasi_blocks)}")
print(f"  Common blocks: {len(overlap)}")
print(f"  Match rate: {len(overlap) / max(len(realisasi_blocks), 1) * 100:.1f}%")

if len(overlap) > 0:
    print(f"\n  ✓ Sample overlapping blocks: {sorted(list(overlap))[:30]}")

# ============================================================================
# STEP 3: PREPARE FOR MERGE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: PREPARING DATA FOR MERGE")
print("=" * 100)

# Rename realisasi column for easier merge
# Column structure: id, numeric_1, estate, blok, ha, ...
# We need to properly name the columns

print("\n🔧 Renaming Realisasi columns for clarity...")

# Get current column names
current_cols = list(df_realisasi.columns)
print(f"  Current first 10 columns: {current_cols[:10]}")

# Create new column names based on position
# We know from the CSV header that:
# Col 0: id, Col 1: (number), Col 2: estate, Col 3: blok, Col 4: ha, etc.
new_col_names = current_cols.copy()
new_col_names[1] = 'number_col'  # The numeric column
new_col_names[2] = 'estate'
new_col_names[3] = 'blok'
new_col_names[4] = 'ha'

# Rename
df_realisasi.columns = new_col_names
print(f"  ✓ Renamed. New first 10 columns: {list(df_realisasi.columns[:10])}")

# Standardize block codes for matching (uppercase, trim)
if 'k001' in df_gabungan.columns:
    df_gabungan['k001_clean'] = df_gabungan['k001'].astype(str).str.upper().str.strip()
    
df_realisasi['blok_clean'] = df_realisasi['blok'].astype(str).str.upper().str.strip()

print(f"\n✓ Standardized block codes for matching")

# ============================================================================
# STEP 4: PERFORM MERGE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: MERGING DATA")
print("=" * 100)

print("\n🔗 Performing LEFT JOIN (gabungan LEFT JOIN realisasi)...")
print("   Join key: gabungan.k001_clean = realisasi.blok_clean")

df_merged = pd.merge(
    df_gabungan,
    df_realisasi,
    left_on='k001_clean',
    right_on='blok_clean',
    how='left',
    suffixes=('_gabungan', '_realisasi')
)

print(f"\n✓ Merge completed!")
print(f"  Result shape: {df_merged.shape[0]} rows × {df_merged.shape[1]} columns")
print(f"  Columns from gabungan: ~{len(df_gabungan.columns)}")
print(f"  Columns from realisasi: ~{len(df_realisasi.columns)}")
print(f"  Total merged columns: {len(df_merged.columns)}")

# Check how many rows got matched
matched_rows = df_merged['blok_clean'].notna().sum()
print(f"\n📊 Match Statistics:")
print(f"  Total rows: {len(df_merged)}")
print(f"  Matched with realisasi: {matched_rows} ({matched_rows/len(df_merged)*100:.1f}%)")
print(f"  Unmatched: {len(df_merged) - matched_rows} ({(len(df_merged)-matched_rows)/len(df_merged)*100:.1f}%)")

# ============================================================================
# STEP 5: PREVIEW MERGED DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: DATA PREVIEW")
print("=" * 100)

print("\n📋 First 5 rows (selected key columns):")
preview_cols = [
    'id_gabungan', 'k001', 'k002',  # From gabungan
    'blok', 'estate', 'ha',  # From realisasi
]
# Filter only existing columns
preview_cols_exist = [col for col in preview_cols if col in df_merged.columns]
print(df_merged[preview_cols_exist].head())

print("\n📋 Summary Statistics:")
print(df_merged[preview_cols_exist].describe())

# ============================================================================
# STEP 6: ANALYZE MERGED DATA QUALITY
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: DATA QUALITY ANALYSIS")
print("=" * 100)

# Missing values in key columns
print("\n❓ Missing Values in Key Columns:")
for col in preview_cols_exist:
    missing = df_merged[col].isnull().sum()
    pct = (missing / len(df_merged)) * 100
    print(f"  {col:20s}: {missing:5d} missing ({pct:5.1f}%)")

# Data types
print("\n📊 Data Types Distribution:")
dtype_counts = df_merged.dtypes.value_counts()
for dtype, count in dtype_counts.items():
    print(f"  {str(dtype):20s}: {count:3d} columns")

# ============================================================================
# STEP 7: SAMPLE MATCHED RECORDS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: SAMPLE MATCHED RECORDS")
print("=" * 100)

# Get rows that were successfully matched
df_matched = df_merged[df_merged['blok'].notna()].copy()

if len(df_matched) > 0:
    print(f"\n✓ Found {len(df_matched)} matched records")
    print(f"\n📋 Sample Matched Records (first 10):")
    
    # Select interesting columns to display
    display_cols = []
    for col in ['id_gabungan', 'k001', 'k002', 'blok', 'estate', 'ha', 'nomor']:
        if col in df_matched.columns:
            display_cols.append(col)
    
    print(df_matched[display_cols].head(10).to_string(index=False))
    
    # Show estate distribution
    if 'estate' in df_matched.columns:
        print(f"\n📊 Estate Distribution in Matched Records:")
        estate_counts = df_matched['estate'].value_counts()
        for estate, count in estate_counts.items():
            print(f"  {estate}: {count} records")
else:
    print("\n⚠️ No matched records found!")

# ============================================================================
# STEP 8: IDENTIFY USEFUL REALISASI COLUMNS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 8: IDENTIFYING REALISASI COLUMNS")
print("=" * 100)

# Get columns that came from realisasi (have _realisasi suffix or are unique to realisasi)
realisasi_specific_cols = [col for col in df_merged.columns if col in df_realisasi.columns and col not in df_gabungan.columns]
print(f"\n📋 Columns from Realisasi ({len(realisasi_specific_cols)} columns):")
print(f"  First 20: {realisasi_specific_cols[:20]}")

# Check which have data
realisasi_with_data = []
for col in realisasi_specific_cols[:50]:  # Check first 50
    non_null = df_merged[col].notna().sum()
    if non_null > 0:
        realisasi_with_data.append((col, non_null))

print(f"\n✓ Columns with data ({len(realisasi_with_data)} of {min(50, len(realisasi_specific_cols))} checked):")
for col, count in sorted(realisasi_with_data, key=lambda x: x[1], reverse=True)[:20]:
    pct = (count / len(df_merged)) * 100
    print(f"  {col:30s}: {count:5d} values ({pct:5.1f}%)")

# ============================================================================
# STEP 9: EXPORT PREVIEW FILES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 9: EXPORTING PREVIEW FILES")
print("=" * 100)

# Export small preview (first 100 rows, key columns only)
print("\n📦 Exporting preview files...")

# Preview 1: First 100 rows, selected columns
preview_sample_cols = [col for col in df_merged.columns if any(x in col.lower() for x in ['id', 'k001', 'k002', 'blok', 'estate', 'ha', 'nomor'])][:30]
df_preview_small = df_merged[preview_sample_cols].head(100)
df_preview_small.to_csv('output/merged_preview_100rows.csv', index=False)
print(f"  ✓ Saved: output/merged_preview_100rows.csv ({df_preview_small.shape[0]} rows × {df_preview_small.shape[1]} cols)")

# Preview 2: Matched records only (all columns, first 50)
if len(df_matched) > 0:
    df_matched.head(50).to_csv('output/merged_matched_50rows.csv', index=False)
    print(f"  ✓ Saved: output/merged_matched_50rows.csv ({min(50, len(df_matched))} rows × {df_matched.shape[1]} cols)")

# Preview 3: Full merged data (for review)
df_merged.to_csv('output/merged_full_data.csv', index=False)
print(f"  ✓ Saved: output/merged_full_data.csv ({df_merged.shape[0]} rows × {df_merged.shape[1]} cols)")

# Excel export for easier viewing (limited to 20k rows for Excel)
df_merged.head(20000).to_excel('output/merged_preview.xlsx', index=False, engine='openpyxl')
print(f"  ✓ Saved: output/merged_preview.xlsx ({min(20000, len(df_merged))} rows × {df_merged.shape[1]} cols)")

# ============================================================================
# STEP 10: GENERATE SUMMARY REPORT
# ============================================================================

print("\n" + "=" * 100)
print("STEP 10: GENERATING SUMMARY REPORT")
print("=" * 100)

summary_report = f"""
# PREVIEW MERGED DATA - SUMMARY REPORT

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 MERGE STATISTICS

### Input Files:
- **Data Gabungan**: {df_gabungan.shape[0]} rows × {df_gabungan.shape[1]} columns
- **Realisasi vs Potensi**: {df_realisasi.shape[0]} rows × {df_realisasi.shape[1]} columns

### Merge Result:
- **Total rows**: {df_merged.shape[0]} rows
- **Total columns**: {df_merged.shape[1]} columns
- **Matched records**: {matched_rows} ({matched_rows/len(df_merged)*100:.1f}%)
- **Unmatched records**: {len(df_merged) - matched_rows} ({(len(df_merged)-matched_rows)/len(df_merged)*100:.1f}%)

### Join Details:
- **Join type**: LEFT JOIN
- **Join key**: gabungan.k001 = realisasi.blok
- **Match strategy**: Case-insensitive, trimmed

---

## 📋 DATA QUALITY

### Missing Values (Top 10 columns):
"""

# Add missing values summary
missing_summary = df_merged.isnull().sum().sort_values(ascending=False).head(10)
for col, count in missing_summary.items():
    pct = (count / len(df_merged)) * 100
    summary_report += f"\n- **{col}**: {count} missing ({pct:.1f}%)"

summary_report += f"""

### Data Types:
"""
for dtype, count in dtype_counts.items():
    summary_report += f"\n- **{dtype}**: {count} columns"

summary_report += f"""

---

## 🎯 KEY FINDINGS

### Overlap Analysis:
- **Gabungan unique blocks**: {len(gabungan_blocks)}
- **Realisasi unique blocks**: {len(realisasi_blocks)}
- **Common blocks**: {len(overlap)}
- **Match rate**: {len(overlap) / max(len(realisasi_blocks), 1) * 100:.1f}%

### Matched Records:
"""

if len(df_matched) > 0 and 'estate' in df_matched.columns:
    summary_report += f"\n**Estate Distribution:**\n"
    estate_counts = df_matched['estate'].value_counts()
    for estate, count in estate_counts.items():
        summary_report += f"\n- {estate}: {count} records"
else:
    summary_report += "\n- No estate data available"

summary_report += f"""

---

## 📁 EXPORTED FILES

1. **merged_full_data.csv**
   - Complete merged dataset
   - {df_merged.shape[0]} rows × {df_merged.shape[1]} columns
   - Ready for upload to Supabase

2. **merged_preview.xlsx**
   - Excel format for easy viewing
   - First {min(20000, len(df_merged))} rows
   - All columns included

3. **merged_preview_100rows.csv**
   - Small sample for quick review
   - 100 rows × {df_preview_small.shape[1]} key columns

4. **merged_matched_50rows.csv** (if matches found)
   - Matched records only
   - {min(50, len(df_matched)) if len(df_matched) > 0 else 0} rows × {df_matched.shape[1] if len(df_matched) > 0 else 0} columns

---

## 💡 RECOMMENDATIONS

### Based on the merge analysis:

"""

if matched_rows / len(df_merged) > 0.5:
    summary_report += f"""
✅ **HIGH MATCH RATE ({matched_rows/len(df_merged)*100:.1f}%)**

**Recommendation**: Proceed with merged data upload

**Action Items:**
1. Review merged_preview.xlsx to validate data quality
2. Check if all expected columns are present
3. Upload merged_full_data.csv to Supabase
4. Create indexes on k001 and blok columns
"""
elif matched_rows / len(df_merged) > 0.2:
    summary_report += f"""
⚠️ **MODERATE MATCH RATE ({matched_rows/len(df_merged)*100:.1f}%)**

**Recommendation**: Consider uploading separately OR investigate unmatched records

**Action Items:**
1. Review why {len(df_merged) - matched_rows} records didn't match
2. Check for data quality issues in join keys
3. Decide: Upload merged OR upload separately
"""
else:
    summary_report += f"""
❌ **LOW MATCH RATE ({matched_rows/len(df_merged)*100:.1f}%)**

**Recommendation**: Upload files separately, establish relationship via foreign key

**Action Items:**
1. Upload data_cleaned_latest.csv → Table: data_gabungan
2. Upload realisasi_cleaned.csv → Table: realisasi_vs_potensi
3. Create JOIN queries when analysis needs both datasets
4. Investigate join key mismatches
"""

summary_report += f"""

### File Size Considerations:

- **Current merged file**: ~{df_merged.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB in memory
- **Columns**: {df_merged.shape[1]} (very wide table)

**If too wide**, consider:
- Uploading separately with foreign key relationship
- Creating views in Supabase for common join patterns
- Selecting only necessary columns from realisasi

---

## 📞 NEXT STEPS

Choose one of the following options:

### Option A: Upload Merged Data ✅
```bash
# Upload to Supabase
python upload_to_supabase.py
# (Modify script to use merged_full_data.csv)
```

### Option B: Upload Separately 📊
```bash
# Upload data_gabungan
python upload_to_supabase.py --file data_cleaned_latest.csv --table data_gabungan

# Upload realisasi
python upload_to_supabase.py --file realisasi_cleaned.csv --table realisasi_vs_potensi
```

### Option C: Review & Decide 🔍
1. Open `merged_preview.xlsx` in Excel
2. Review data quality and completeness
3. Decide based on your analysis needs

---

**Status**: ✅ Preview Ready - Awaiting Decision
"""

# Save report
with open('output/merged_data_preview_report.md', 'w', encoding='utf-8') as f:
    f.write(summary_report)

print(f"\n✓ Saved: output/merged_data_preview_report.md")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("PREVIEW COMPLETED!")
print("=" * 100)

print(f"""
📊 MERGE SUMMARY:
  - Total rows: {df_merged.shape[0]}
  - Total columns: {df_merged.shape[1]}
  - Matched records: {matched_rows} ({matched_rows/len(df_merged)*100:.1f}%)
  - Unmatched records: {len(df_merged) - matched_rows} ({(len(df_merged)-matched_rows)/len(df_merged)*100:.1f}%)

📁 FILES GENERATED:
  ✓ merged_full_data.csv - Complete merged data
  ✓ merged_preview.xlsx - Excel preview (first 20k rows)
  ✓ merged_preview_100rows.csv - Small sample
  ✓ merged_matched_50rows.csv - Matched records only
  ✓ merged_data_preview_report.md - Detailed report

🎯 NEXT STEPS:
  1. Review files in output/ directory
  2. Open merged_preview.xlsx for visual inspection
  3. Read merged_data_preview_report.md for recommendations
  4. Decide: Upload merged OR upload separately

""")

print("=" * 100)
print("Ready for your decision!")
print("=" * 100)
