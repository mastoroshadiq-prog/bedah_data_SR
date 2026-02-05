import pandas as pd

# Read with proper header
df = pd.read_excel('source/data_gabungan.xlsx', sheet_name=0, header=[3, 4])
print('Multi-level columns:', df.columns[:10].tolist())

# Try reading with row 4 as header
df2 = pd.read_excel('source/data_gabungan.xlsx', sheet_name=0, skiprows=4, nrows=50)
print('\nColumn names:', df2.columns[:10].tolist())
print('\nFirst 20 rows:')
print(df2.iloc[:20, :6])  # First 6 columns

# Extract estate, division, block mapping
if 'Unnamed: 0' in df2.columns:
    block_col = df2.columns[0]
    
# Look for pattern
print('\n\nChecking column patterns...')
for i, col in enumerate(df2.columns[:10]):
    print(f'Col {i}: {col}')
    print(f'Sample: {df2[col].head(3).tolist()}')
    print()
