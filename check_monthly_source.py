import pandas as pd
import os

file = 'output/normalized_tables/phase3_production/production_monthly.csv'

print(f"File exists: {os.path.exists(file)}")

if os.path.exists(file):
    df = pd.read_csv(file)
    print(f"\nRows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    print(f"\nYear-Month combinations:")
    if 'year' in df.columns and 'month' in df.columns:
        print(df.groupby(['year', 'month']).size())
    
    print(f"\nFirst 10 rows:")
    print(df.head(10).to_string())
else:
    print("File NOT found!")
