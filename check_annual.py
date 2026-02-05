import pandas as pd

df = pd.read_csv('output/normalized_tables/phase3_production/production_annual.csv')

print(f'Total records: {len(df)}')
print(f'Unique blocks: {df["block_id"].nunique()}')
print(f'Years: {sorted(df["year"].unique())}')

print(f'\nRecords per year:')
print(df.groupby('year').size())

print(f'\nAverage gap % by year:')
print(df.groupby('year')['gap_pct_ton'].mean().round(2))

print(f'\nSample data:')
print(df[['block_code', 'year', 'real_ton', 'potensi_ton', 'gap_pct_ton']].head(15))
