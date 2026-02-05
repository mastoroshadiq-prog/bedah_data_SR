import pandas as pd

df = pd.read_csv('output/block_division_mapping.csv')

print('=' * 80)
print('DUPLICATE CHECK')
print('=' * 80)
print(f'Total rows: {len(df)}')
print(f'Unique block_codes: {df["block_code"].nunique()}')
print(f'Duplicates: {len(df) - df["block_code"].nunique()}')

# Check AME001 specifically
print('\n' + '=' * 80)
print('AME001 (AME I) DETAILED CHECK')
print('=' * 80)

ame1 = df[df['division'] == 'AME001'].copy()
print(f'\nTotal AME001 rows: {len(ame1)}')
print(f'Unique AME001 blocks: {ame1["block_code"].nunique()}')

# Check for duplicates
dups = ame1[ame1.duplicated(subset=['block_code'], keep=False)]
if len(dups) > 0:
    print(f'\n⚠️  FOUND {len(dups)} DUPLICATE ENTRIES!')
    print('\nDuplicate blocks:')
    print(dups.sort_values('block_code')[['block_code', 'division', 'division_lama']])

# Show unique blocks list
print('\n' + '=' * 80)
print(f'AME001 UNIQUE BLOCKS ({ame1["block_code"].nunique()} total):')
print('=' * 80)
unique_blocks = sorted(ame1['block_code'].unique())
for i, block in enumerate(unique_blocks, 1):
    print(f'{i:3d}. {block}')

# Check each estate division
print('\n' + '=' * 80)
print('ESTATE DIVISION SUMMARY (UNIQUE BLOCKS ONLY)')
print('=' * 80)

for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df[df['estate'] == estate]
    print(f'\n{estate}:')
    
    divisions = sorted(df_estate['division'].unique())
    for div in divisions:
        df_div = df_estate[df_estate['division'] == div]
        unique_count = df_div['block_code'].nunique()
        total_count = len(df_div)
        
        if unique_count != total_count:
            print(f'  {div}: {unique_count} blocks (⚠️  {total_count} rows - has duplicates!)')
        else:
            print(f'  {div}: {unique_count} blocks')
