"""
Script untuk membandingkan data antara:
1. Realisasi vs Potensi PT SR.xlsx
2. data_gabungan.xlsx (hasil normalisasi: data_cleaned_latest.csv)

Tujuan: Mengidentifikasi apakah data dari file Realisasi vs Potensi
sudah terwakili dalam data_gabungan
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 100)
print("ANALISA KOMPARATIF: Realisasi vs Potensi PT SR vs Data Gabungan")
print("=" * 100)

# ============================================================================
# STEP 1: LOAD FILE REALISASI VS POTENSI
# ============================================================================

print("\n" + "=" * 100)
print("STEP 1: LOADING FILE - Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

try:
    df_realisasi = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx')
    print(f"✓ File loaded successfully")
    print(f"  Shape: {df_realisasi.shape[0]} rows × {df_realisasi.shape[1]} columns")
    print(f"  Size: {df_realisasi.memory_usage(deep=True).sum() / 1024:.2f} KB")
except Exception as e:
    print(f"✗ Error loading file: {str(e)}")
    exit(1)

print(f"\n📋 Column Names ({len(df_realisasi.columns)}):")
for i, col in enumerate(df_realisasi.columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\n📊 Data Preview (First 5 rows):")
print(df_realisasi.head())

print(f"\n📈 Data Types:")
print(df_realisasi.dtypes)

print(f"\n❓ Missing Values:")
missing = df_realisasi.isnull().sum()
if missing.sum() > 0:
    print(missing[missing > 0])
else:
    print("  No missing values")

print(f"\n🔑 Unique Values Analysis:")
for col in df_realisasi.columns[:10]:  # First 10 columns
    unique_count = df_realisasi[col].nunique()
    print(f"  {col}: {unique_count} unique values")
    
    # Show values if < 20 unique
    if unique_count < 20 and unique_count > 0:
        try:
            unique_vals = df_realisasi[col].dropna().unique()
            if len(str(unique_vals)) < 200:  # Avoid too long output
                sorted_vals = sorted([str(v) for v in unique_vals])[:10]
                print(f"    → {sorted_vals}")
        except Exception as e:
            print(f"    → (unable to display values)")


# ============================================================================
# STEP 2: LOAD FILE DATA GABUNGAN (HASIL NORMALISASI)
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: LOADING FILE - data_gabungan.xlsx (Normalized Version)")
print("=" * 100)

try:
    # Load dari hasil normalisasi
    df_gabungan = pd.read_csv('output/data_cleaned_latest.csv')
    print(f"✓ Normalized file loaded successfully")
    print(f"  Shape: {df_gabungan.shape[0]} rows × {df_gabungan.shape[1]} columns")
    print(f"  Size: {df_gabungan.memory_usage(deep=True).sum() / 1024:.2f} KB")
except Exception as e:
    print(f"✗ Error loading normalized file: {str(e)}")
    exit(1)

print(f"\n📋 Column Names (First 20):")
for i, col in enumerate(df_gabungan.columns[:20], 1):
    print(f"  {i:2d}. {col}")
print(f"  ... (total {len(df_gabungan.columns)} columns)")

print(f"\n📊 Data Preview (First 3 rows, selected columns):")
preview_cols = [col for col in ['id', 'k001', 'k002', 'c001', 'c002', 'c003', 'c004'] if col in df_gabungan.columns]
print(df_gabungan[preview_cols].head(3))

# ============================================================================
# STEP 3: IDENTIFIKASI KEY COLUMNS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: IDENTIFIKASI KEY COLUMNS (Potential Matching Columns)")
print("=" * 100)

# Cari kolom yang mungkin jadi identifier
print("\n🔍 Analyzing potential identifier columns in Realisasi file:")

id_candidates_realisasi = []
for col in df_realisasi.columns:
    # Check if column name suggests it's an ID
    col_lower = str(col).lower()
    if any(keyword in col_lower for keyword in ['kode', 'id', 'nomor', 'blok', 'afdeling', 'block']):
        unique_ratio = df_realisasi[col].nunique() / len(df_realisasi)
        id_candidates_realisasi.append({
            'column': col,
            'unique_count': df_realisasi[col].nunique(),
            'unique_ratio': unique_ratio,
            'sample_values': df_realisasi[col].dropna().head(5).tolist()
        })

if id_candidates_realisasi:
    print("\n  Potential ID columns found:")
    for candidate in id_candidates_realisasi:
        print(f"\n  📌 {candidate['column']}")
        print(f"     Unique: {candidate['unique_count']} ({candidate['unique_ratio']*100:.1f}%)")
        print(f"     Sample: {candidate['sample_values']}")
else:
    print("  No obvious ID columns found")

print("\n🔍 Analyzing potential identifier columns in Data Gabungan:")

id_candidates_gabungan = []
for col in df_gabungan.columns[:30]:  # Check first 30 columns
    col_lower = str(col).lower()
    if any(keyword in col_lower for keyword in ['k001', 'k002', 'c001', 'c002', 'c003', 'c004', 'c005', 'c006', 'blok']):
        unique_ratio = df_gabungan[col].nunique() / len(df_gabungan)
        id_candidates_gabungan.append({
            'column': col,
            'unique_count': df_gabungan[col].nunique(),
            'unique_ratio': unique_ratio,
            'sample_values': df_gabungan[col].dropna().head(5).tolist()
        })

if id_candidates_gabungan:
    print("\n  Potential ID columns found:")
    for candidate in id_candidates_gabungan:
        print(f"\n  📌 {candidate['column']}")
        print(f"     Unique: {candidate['unique_count']} ({candidate['unique_ratio']*100:.1f}%)")
        print(f"     Sample: {candidate['sample_values']}")

# ============================================================================
# STEP 4: ANALISA OVERLAP DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: ANALISA OVERLAP & COVERAGE")
print("=" * 100)

# Try to find common identifier
print("\n🔎 Mencari kolom pencocokan...")

# Strategy: Compare column names similarity
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

potential_matches = []
for col_real in df_realisasi.columns:
    for col_gab in df_gabungan.columns:
        similarity = similar(col_real, col_gab)
        if similarity > 0.6:  # 60% similarity
            potential_matches.append({
                'realisasi_col': col_real,
                'gabungan_col': col_gab,
                'similarity': similarity
            })

if potential_matches:
    print("\n  🎯 Potential matching columns (by name similarity):")
    # Sort by similarity
    potential_matches = sorted(potential_matches, key=lambda x: x['similarity'], reverse=True)
    for match in potential_matches[:10]:  # Top 10
        print(f"     {match['realisasi_col']:30s} ← → {match['gabungan_col']:30s} (similarity: {match['similarity']*100:.1f}%)")

# ============================================================================
# STEP 5: VALUE-BASED COMPARISON
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: VALUE-BASED COMPARISON")
print("=" * 100)

print("\n📊 Statistical Comparison:")

# Get numeric columns from both
numeric_cols_real = df_realisasi.select_dtypes(include=[np.number]).columns
numeric_cols_gab = df_gabungan.select_dtypes(include=[np.number]).columns

print(f"\n  Realisasi file: {len(numeric_cols_real)} numeric columns")
print(f"  Data Gabungan: {len(numeric_cols_gab)} numeric columns")

# Basic stats comparison
print("\n  📈 Realisasi file stats:")
print(df_realisasi[numeric_cols_real].describe())

print("\n  📈 Data Gabungan stats (sample):")
sample_numeric = list(numeric_cols_gab[:5])
print(df_gabungan[sample_numeric].describe())

# ============================================================================
# STEP 6: IDENTIFIER MATCHING ANALYSIS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: DETAILED IDENTIFIER MATCHING")
print("=" * 100)

# Try to extract block/afdeling codes from both datasets
print("\n🔍 Extracting identifiers from both datasets...")

# From Realisasi
realisasi_identifiers = set()
for col in df_realisasi.columns:
    if any(keyword in str(col).lower() for keyword in ['kode', 'blok', 'afdeling', 'block']):
        values = df_realisasi[col].dropna().astype(str).unique()
        realisasi_identifiers.update(values)

print(f"\n  Found {len(realisasi_identifiers)} unique identifiers in Realisasi file")
if len(realisasi_identifiers) < 50:
    print(f"  Identifiers: {sorted(list(realisasi_identifiers))[:20]}")

# From Gabungan
gabungan_identifiers = set()
for col in ['k001', 'k002', 'c001', 'c002', 'c003', 'c004', 'c005', 'c006', 'c007']:
    if col in df_gabungan.columns:
        values = df_gabungan[col].dropna().astype(str).unique()
        gabungan_identifiers.update(values)

print(f"\n  Found {len(gabungan_identifiers)} unique identifiers in Data Gabungan")
if len(gabungan_identifiers) < 50:
    print(f"  Identifiers: {sorted(list(gabungan_identifiers))[:20]}")

# Check overlap
overlap = realisasi_identifiers.intersection(gabungan_identifiers)
only_realisasi = realisasi_identifiers - gabungan_identifiers
only_gabungan = gabungan_identifiers - realisasi_identifiers

print(f"\n📊 Overlap Analysis:")
print(f"  ✓ Common identifiers: {len(overlap)} ({len(overlap)/max(len(realisasi_identifiers),1)*100:.1f}% of Realisasi)")
print(f"  ⚠ Only in Realisasi: {len(only_realisasi)}")
print(f"  ⚠ Only in Gabungan: {len(only_gabungan)}")

if overlap:
    print(f"\n  Common identifiers (sample): {sorted(list(overlap))[:20]}")

if only_realisasi and len(only_realisasi) < 50:
    print(f"\n  Only in Realisasi: {sorted(list(only_realisasi))[:20]}")

# ============================================================================
# STEP 7: GENERATE COMPARISON REPORT
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: GENERATING COMPARISON REPORT")
print("=" * 100)

report = f"""
# ANALISA KOMPARATIF: Realisasi vs Potensi PT SR vs Data Gabungan

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## EXECUTIVE SUMMARY

