"""
FIX blocks CSV - remove extra column and keep only what's needed
"""

import pandas as pd

# Read blocks
df_blocks = pd.read_csv('output/normalized_tables/phase1_core/blocks_standardized.csv')

print("Before fix:")
print(f"Columns: {list(df_blocks.columns)}")
print(f"Rows: {len(df_blocks)}")

# Remove 'block_code_standardized' column
df_blocks = df_blocks.drop('block_code_standardized', axis=1)

print("\nAfter fix:")
print(f"Columns: {list(df_blocks.columns)}")

# Save
df_blocks.to_csv('output/normalized_tables/phase1_core/blocks_standardized.csv', index=False)

print("\n✅ Fixed! blocks_standardized.csv now has correct columns")
print("Columns: id, block_code, has_production_data, category")
