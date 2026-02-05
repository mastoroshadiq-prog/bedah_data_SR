import pandas as pd

# Load file
df = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx',
                   sheet_name='Real VS Potensi Inti',
                   header=None)

print("Total columns:", df.shape[1])
print("Total rows:", df.shape[0])

print("\nRow 0 (likely year indicators):")
row0 = df.iloc[0, :]
for i in range(0, len(row0), 20):
    print(f"  Cols {i}-{i+19}: {row0[i:i+20].tolist()}")

print("\nSearching for years 2014-2025 in first 3 rows:")
for year in range(2014, 2026):
    found_in_rows = []
    for row_idx in range(3):
        row = df.iloc[row_idx, :]
        cols = [i for i, val in enumerate(row) if pd.notna(val) and str(year) in str(val)]
        if cols:
            found_in_rows.append(f"Row{row_idx}:{len(cols)}cols")
    if found_in_rows:
        print(f"{year}: {', '.join(found_in_rows)}")