### File 1: Realisasi vs Potensi PT SR.xlsx
- **Rows**: {df_realisasi.shape[0]:,}
- **Columns**: {df_realisasi.shape[1]}
- **Size**: {df_realisasi.memory_usage(deep=True).sum() / 1024:.2f} KB
- **Missing Data**: {df_realisasi.isnull().sum().sum():,} cells

### File 2: Data Gabungan (Normalized)
- **Rows**: {df_gabungan.shape[0]:,}
- **Columns**: {df_gabungan.shape[1]}
- **Size**: {df_gabungan.memory_usage(deep=True).sum() / 1024:.2f} KB
- **Missing Data**: {df_gabungan.isnull().sum().sum():,} cells

## OVERLAP ANALYSIS

### Identifier Overlap
- **Total identifiers in Realisasi**: {len(realisasi_identifiers)}
- **Total identifiers in Gabungan**: {len(gabungan_identifiers)}
- **Common identifiers**: {len(overlap)} ({len(overlap)/max(len(realisasi_identifiers),1)*100:.1f}% coverage)
- **Only in Realisasi**: {len(only_realisasi)}
- **Only in Gabungan**: {len(only_gabungan)}

### Data Coverage Analysis

"""

if len(overlap) / max(len(realisasi_identifiers), 1) >= 0.8:
    report += """
