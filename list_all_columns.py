import pandas as pd

df = pd.read_csv('output/normalized_production_data_COMPLETE.csv')
cols = list(df.columns)

print(f'Total columns: {len(cols)}')
print('\nAll columns:')
for i, c in enumerate(cols):
    print(f'{i+1:3d}. {c}')
