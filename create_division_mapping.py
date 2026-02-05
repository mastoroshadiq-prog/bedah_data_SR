import pandas as pd

# Read Excel properly
df = pd.read_excel('source/data_gabungan.xlsx', sheet_name=0, skiprows=4)

# Rename columns for clarity
df.columns = ['block_code', 'year', 'nomor', 'estate_lama', 'estate', 'division_lama', 'division', 'block_lama', 'block_baru'] + list(df.columns[9:])

# Filter out header rows and empty rows
df = df[df['block_code'].notna()]
df = df[df['block_code'] != 'K001']  # Remove code row
df = df[df['block_code'].str.contains(r'[A-Z]\d', na=False)]  # Only valid block codes

# Extract block_code → division mapping
block_division_map = df[['block_code', 'estate', 'division', 'division_lama']].copy()
block_division_map = block_division_map[block_division_map['block_code'].notna()]

print('=' * 80)
print('BLOCK → DIVISION MAPPING')
print('=' * 80)
print(f'\nTotal blocks with division: {len(block_division_map)}')

# Show sample by division
print('\n## DIVISION BREAKDOWN:')
for div in sorted(block_division_map['division'].dropna().unique()):
    count = len(block_division_map[block_division_map['division'] == div])
    div_lama = block_division_map[block_division_map['division'] == div]['division_lama'].iloc[0]
    print(f'{div} ({div_lama}): {count} blocks')

# Show samples per division
print('\n## SAMPLE BLOCKS PER DIVISION:')
for div in sorted(block_division_map['division'].dropna().unique())[:6]:
    print(f'\n{div}:')
    sample = block_division_map[block_division_map['division'] == div].head(10)
    print(sample[['block_code', 'estate', 'division']].to_string(index=False))

# Save to CSV
output_file = 'output/block_division_mapping.csv'
block_division_map.to_csv(output_file, index=False)
print(f'\n\n✅ Saved to: {output_file}')
print(f'Total records: {len(block_division_map)}')

# Check for each estate
print('\n## ESTATE SUMMARY:')
for estate in ['AME', 'OLE', 'DBE']:
    df_estate = block_division_map[block_division_map['estate'] == estate]
    divisions = df_estate['division'].unique()
    print(f'\n{estate}: {len(df_estate)} blocks')
    for div in sorted(divisions):
        count = len(df_estate[df_estate['division'] == div])
        print(f'  - {div}: {count} blocks')