✅ **HIGH COVERAGE** (≥80%)
Data dari file Realisasi vs Potensi **SUDAH TERWAKILI dengan baik** dalam data_gabungan.
"""
elif len(overlap) / max(len(realisasi_identifiers), 1) >= 0.5:
    report += """
⚠️ **MEDIUM COVERAGE** (50-79%)
Data dari file Realisasi vs Potensi **SEBAGIAN TERWAKILI** dalam data_gabungan.
Ada beberapa data yang belum terintegrasi.
"""
else:
    report += """
❌ **LOW COVERAGE** (<50%)
Data dari file Realisasi vs Potensi **BELUM TERWAKILI dengan baik** dalam data_gabungan.
Kemungkinan kedua file berisi data yang berbeda atau struktur yang sangat berbeda.
"""

report += f"""

## DETAILED FINDINGS

### Common Identifiers (Sample)
{', '.join(sorted(list(overlap))[:30])}

### Only in Realisasi vs Potensi (Sample)
{', '.join(sorted(list(only_realisasi))[:30]) if only_realisasi else 'None'}

### Only in Data Gabungan (Sample)
{', '.join(sorted(list(only_gabungan))[:30]) if only_gabungan else 'None'}

## COLUMN STRUCTURE COMPARISON

### Realisasi vs Potensi Columns
{chr(10).join([f'{i+1}. {col}' for i, col in enumerate(df_realisasi.columns)])}

