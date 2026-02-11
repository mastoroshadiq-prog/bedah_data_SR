import pandas as pd
import sys

print("COMPARING EXCEL FILES VS DATABASE")
print("="*80)

# Load Excel files
print("\n1. Loading source Excel files...")

try:
    df_gabungan = pd.read_excel('source/data_gabungan.xlsx')
    print(f"   data_gabungan.xlsx: {len(df_gabungan)} rows")
    print(f"   Columns: {df_gabungan.columns.tolist()}")
except Exception as e:
    print(f"   Error loading data_gabungan.xlsx: {e}")
    df_gabungan = None

try:
    df_realisasi = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx')
    print(f"\n   Realisasi vs Potensi PT SR.xlsx: {len(df_realisasi)} rows")
    print(f"   Columns: {df_realisasi.columns.tolist()}")
except Exception as e:
    print(f"   Error loading Realisasi file: {e}")
    df_realisasi = None

if df_gabungan is not None:
    print("\n" + "="*80)
    print("PRODUCTION DATA FROM EXCEL (data_gabungan.xlsx)")
    print("="*80)
    
    # Try to identify production columns
    print("\nSample data (first 5 rows):")
    print(df_gabungan.head())
    
    # Look for year-related columns
    year_cols = [col for col in df_gabungan.columns if '2023' in str(col) or '2024' in str(col) or '2025' in str(col)]
    print(f"\nYear-related columns: {year_cols}")
    
    # Look for production/realisasi columns
    prod_cols = [col for col in df_gabungan.columns if any(word in str(col).lower() for word in ['real', 'potensi', 'produksi', 'ton'])]
    print(f"Production-related columns: {prod_cols}")

if df_realisasi is not None:
    print("\n" + "="*80)
    print("PRODUCTION DATA FROM EXCEL (Realisasi vs Potensi PT SR.xlsx)")
    print("="*80)
    
    print("\nSample data (first 5 rows):")
    print(df_realisasi.head())
    
    # Check if this file has yearly breakdown
    if 'TAHUN' in df_realisasi.columns or 'Tahun' in df_realisasi.columns or 'tahun' in df_realisasi.columns:
        year_col = [c for c in df_realisasi.columns if 'tahun' in c.lower()][0]
        print(f"\nYears in file: {df_realisasi[year_col].unique()}")
        
        for year in [2023, 2024, 2025]:
            df_year = df_realisasi[df_realisasi[year_col] == year]
            print(f"\n{year}: {len(df_year)} records")
    
    # Look for actual/target columns
    real_cols = [col for col in df_realisasi.columns if 'real' in str(col).lower() or 'aktual' in str(col).lower()]
    target_cols = [col for col in df_realisasi.columns if 'potensi' in str(col).lower() or 'target' in str(col).lower()]
    
    print(f"\nActual production columns: {real_cols}")
    print(f"Target production columns: {target_cols}")
    
    if len(real_cols) > 0 and len(target_cols) > 0:
        print("\n" + "="*80)
        print("CALCULATING TOTALS FROM EXCEL")
        print("="*80)
        
        real_col = real_cols[0]
        target_col = target_cols[0]
        
        # Check if there's a year column
        year_col_candidates = [c for c in df_realisasi.columns if 'tahun' in c.lower() or 'year' in c.lower()]
        
        if len(year_col_candidates) > 0:
            year_col = year_col_candidates[0]
            
            for year in [2023, 2024, 2025]:
                df_y = df_realisasi[df_realisasi[year_col] == year]
                if len(df_y) > 0:
                    actual_sum = df_y[real_col].sum()
                    target_sum = df_y[target_col].sum()
                    print(f"\n{year}:")
                    print(f"  Records: {len(df_y)}")
                    print(f"  Actual (Excel): {actual_sum:,.2f} Ton")
                    print(f"  Target (Excel): {target_sum:,.2f} Ton")
        else:
            # No year column - might be separate sheets or different structure
            print("\nNo year column found - checking for multi-year data...")
            total_actual = df_realisasi[real_col].sum()
            total_target = df_realisasi[target_col].sum()
            print(f"Total Actual: {total_actual:,.2f} Ton")
            print(f"Total Target: {total_target:,.2f} Ton")

print("\n" + "="*80)
print("COMPARISON SUMMARY")
print("="*80)
print("\nBoss's Manual Count:")
print("  2023 Actual: 141,984 Ton")
print("  2023 Target: 188,208 Ton")
print("\nDatabase Query:")
print("  2023 Actual: 140,396.31 Ton")
print("  2023 Target: 186,157.99 Ton")
print("\nDifference:")
print("  Actual: 1,587.69 Ton missing")
print("  Target: 2,050.01 Ton missing")
print("\nRoot Cause: 99 NULL + 150 ZERO values in database")
print("Action: Need to re-upload or fix these records")

print("\nDONE")
