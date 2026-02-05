import pandas as pd

df = pd.read_csv('output/normalized_tables/phase1_core/blocks_standardized.csv')

print("Blocks CSV columns:")
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

print(f"\nTotal columns: {len(df.columns)}")
print(f"Total rows: {len(df)}")
