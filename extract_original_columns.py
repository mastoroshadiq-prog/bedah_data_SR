"""
Extract Original Column Names from Source Excel Files
"""

import pandas as pd

print("=" * 80)
print("EXTRACTING ORIGINAL COLUMN NAMES FROM SOURCE FILES")
print("=" * 80)

# ============================================================================
# 1. DATA_GABUNGAN.XLSX
# ============================================================================
print("\n" + "=" * 80)
print("1. ANALYZING: data_gabungan.xlsx")
print("=" * 80)

# Read with header at row 6
df_gabungan = pd.read_excel('source/data_gabungan.xlsx', header=6)
print(f"\nTotal columns: {len(df_gabungan.columns)}")
print(f"Total rows: {len(df_gabungan)}")

print("\n📋 ALL COLUMN NAMES:")
print("-" * 80)
for i, col in enumerate(df_gabungan.columns, 1):
    print(f"{i:3d}. {col}")

# ============================================================================
# 2. REALISASI VS POTENSI PT SR.XLSX
# ============================================================================
print("\n" + "=" * 80)
print("2. ANALYZING: Realisasi vs Potensi PT SR.xlsx")
print("=" * 80)

# Read with header at row 9 (as detected previously)
df_realisasi = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', header=9)
print(f"\nTotal columns: {len(df_realisasi.columns)}")
print(f"Total rows: {len(df_realisasi)}")

print("\n📋 ALL COLUMN NAMES:")
print("-" * 80)
for i, col in enumerate(df_realisasi.columns, 1):
    print(f"{i:3d}. {col}")

# ============================================================================
# 3. SAVE TO FILE FOR REFERENCE
# ============================================================================
print("\n" + "=" * 80)
print("SAVING COLUMN LISTS TO FILE")
print("=" * 80)

with open('output/original_column_names.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ORIGINAL COLUMN NAMES FROM SOURCE FILES\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("1. DATA_GABUNGAN.XLSX\n")
    f.write("-" * 80 + "\n")
    f.write(f"Total columns: {len(df_gabungan.columns)}\n\n")
    for i, col in enumerate(df_gabungan.columns, 1):
        f.write(f"{i:3d}. {col}\n")
    
    f.write("\n" + "=" * 80 + "\n\n")
    
    f.write("2. REALISASI VS POTENSI PT SR.XLSX\n")
    f.write("-" * 80 + "\n")
    f.write(f"Total columns: {len(df_realisasi.columns)}\n\n")
    for i, col in enumerate(df_realisasi.columns, 1):
        f.write(f"{i:3d}. {col}\n")

print("✅ Column list saved to: output/original_column_names.txt")

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)
