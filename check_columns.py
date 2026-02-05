import pandas as pd

df = pd.read_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv')

print('Exact columns in CSV:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print(f'\nFirst row sample:')
print(df.iloc[0])
