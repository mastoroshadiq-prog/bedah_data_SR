"""
Complete Column Mapping dan Lengkapi Data total_kenthosan
Berdasarkan mapping dictionary yang tersedia
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("COMPLETE COLUMN MAPPING & DATA CLEANUP")
print("=" * 100)

# Load mapping dictionary
mapping_df = pd.read_csv('output/column_name_mapping_fixed.csv')
print(f"\n✅ Loaded mapping dictionary: {len(mapping_df)} rows")

# Create mapping dictionary (dari code ke meaningful_name)
column_mapping = dict(zip(mapping_df['code'].str.lower(), mapping_df['meaningful_name']))

# Load current production data
df_prod = pd.read_csv('output/normalized_production_data_v2_fixed.csv')
print(f"\n✅ Loaded production data: {len(df_prod)} rows × {len(df_prod.columns)} columns")

print("\n📋 Current column names:")
current_cols = list(df_prod.columns)
for i, col in enumerate(current_cols[:52], 1):
    print(f"  {i:2d}. {col}")

# Create new column names by applying mapping
new_column_names = []
unmapped_cols = []

for col in df_prod.columns:
    col_lower = col.lower()
    
    # Skip id dan block_id
    if col in ['id', 'block_id']:
        new_column_names.append(col)
        continue
    
    # Check if column exists in mapping
    if col_lower in column_mapping:
        mapped_name = column_mapping[col_lower]
        new_column_names.append(mapped_name)
    elif col_lower.startswith('k00') or col_lower.startswith('c0') or col_lower.startswith('p0'):
        # Columns dengan format k001, c001, p001
        code_upper = col_lower.upper()
        if code_upper in mapping_df['code'].values:
            mapped_name = mapping_df[mapping_df['code'] == code_upper]['meaningful_name'].iloc[0]
            new_column_names.append(mapped_name)
        else:
            unmapped_cols.append(col)
            new_column_names.append(col)  # Keep original
    else:
        # Keep columns that start with recognized patterns
        if any(col.startswith(prefix) for prefix in ['thn_', 'total_', 'realisasi_']):
            new_column_names.append(col)
        else:
            unmapped_cols.append(col)
            new_column_names.append(col)

print(f"\n⚠️  Unmapped columns ({len(unmapped_cols)}):")
for col in unmapped_cols:
    print(f"  - {col}")

# Apply new column names
df_prod.columns = new_column_names

print(f"\n✅ Applied new column names")

# Now calculate total_kenthosan if missing
# total_kenthosan = sisip_kentosan(C040) + C043 + C044 + C047
# which should now be: thn_2023_sisip_kentosan + thn_2024_kentosan + ... + thn_2025_kenthosan

kentosan_columns = [
    'thn_2023_sisip_kentosan',
    'thn_2024_kentosan', 
    'thn_2025_kenthosan'
]

# Check if these columns exist
existing_kentosan = [col for col in kentosan_columns if col in df_prod.columns]
print(f"\n📊 Found kentosan columns: {existing_kentosan}")

if 'total_kenthosan' in df_prod.columns and existing_kentosan:
    print(f"\n🔄 Calculating total_kenthosan...")
    
    # Calculate sum of all kentosan columns (fillna with 0)
    df_prod['total_kenthosan'] = df_prod[existing_kentosan].fillna(0).sum(axis=1)
    
    # Replace 0 with empty string for cleaner output
    df_prod['total_kenthosan'] = df_prod['total_kenthosan'].replace(0, '')
    
    print(f"✅ Completed total_kenthosan calculation for all {len(df_prod)} rows")
    
    # Show sample
    sample_with_kentosan = df_prod[df_prod['total_kenthosan'] != ''].head(10)
    if len(sample_with_kentosan) > 0:
        print(f"\n📋 Sample rows with total_kenthosan:")
        print(sample_with_kentosan[['id', 'block_id'] + existing_kentosan + ['total_kenthosan']])

# Save the corrected data
df_prod.to_csv('output/normalized_production_data_v2_complete.csv', index=False, encoding='utf-8')
print(f"\n✅ Saved: output/normalized_production_data_v2_complete.csv")

# Create a summary of column mappings applied
mapping_summary = pd.DataFrame({
    'original_column': current_cols,
    'new_column': new_column_names
})
mapping_summary.to_csv('output/column_mapping_applied.csv', index=False, encoding='utf-8')
print(f"✅ Saved: output/column_mapping_applied.csv")

print("\n" + "=" * 100)
print("✅ MAPPING COMPLETE!")
print("=" * 100)
print(f"\nFinal data:")
print(f"  - Rows: {len(df_prod)}")
print(f"  - Columns: {len(df_prod.columns)}")
print(f"  - Properly mapped columns: {len(df_prod.columns) - len(unmapped_cols)}")
print(f"  - Unmapped columns: {len(unmapped_cols)}")
