"""
FIX MAPPING UNTUK KOLOM C019-C029
Berdasarkan screenshot yang diberikan user, kolom C019-C029 adalah:
REALISASI TANAM SD NOVEMBER 2025 - KOMPOSISI POKOK dengan tahun 2009-2019
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("FIXING C019-C029 COLUMN MAPPING")
print("=" * 80)

# Load existing production data
df_prod = pd.read_csv('output/normalized_production_data_v2.csv')
print(f"\n✅ Loaded production data: {len(df_prod)} rows × {len(df_prod.columns)} columns")

# Check current column names
current_cols = list(df_prod.columns)
print(f"\nCurrent columns (first 35):")
for i, col in enumerate(current_cols[:35]):
    print(f"  {i+1}. {col}")

# Define the mapping for c019-c029
column_rename_map = {
    'c019': 'realisasi_tanam_komposisi_pokok_2009',
    'c020': 'realisasi_tanam_komposisi_pokok_2010',
    'c021': 'realisasi_tanam_komposisi_pokok_2011',
    'c022': 'realisasi_tanam_komposisi_pokok_2012',
    'c023': 'realisasi_tanam_komposisi_pokok_2013',
    'c024': 'realisasi_tanam_komposisi_pokok_2014',
    'c025': 'realisasi_tanam_komposisi_pokok_2015',
    'c026': 'realisasi_tanam_komposisi_pokok_2016',
    'c027': 'realisasi_tanam_komposisi_pokok_2017',
    'c028': 'realisasi_tanam_komposisi_pokok_2018',
    'c029': 'realisasi_tanam_komposisi_pokok_2019'
}

print(f"\n📋 Renaming columns:")
for old_name, new_name in column_rename_map.items():
    if old_name in df_prod.columns:
        print(f"  ✓ {old_name} → {new_name}")
    else:
        print(f"  ✗ {old_name} NOT FOUND in dataframe")

# Apply renaming
df_prod = df_prod.rename(columns=column_rename_map)

# Save the updated file
df_prod.to_csv('output/normalized_production_data_v2_fixed.csv', index=False, encoding='utf-8')
print(f"\n✅ Saved: output/normalized_production_data_v2_fixed.csv")

# Also update the column mapping file
mapping_df = pd.read_csv('output/column_name_mapping.csv')
print(f"\n✅ Loaded mapping file: {len(mapping_df)} rows")

# Update the mapping
for old_code, new_name in column_rename_map.items():
    mask = mapping_df['code'] == old_code.upper()
    if mask.any():
        mapping_df.loc[mask, 'meaningful_name'] = new_name
        print(f"  ✓ Updated {old_code.upper()} → {new_name}")

# Save updated mapping
mapping_df.to_csv('output/column_name_mapping_fixed.csv', index=False, encoding='utf-8')
print(f"\n✅ Saved: output/column_name_mapping_fixed.csv")

print("\n" + "=" * 80)
print("✅ MAPPING FIXED SUCCESSFULLY!")
print("=" * 80)
print(f"\nUpdated files:")
print(f"  - normalized_production_data_v2_fixed.csv")
print(f"  - column_name_mapping_fixed.csv")
