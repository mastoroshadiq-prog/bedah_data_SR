"""
FIX: Recreate estates.csv with correct data model
The current file has divisions, not estates!

Correct model:
- 3 estates (AME, OLE, DBE)
- 13 divisions (AME01, AME02, etc)
"""

import pandas as pd

# Read current file
df_old = pd.read_csv('output/normalized_tables/phase1_core/estates.csv')

print("Current data (WRONG - these are divisions!):")
print(df_old)
print(f"\nTotal rows: {len(df_old)}")
print(f"Unique estate_codes: {df_old['estate_code'].nunique()}")

# Create CORRECT estates table (only 3 estates)
estates_data = [
    {'id': 1, 'estate_code': 'AME', 'estate_name': 'Amanah Estate'},
    {'id': 2, 'estate_code': 'OLE', 'estate_name': 'Oleum Estate'},
    {'id': 3, 'estate_code': 'DBE', 'estate_name': 'Dabest Estate'}
]

df_estates = pd.DataFrame(estates_data)

# Save corrected estates
df_estates.to_csv('output/normalized_tables/phase1_core/estates.csv', index=False)

print("\n" + "="*80)
print("CORRECTED estates.csv:")
print(df_estates)
print(f"\nTotal rows: {len(df_estates)}")
print(f"Unique estate_codes: {df_estates['estate_code'].nunique()}")

# Save old data as divisions (for reference)
df_old.to_csv('output/normalized_tables/phase1_core/divisions_reference.csv', index=False)
print(f"\nOld data saved to: divisions_reference.csv")

print("\n✅ estates.csv fixed!")
print("Now you can upload successfully!")
