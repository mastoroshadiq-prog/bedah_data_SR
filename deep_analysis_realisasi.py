"""
Deep Analysis & Preprocessing untuk Realisasi vs Potensi PT SR.xlsx
Tujuan: 
1. Identifikasi struktur header yang benar
2. Parse data dengan tepat
3. Analisa relationship dengan data_gabungan
4. Generate insights
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("DEEP ANALYSIS: Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

# ============================================================================
# STEP 1: RAW FILE EXPLORATION
# ============================================================================

print("\n" + "=" * 100)
print("STEP 1: RAW FILE EXPLORATION (First 20 rows, no header)")
print("=" * 100)

# Read raw without header
df_raw = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', header=None, nrows=20)
print(f"\nShape: {df_raw.shape}")
print(f"\nFirst 20 rows (raw):")
print(df_raw)

# Save to see structure
df_raw.to_csv('output/realisasi_raw_preview.csv', index=False)
print(f"\n✓ Raw preview saved to: output/realisasi_raw_preview.csv")

# ============================================================================
# STEP 2: DETECT HEADER ROW
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: HEADER DETECTION")
print("=" * 100)

print("\nAnalyzing row by row to find header...")

for row_idx in range(15):
    row_data = df_raw.iloc[row_idx]
    non_null_count = row_data.notna().sum()
    unique_count = len(row_data.dropna().unique())
    
    print(f"\nRow {row_idx}:")
    print(f"  Non-null cells: {non_null_count}/{len(row_data)}")
    print(f"  Unique values: {unique_count}")
    print(f"  Sample values: {list(row_data.dropna().head(10))}")
    
    # Heuristic: header row biasanya punya banyak non-null dan unique values
    if non_null_count > len(row_data) * 0.5:
        print(f"  → Possible header row!")

# ============================================================================
# STEP 3: TRY DIFFERENT HEADER CONFIGURATIONS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: TESTING DIFFERENT HEADER CONFIGURATIONS")
print("=" * 100)

best_config = None
best_score = 0

for skip_rows in range(10):
    try:
        # Try reading with different skip rows
        df_test = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', 
                                header=0, 
                                skiprows=range(skip_rows) if skip_rows > 0 else None,
                                nrows=10)
        
        # Score this configuration
        # Good config has: many named columns, few "Unnamed", reasonable data
        unnamed_count = sum(1 for col in df_test.columns if 'Unnamed' in str(col))
        named_count = len(df_test.columns) - unnamed_count
        score = named_count * 10 - unnamed_count
        
        print(f"\nConfig: skip_rows={skip_rows}")
        print(f"  Total columns: {len(df_test.columns)}")
        print(f"  Named columns: {named_count}")
        print(f"  Unnamed columns: {unnamed_count}")
        print(f"  Score: {score}")
        print(f"  First 10 columns: {list(df_test.columns[:10])}")
        
        if score > best_score:
            best_score = score
            best_config = skip_rows
            
    except Exception as e:
        print(f"\nConfig: skip_rows={skip_rows} → Error: {str(e)[:50]}")

print(f"\n🎯 Best configuration: skip_rows={best_config} (score: {best_score})")

# ============================================================================
# STEP 4: LOAD WITH BEST CONFIGURATION
# ============================================================================

print("\n" + "=" * 100)
print(f"STEP 4: LOADING WITH BEST CONFIG (skip_rows={best_config})")
print("=" * 100)

df_realisasi = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx',
                             header=0,
                             skiprows=range(best_config) if best_config > 0 else None)

print(f"\n✓ Loaded successfully!")
print(f"  Shape: {df_realisasi.shape}")
print(f"  Memory: {df_realisasi.memory_usage(deep=True).sum() / 1024:.2f} KB")

print(f"\n📋 All Columns ({len(df_realisasi.columns)}):")
for i, col in enumerate(df_realisasi.columns, 1):
    # Clean column name for display
    col_str = str(col).strip()
    if len(col_str) > 50:
        col_str = col_str[:47] + "..."
    print(f"  {i:3d}. {col_str}")

# ============================================================================
# STEP 5: DATA PREVIEW & ANALYSIS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: DATA PREVIEW & INITIAL ANALYSIS")
print("=" * 100)

print(f"\n📊 First 5 rows:")
print(df_realisasi.head())

print(f"\n📈 Data Types:")
print(df_realisasi.dtypes.value_counts())

print(f"\n❓ Missing Values Summary:")
missing = df_realisasi.isnull().sum()
total_missing = missing.sum()
print(f"  Total missing: {total_missing:,} cells ({total_missing / (df_realisasi.shape[0] * df_realisasi.shape[1]) * 100:.2f}%)")

if total_missing > 0:
    print(f"\n  Top 10 columns with missing values:")
    top_missing = missing[missing > 0].sort_values(ascending=False).head(10)
    for col, count in top_missing.items():
        pct = (count / len(df_realisasi)) * 100
        col_str = str(col)[:40]
        print(f"    {col_str:40s}: {count:4d} ({pct:5.1f}%)")

# ============================================================================
# STEP 6: IDENTIFY KEY COLUMNS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: IDENTIFYING KEY COLUMNS (Identifiers)")
print("=" * 100)

print("\n🔍 Searching for identifier columns...")

identifier_candidates = []

for col in df_realisasi.columns:
    col_str = str(col).lower()
    
    # Check if column name suggests it's an identifier
    is_potential_id = any(keyword in col_str for keyword in [
        'kode', 'id', 'nomor', 'blok', 'afdeling', 'estate', 'block', 
        'divisi', 'wilayah', 'region', 'area', 'no'
    ])
    
    if is_potential_id or len(df_realisasi[col].dropna()) > 0:
        unique_count = df_realisasi[col].nunique()
        unique_ratio = unique_count / len(df_realisasi) if len(df_realisasi) > 0 else 0
        
        # Get sample values
        sample_values = df_realisasi[col].dropna().head(10).tolist()
        
        # Only consider if it has some variability
        if unique_count > 1:
            identifier_candidates.append({
                'column': col,
                'unique_count': unique_count,
                'unique_ratio': unique_ratio,
                'sample_values': sample_values,
                'is_potential_id': is_potential_id
            })

# Sort by likelihood of being an identifier
identifier_candidates = sorted(identifier_candidates, 
                              key=lambda x: (x['is_potential_id'], x['unique_ratio']), 
                              reverse=True)

print(f"\n📌 Found {len(identifier_candidates)} potential identifier columns:")

for i, candidate in enumerate(identifier_candidates[:15], 1):  # Top 15
    col_name = str(candidate['column'])[:40]
    print(f"\n  {i}. {col_name}")
    print(f"     Unique: {candidate['unique_count']} ({candidate['unique_ratio']*100:.1f}%)")
    print(f"     Type: {'ID Column' if candidate['is_potential_id'] else 'Data Column'}")
    print(f"     Sample: {candidate['sample_values'][:5]}")

# ============================================================================
# STEP 7: COMPARE WITH DATA GABUNGAN
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: COMPARISON WITH DATA GABUNGAN")
print("=" * 100)

# Load data gabungan
df_gabungan = pd.read_csv('output/data_cleaned_latest.csv')

print(f"\n📊 Data Gabungan Info:")
print(f"  Shape: {df_gabungan.shape}")
print(f"  Key columns: {list(df_gabungan.columns[:15])}")

# Extract all unique values from both datasets
print(f"\n🔍 Extracting identifiers from both datasets...")

# From Realisasi - try to extract from top identifier columns
realisasi_ids = set()
for candidate in identifier_candidates[:10]:  # Top 10 candidates
    col = candidate['column']
    values = df_realisasi[col].dropna().astype(str).str.strip()
    realisasi_ids.update(values.unique())

print(f"\n  Realisasi: {len(realisasi_ids)} unique identifiers")
if len(realisasi_ids) < 100:
    print(f"  Sample: {sorted(list(realisasi_ids))[:20]}")

# From Gabungan - key columns
gabungan_ids = set()
key_cols = ['k001', 'k002', 'c001', 'c002', 'c003', 'c004', 'c005', 'c006', 'c007', 'c008']
for col in key_cols:
    if col in df_gabungan.columns:
        values = df_gabungan[col].dropna().astype(str).str.strip()
        gabungan_ids.update(values.unique())

print(f"  Gabungan: {len(gabungan_ids)} unique identifiers")
if len(gabungan_ids) < 100:
    print(f"  Sample: {sorted(list(gabungan_ids))[:20]}")

# Find overlap
overlap = realisasi_ids.intersection(gabungan_ids)
only_realisasi = realisasi_ids - gabungan_ids
only_gabungan = gabungan_ids - realisasi_ids

print(f"\n📊 OVERLAP ANALYSIS:")
print(f"  Common: {len(overlap)} identifiers")
print(f"  Only in Realisasi: {len(only_realisasi)}")
print(f"  Only in Gabungan: {len(only_gabungan)}")

if len(overlap) > 0:
    coverage = len(overlap) / len(realisasi_ids) * 100 if len(realisasi_ids) > 0 else 0
    print(f"  Coverage: {coverage:.1f}%")
    print(f"\n  ✓ Common identifiers (sample): {sorted(list(overlap))[:30]}")

# ============================================================================
# STEP 8: COLUMN NAME SIMILARITY ANALYSIS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 8: COLUMN NAME SIMILARITY ANALYSIS")
print("=" * 100)

from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

print("\n🔍 Finding similar column names...")

matches = []
for col_real in df_realisasi.columns:
    for col_gab in df_gabungan.columns:
        sim = similarity(col_real, col_gab)
        if sim > 0.3:  # 30% similarity threshold
            matches.append({
                'realisasi': str(col_real)[:40],
                'gabungan': col_gab,
                'similarity': sim
            })

matches = sorted(matches, key=lambda x: x['similarity'], reverse=True)

print(f"\n📋 Top 20 column name matches:")
for i, match in enumerate(matches[:20], 1):
    print(f"  {i:2d}. {match['realisasi']:40s} ↔ {match['gabungan']:20s} ({match['similarity']*100:.1f}%)")

# ============================================================================
# STEP 9: STATISTICAL COMPARISON
# ============================================================================

print("\n" + "=" * 100)
print("STEP 9: STATISTICAL COMPARISON")
print("=" * 100)

# Numeric columns
numeric_real = df_realisasi.select_dtypes(include=[np.number]).columns
numeric_gab = df_gabungan.select_dtypes(include=[np.number]).columns

print(f"\n📊 Numeric columns:")
print(f"  Realisasi: {len(numeric_real)} columns")
print(f"  Gabungan: {len(numeric_gab)} columns")

if len(numeric_real) > 0:
    print(f"\n  Realisasi statistics (first 5 numeric cols):")
    print(df_realisasi[list(numeric_real[:5])].describe())

# ============================================================================
# STEP 10: GENERATE INSIGHTS & RECOMMENDATIONS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 10: INSIGHTS & RECOMMENDATIONS")
print("=" * 100)

insights = []

# Insight 1: Coverage
if len(overlap) > 0:
    coverage_pct = len(overlap) / max(len(realisasi_ids), 1) * 100
    if coverage_pct >= 50:
        insights.append(f"✓ GOOD: {coverage_pct:.1f}% identifier overlap found - files are related!")
    elif coverage_pct >= 20:
        insights.append(f"⚠ PARTIAL: {coverage_pct:.1f}% identifier overlap - some relationship exists")
    else:
        insights.append(f"⚠ LOW: {coverage_pct:.1f}% identifier overlap - limited relationship")
else:
    insights.append("✗ NO OVERLAP: Files appear to contain different data entities")

# Insight 2: Structure
if best_config > 0:
    insights.append(f"⚠ Header at row {best_config} - file has preamble/title rows")
else:
    insights.append("✓ Clean structure - header at row 0")

# Insight 3: Column names
unnamed_count = sum(1 for col in df_realisasi.columns if 'Unnamed' in str(col))
if unnamed_count > len(df_realisasi.columns) * 0.5:
    insights.append(f"⚠ {unnamed_count} unnamed columns - possible merged cells or complex layout")
else:
    insights.append(f"✓ Most columns have names ({len(df_realisasi.columns) - unnamed_count}/{len(df_realisasi.columns)})")

# Insight 4: Similar columns
if len(matches) > 10:
    insights.append(f"✓ Found {len(matches)} column name similarities - structural relationship exists")
else:
    insights.append(f"⚠ Limited column name overlap ({len(matches)}) - different data schemas")

print("\n🎯 KEY INSIGHTS:")
for i, insight in enumerate(insights, 1):
    print(f"\n  {i}. {insight}")

# ============================================================================
# STEP 11: SAVE CLEANED REALISASI DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 11: SAVING PREPROCESSED REALISASI DATA")
print("=" * 100)

# Clean column names
df_realisasi_clean = df_realisasi.copy()

# Rename unnamed columns
new_columns = []
for i, col in enumerate(df_realisasi_clean.columns):
    col_str = str(col).strip()
    if 'Unnamed' in col_str or col_str == '':
        new_columns.append(f'column_{i}')
    else:
        # Clean column name
        clean_name = col_str.lower().replace(' ', '_').replace('.', '_').replace('/', '_')
        clean_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_name)
        while '__' in clean_name:
            clean_name = clean_name.replace('__', '_')
        clean_name = clean_name.strip('_')
        new_columns.append(clean_name)

df_realisasi_clean.columns = new_columns

# Add metadata
df_realisasi_clean.insert(0, 'id', range(1, len(df_realisasi_clean) + 1))
df_realisasi_clean['created_at'] = datetime.now()
df_realisasi_clean['data_source'] = 'Realisasi vs Potensi PT SR.xlsx'

# Save
output_files = {
    'csv': 'output/realisasi_cleaned.csv',
    'excel': 'output/realisasi_cleaned.xlsx',
    'json': 'output/realisasi_cleaned.json'
}

df_realisasi_clean.to_csv(output_files['csv'], index=False, encoding='utf-8-sig')
df_realisasi_clean.to_excel(output_files['excel'], index=False)
df_realisasi_clean.to_json(output_files['json'], orient='records', indent=2, date_format='iso')

print(f"\n✓ Preprocessed Realisasi data saved:")
for format_type, path in output_files.items():
    file_size = pd.read_csv(path) if format_type == 'csv' else df_realisasi_clean
    print(f"  - {path}")

print(f"\n✓ Final shape: {df_realisasi_clean.shape}")
print(f"✓ Columns: {len(df_realisasi_clean.columns)}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("FINAL SUMMARY")
print("=" * 100)

summary = f"""
📊 PREPROCESSING RESULTS FOR REALISASI VS POTENSI PT SR.xlsx

