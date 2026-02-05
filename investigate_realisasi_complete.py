"""
Investigate complete structure of Realisasi file to find ALL years (2014-2025)
"""
import pandas as pd
import numpy as np

print("=" * 100)
print("DETAILED INVESTIGATION: Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

# Load raw file
df_raw = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx',
                       sheet_name='Real VS Potensi Inti',
                       header=None)

print(f"\nFile dimensions: {df_raw.shape}")
print(f"Total columns: {df_raw.shape[1]}")
print(f"Total rows: {df_raw.shape[0]}")

# Check header rows for year indicators
print("\n" + "=" * 100)
print("SEARCHING FOR YEAR INDICATORS IN HEADER ROWS")
print("=" * 100)

years_to_find = list(range(2014, 2026))  # 2014-2025

for row_idx in range(10):
    row_data = df_raw.iloc[row_idx, :]
    
    # Find year mentions
    year_positions = []
    for col_idx, value in enumerate(row_data):
        if pd.notna(value):
            val_str = str(value)
            for year in years_to_find:
                if str(year) in val_str:
                    year_positions.append((col_idx, year, value))
    
    if year_positions:
        print(f"\nRow {row_idx}: Found {len(year_positions)} year indicators")
        print(f"  Years: {sorted(set([y[1] for y in year_positions]))}")
        print(f"  Sample positions: {year_positions[:5]}")

# Check column ranges
print("\n" + "=" * 100)
print("ANALYZING COLUMN STRUCTURE")
print("=" * 100)

print(f"\nShowing header structure (rows 0-8, every 20th column):")
for i in range(0, df_raw.shape[1], 20):
    end_col = min(i + 20, df_raw.shape[1])
    print(f"\nColumns {i}-{end_col-1}:")
    for row_idx in range(9):
        row_sample = df_raw.iloc[row_idx, i:end_col]
        print(f"  Row {row_idx}: {row_sample.tolist()}")

# Find data start row
print("\n" + "=" * 100)
print("FINDING DATA START ROW")
print("=" * 100)

data_start_row = None
for i in range(20):
    val = df_raw.iloc[i, 0]
    if pd.notna(val) and isinstance(val, (int, float)) and val == 1.0:
        data_start_row = i
        print(f"\n✅ Data starts at row {data_start_row}")
        print(f"   First data row: {df_raw.iloc[i, :10].tolist()}")
        break

print("\n" + "=" * 100)
print("INVESTIGATION COMPLETE")
print("=" * 100)
