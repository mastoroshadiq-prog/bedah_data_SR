"""
FIX CSV column names with special characters
"""

import pandas as pd

print("Fixing CSV column names...")

# Fix block_pest_disease - has "%serangan" column
print("\n1. block_pest_disease.csv")
df = pd.read_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv')
print(f"   Before: {list(df.columns)}")

# Rename "%serangan" to "pct_serangan"
df = df.rename(columns={'%serangan': 'pct_serangan'})
df.to_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv', index=False)

print(f"   After:  {list(df.columns)}")
print(f"   ✅ Fixed!")

print("\n✅ All CSV column names fixed!")
print("\nNow you can:")
print("1. Run SQL fix in Supabase")
print("2. Run upload script")
