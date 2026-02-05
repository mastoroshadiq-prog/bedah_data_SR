"""
Compare kedua file Excel untuk produksi 2023-2025
"""
import pandas as pd
import openpyxl

print("=" * 100)
print("FILE COMPARISON: data_gabungan.xlsx vs Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

# File 1: data_gabungan.xlsx
print("\n" + "=" * 100)
print("FILE 1: data_gabungan.xlsx")
print("=" * 100)

try:
    xls1 = pd.ExcelFile('source/data_gabungan.xlsx')
    print(f"\n✅ File loaded successfully")
    print(f"Sheets available: {xls1.sheet_names}")
    print(f"Total sheets: {len(xls1.sheet_names)}")
    
    # Check each sheet
    for i, sheet in enumerate(xls1.sheet_names, 1):
        df = pd.read_excel('source/data_gabungan.xlsx', sheet_name=sheet, nrows=5)
        print(f"\n{i}. Sheet: '{sheet}'")
        print(f"   Shape: {df.shape[0]} rows (preview) × {df.shape[1]} columns")
        print(f"   Sample columns: {list(df.columns[:8])}")
        
        # Check for year indicators
        year_cols = [c for c in df.columns if '201' in str(c) or '202' in str(c)]
        if year_cols:
            print(f"   Year columns found: {year_cols[:5]}")
        
        # Check for F005A duplicate
        if 'blok' in str(df.columns).lower() or 'block' in str(df.columns).lower():
            blok_col = [c for c in df.columns if 'blok' in str(c).lower() or 'block' in str(c).lower()][0]
            if 'F005A' in df[blok_col].astype(str).values:
                f005a_count = (df[blok_col].astype(str) == 'F005A').sum()
                print(f"   ⚠️  F005A found: {f005a_count} occurrences (in preview)")

except Exception as e:
    print(f"❌ Error: {e}")

# File 2: Realisasi vs Potensi PT SR.xlsx
print("\n" + "=" * 100)
print("FILE 2: Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

try:
    xls2 = pd.ExcelFile('source/Realisasi vs Potensi PT SR.xlsx')
    print(f"\n✅ File loaded successfully")
    print(f"Sheets available: {xls2.sheet_names}")
    print(f"Total sheets: {len(xls2.sheet_names)}")
    
    # Check each sheet
    for i, sheet in enumerate(xls2.sheet_names, 1):
        df = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', sheet_name=sheet, nrows=5)
        print(f"\n{i}. Sheet: '{sheet}'")
        print(f"   Shape: {df.shape[0]} rows (preview) × {df.shape[1]} columns")
        print(f"   Sample columns: {list(df.columns[:8])}")
        
        # Check for year indicators
        year_cols = [c for c in df.columns if '201' in str(c) or '202' in str(c)]
        if year_cols:
            print(f"   Year columns found: {year_cols[:5]}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