### Data Gabungan Columns (First 30)
{chr(10).join([f'{i+1}. {col}' for i, col in enumerate(df_gabungan.columns[:30])])}

## RECOMMENDATIONS

"""

if len(overlap) / max(len(realisasi_identifiers), 1) < 0.8:
    report += """
1. **Review Missing Data**: Identifikasi mengapa beberapa identifier tidak match
2. **Data Integration**: Pertimbangkan untuk menggabungkan data yang belum terintegrasi
3. **Validation**: Lakukan validasi manual untuk beberapa sample data
"""
else:
    report += """
1. ✅ Data integration sudah baik
2. ✅ Lanjutkan ke tahap analisa mendalam
3. ✅ Upload data_cleaned_latest.csv ke Supabase
"""

report += """

## NEXT STEPS

1. Review laporan ini untuk memahami coverage data
2. Jika coverage rendah, pertimbangkan merge manual
3. Jika coverage tinggi, lanjutkan upload ke Supabase
4. Lakukan analisa lanjutan pada data yang sudah terintegrasi

---
Generated by: Data Comparison Analysis Tool v1.0
"""

# Save report
report_path = 'output/comparison_report.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✓ Report saved to: {report_path}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("KESIMPULAN ANALISA")
print("=" * 100)

coverage_pct = len(overlap) / max(len(realisasi_identifiers), 1) * 100

print(f"\n📊 Data Coverage: {coverage_pct:.1f}%")

if coverage_pct >= 80:
    print("\n✅ KESIMPULAN: Data dari 'Realisasi vs Potensi PT SR.xlsx' SUDAH TERWAKILI dengan BAIK")
    print("              dalam hasil normalisasi 'data_gabungan.xlsx'")
    print("\n👍 Rekomendasi:")
    print("   • Data gabungan sudah representatif")
    print("   • Dapat langsung lanjut upload ke Supabase")
    print("   • Siap untuk analisa lanjutan")
elif coverage_pct >= 50:
    print("\n⚠️  KESIMPULAN: Data dari 'Realisasi vs Potensi PT SR.xlsx' SEBAGIAN TERWAKILI")
    print("              dalam hasil normalisasi 'data_gabungan.xlsx'")
    print("\n💡 Rekomendasi:")
    print("   • Review data yang belum ter-cover")
    print("   • Pertimbangkan merge manual jika diperlukan")
    print("   • Validasi beberapa sample data")
else:
    print("\n❌ KESIMPULAN: Data dari 'Realisasi vs Potensi PT SR.xlsx' BELUM TERWAKILI dengan baik")
    print("              dalam hasil normalisasi 'data_gabungan.xlsx'")
    print("\n⚠️  Rekomendasi:")
    print("   • Kedua file kemungkinan berisi data yang berbeda")
    print("   • Perlu investigasi lebih lanjut tentang hubungan kedua file")
    print("   • Mungkin perlu preprocessing terpisah untuk file Realisasi")

print(f"\n📄 Detail lengkap tersimpan di: {report_path}")
print("\n" + "=" * 100)
