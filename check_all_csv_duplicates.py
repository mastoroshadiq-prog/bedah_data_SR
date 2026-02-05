"""
CHECK ALL CSV FILES FOR DUPLICATES (Tables 4-8)
Find and fix any duplicate keys before upload
"""

import pandas as pd

print("=" * 100)
print("CHECKING ALL CSV FILES FOR DUPLICATES")
print("=" * 100)

# Define all remaining tables to check
tables_to_check = [
    {
        'name': 'block_pest_disease',
        'file': 'output/normalized_tables/phase2_metadata/block_pest_disease.csv',
        'unique_key': 'block_id'
    },
    {
        'name': 'block_planting_history',
        'file': 'output/normalized_tables/phase2_metadata/block_planting_history.csv',
        'unique_key': ['block_id', 'year']
    },
    {
        'name': 'block_planting_yearly',
        'file': 'output/normalized_tables/phase2_metadata/block_planting_yearly.csv',
        'unique_key': ['block_id', 'year']
    },
    {
        'name': 'production_annual',
        'file': 'output/normalized_tables/phase3_production/production_annual.csv',
        'unique_key': ['block_id', 'year']
    },
    {
        'name': 'production_monthly',
        'file': 'output/normalized_tables/phase3_production/production_monthly.csv',
        'unique_key': ['block_id', 'year', 'month']
    }
]

total_fixed = 0
results = []

for table in tables_to_check:
    name = table['name']
    file_path = table['file']
    unique_key = table['unique_key']
    
    print(f"\n[{name}]")
    print(f"  File: {file_path}")
    print(f"  Unique key: {unique_key}")
    
    df = pd.read_csv(file_path)
    rows_before = len(df)
    
    # Check for duplicates
    dupes = df[df.duplicated(subset=unique_key, keep=False)]
    
    if len(dupes) > 0:
        print(f"  ❌ DUPLICATES FOUND: {len(dupes)} duplicate rows")
        
        # Show sample
        print(f"\n  Sample duplicates:")
        if isinstance(unique_key, list):
            cols_to_show = ['id'] + unique_key
        else:
            cols_to_show = ['id', unique_key]
        print(dupes[cols_to_show].head(10).to_string(index=False))
        
        # Fix by keeping first occurrence
        df_fixed = df.drop_duplicates(subset=unique_key, keep='first')
        rows_after = len(df_fixed)
        removed = rows_before - rows_after
        
        # Save fixed version
        df_fixed.to_csv(file_path, index=False)
        
        print(f"\n  ✅ FIXED:")
        print(f"     Before: {rows_before} rows")
        print(f"     After: {rows_after} rows")
        print(f"     Removed: {removed} duplicates")
        
        total_fixed += removed
        results.append({
            'table': name,
            'status': '✅ FIXED',
            'before': rows_before,
            'after': rows_after,
            'removed': removed
        })
    else:
        print(f"  ✅ OK: No duplicates ({rows_before} unique rows)")
        results.append({
            'table': name,
            'status': '✅ OK',
            'before': rows_before,
            'after': rows_before,
            'removed': 0
        })

# Summary
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

for result in results:
    print(f"\n{result['table']}: {result['status']}")
    if result['removed'] > 0:
        print(f"  {result['before']} → {result['after']} rows (removed {result['removed']})")
    else:
        print(f"  {result['after']} rows (clean)")

print("\n" + "=" * 100)
if total_fixed > 0:
    print(f"✅ FIXED {total_fixed} total duplicates across all files")
else:
    print(f"✅ ALL FILES CLEAN - No duplicates found")
print("=" * 100)

print("\n✅ All CSV files checked and fixed!")
print("Now you can safely run: python phase5_upload_supabase.py")
