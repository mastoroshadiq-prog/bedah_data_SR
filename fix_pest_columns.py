import pandas as pd

# Fix block_pest_disease column names
df = pd.read_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv')

print("Before:")
print(list(df.columns))

# Rename columns with & to _
df = df.rename(columns={
    'serangan_ganoderma_pkk_stadium_1&2': 'serangan_ganoderma_pkk_stadium_1_2',
    'stadium_3&4': 'stadium_3_4'
})

print("\nAfter:")
print(list(df.columns))

# Save
df.to_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv', index=False)

print("\n✅ Fixed! Column names now match SQL schema")