1. FILE STRUCTURE
   - Original shape: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns
   - Header detected at row: {best_config}
   - Final shape: {df_realisasi_clean.shape[0]} rows × {df_realisasi_clean.shape[1]} columns

2. DATA QUALITY
   - Missing values: {df_realisasi.isnull().sum().sum():,} cells
   - Unnamed columns: {unnamed_count} (cleaned)
   - Data types: {len(numeric_real)} numeric, {len(df_realisasi.columns) - len(numeric_real)} other

3. RELATIONSHIP WITH DATA GABUNGAN
   - Identifier overlap: {len(overlap)} common identifiers
   - Coverage: {len(overlap) / max(len(realisasi_ids), 1) * 100:.1f}%
   - Column name matches: {len(matches)} similar columns

4. OUTPUT FILES
   - CSV: {output_files['csv']}
   - Excel: {output_files['excel']}
   - JSON: {output_files['json']}

5. STATUS
   {'✅ DATA READY FOR UPLOAD' if len(overlap) > 10 else '⚠️ RECOMMEND MANUAL REVIEW'}
"""

print(summary)

# Save summary report
with open('output/realisasi_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(f"# Deep Analysis Report: Realisasi vs Potensi PT SR.xlsx\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(summary)
    f.write(f"\n\n## Key Insights\n\n")
    for i, insight in enumerate(insights, 1):
        f.write(f"{i}. {insight}\n")
    f.write(f"\n\n## Top Identifier Candidates\n\n")
    for i, candidate in enumerate(identifier_candidates[:10], 1):
        f.write(f"{i}. {candidate['column']}\n")
        f.write(f"   - Unique: {candidate['unique_count']} ({candidate['unique_ratio']*100:.1f}%)\n")
        f.write(f"   - Sample: {candidate['sample_values'][:5]}\n\n")

print(f"\n✓ Full report saved to: output/realisasi_analysis_report.md")

print("\n" + "=" * 100)
print("DEEP ANALYSIS COMPLETED!")
print("=" * 100)
