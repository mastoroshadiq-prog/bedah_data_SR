import pandas as pd

df = pd.read_excel('source/data_gabungan.xlsx', nrows=5)
print('Total columns:', len(df.columns))
print('\nFirst 30 columns:')
for i, col in enumerate(df.columns[:30]):
    print(f'{i}: {col}')
