import pandas as pd

df = pd.read_csv('output/block_division_mapping.csv')

print('DUPLICATE CHECK')
print(f'Total rows: {len(df)}')
print(f'Unique block_codes: {df["block_code"].nunique()}')

# Get unique blocks per division
print('\nESTATE DIVISION SUMMARY (UNIQUE BLOCKS)')

for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df[df['estate'] == estate]
    print(f'\n{estate}:')
    
    divisions = sorted(df_estate['division'].unique())
    for div in divisions:
        df_div = df_estate[df_estate['division'] == div]
        unique_count = df_div['block_code'].nunique()
        print(f'  {div}: {unique_count} blocks')
        
# Detail for AME001
print('\n\nAME001 BLOCKS LIST:')
ame1 = df[df['division'] == 'AME001']
unique_blocks = sorted(ame1['block_code'].unique())
for i, block in enumerate(unique_blocks, 1):
    print(f'{i}. {block}')

print(f'\nTotal AME001 unique blocks: {len(unique_blocks)}')
