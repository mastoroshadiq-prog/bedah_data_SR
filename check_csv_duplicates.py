import pandas as pd

# Check for duplicate block_id in CSV
df = pd.read_csv('output/normalized_tables/phase2_metadata/block_land_infrastructure.csv')

print(f'Total rows: {len(df)}')
print(f'Unique block_id: {df["block_id"].nunique()}')

# Find duplicates
dupes = df[df.duplicated('block_id', keep=False)].sort_values('block_id')

print(f'\nDuplicate block_ids found: {len(dupes)}')

if len(dupes) > 0:
    print('\n❌ PROBLEM FOUND: CSV has duplicate block_id values!')
    print('\nDuplicate rows:')
    print(dupes[['id', 'block_id', 'block_code']].head(20))
    
    print('\n\nFixing...')
    # Keep only first occurrence of each block_id
    df_fixed = df.drop_duplicates(subset=['block_id'], keep='first')
    
    print(f'\nAfter fix:')
    print(f'  Original rows: {len(df)}')
    print(f'  Fixed rows: {len(df_fixed)}')
    print(f'  Removed: {len(df) - len(df_fixed)} duplicates')
    
    # Save fixed version
    df_fixed.to_csv('output/normalized_tables/phase2_metadata/block_land_infrastructure.csv', index=False)
    print('\n✅ CSV FIXED and saved!')
    
else:
    print('\n✅ No duplicates found in CSV')
