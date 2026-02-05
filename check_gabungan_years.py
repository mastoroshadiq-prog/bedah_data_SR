import pandas as pd

print("=" * 80)
print("CHECKING data_gabungan.xlsx FOR YEAR COVERAGE")
print("=" * 80)

# Load raw
df = pd.read_excel('source/data_gabungan.xlsx', sheet_name='Lembar1', header=None, nrows=10)

print(f"\nShape: {df.shape}")
print(f"\nFirst 10 rows, showing columns 0-40:")

for i in range(10):
    row_data = df.iloc[i, :40].tolist()
    print(f"Row {i}: {row_data}")

print("\n" + "=" * 80)
print("Searching for year mentions in first 5 rows...")
print("=" * 80)

for year in range(2014, 2026):
    for row_idx in range(5):
        row = df.iloc[row_idx, :]
        mentions = sum(1 for val in row if pd.notna(val) and str(year) in str(val))
        if mentions > 0:
            print(f"Year {year} found in Row {row_idx}: {mentions} times")
            # Show positions
            positions = [i for i, val in enumerate(row) if pd.notna(val) and str(year) in str(val)]
            print(f"  Column positions: {positions[:10]}")
