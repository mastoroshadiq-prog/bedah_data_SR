import pandas as pd

df = pd.read_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv')

print('CSV columns:', df.columns.tolist())
print('\nTotal records:', len(df))

# Check G001A
g001a = df[df['block_id'] == 236]
if len(g001a) > 0:
    print('\nG001A (block_id=236) in CSV:')
    for col in df.columns:
        val = g001a[col].values[0]
        print(f'  {col}: {val}')
        
    # Compare with what we're sending to Supabase
    print('\nWhat we should upload:')
    record = g001a.to_dict('records')[0]
    for key, val in record.items():
        print(f'  {key}: {val} (type: {type(val).__name__})')
