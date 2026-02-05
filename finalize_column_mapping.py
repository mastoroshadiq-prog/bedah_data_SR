"""
FINAL COMPLETE COLUMN MAPPING
Mapping semua kolom dengan benar sesuai dictionary
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("FINAL COMPLETE COLUMN MAPPING")
print("=" * 100)

# Load the production data with current column names
df_prod = pd.read_csv('output/normalized_production_data_v2_fixed.csv')
print(f"\n✅ Loaded production data: {len(df_prod)} rows × {len(df_prod.columns)} columns")

# Manual mapping for all columns based on user's modifications and context
final_column_mapping = {
    'id': 'id',
    'block_id': 'block_id',
    'k001': 'kode_blok_lama',
    'k002': 'tahun_tanam',
    'nomor': 'nomor_urut',
    'baru': 'estate_code',
    'baru.1': 'divisi_code',
    'baru.2': 'kode_blok_baru',
    'tt': 'tahun_tanam_utama',
    'varietas_bibit': 'varietas_bibit',
    'ha_statement_luas_tanam_sd_thn_2024': 'luas_tanam_sd_2024_ha',
    'penambahan': 'penambahan_luas_ha',
    'sd_2025': 'total_luas_sd_2025_ha',
    'empls': 'empls',
    'bbt': 'bbt',
    'pks': 'pks',
    'jln_parit': 'jalan_parit_ha',
    'areal_cdg': 'areal_cadangan_ha',
    'total': 'total_luas_keseluruhan_ha',
    'realisasi_tanam_sd_november_2025_komposisi_pokok': 'realisasi_tanam_komposisi_pokok_header',
    'realisasi_tanam_komposisi_pokok_2009': 'realisasi_tanam_komposisi_pokok_2009',
    'realisasi_tanam_komposisi_pokok_2010': 'realisasi_tanam_komposisi_pokok_2010',
    'realisasi_tanam_komposisi_pokok_2011': 'realisasi_tanam_komposisi_pokok_2011',
    'realisasi_tanam_komposisi_pokok_2012': 'realisasi_tanam_komposisi_pokok_2012',
    'realisasi_tanam_komposisi_pokok_2013': 'realisasi_tanam_komposisi_pokok_2013',
    'realisasi_tanam_komposisi_pokok_2014': 'realisasi_tanam_komposisi_pokok_2014',
    'realisasi_tanam_komposisi_pokok_2015': 'realisasi_tanam_komposisi_pokok_2015',
    'realisasi_tanam_komposisi_pokok_2016': 'realisasi_tanam_komposisi_pokok_2016',
    'realisasi_tanam_komposisi_pokok_2017': 'realisasi_tanam_komposisi_pokok_2017',
    'realisasi_tanam_komposisi_pokok_2018': 'realisasi_tanam_komposisi_pokok_2018',
    'realisasi_tanam_komposisi_pokok_2019': 'realisasi_tanam_komposisi_pokok_2019',
    'sd_thn_2019_pkk': 'total_sd_2019_pokok',
    'sph': 'standar_pokok_per_hektar',
    'thn_2020_tanam': 'tanam_2020',
    'thn_2020_sisip': 'sisip_2020',
    'thn_2021_tanam': 'tanam_2021',
    'thn_2021_sisip': 'sisip_2021',
    'thn_2022_tanam': 'tanam_2022',
    'thn_2022_sisip': 'sisip_2022',
    'thn_2023_tanam': 'tanam_2023',
    'thn_2023_sisip': 'sisip_2023',
    'thn_2023_sisip_kentosan': 'sisip_kentosan_2023',
    'thn_2024_tanam': 'tanam_2024',
    'thn_2024_sisip': 'sisip_2024',
    'thn_2024_kentosan': 'sisip_kentosan_2024',
    'thn_2025_tanam': 'tanam_2025',
    'thn_2025_sisip': 'sisip_2025',
    'thn_2025_kenthosan': 'sisip_kentosan_2025',
    'total_tanam': 'total_tanam',
    'total_sisip': 'total_sisip',
    'total_kenthosan': 'total_kentosan'
}

print(f"\n📋 Applying mapping to {len(final_column_mapping)} columns...")

# Apply the mapping
df_renamed = df_prod.rename(columns=final_column_mapping)

# Check which columns were not mapped
unmapped_cols = [col for col in df_prod.columns if col not in final_column_mapping]
if unmapped_cols:
    print(f"\n⚠️  Warning: {len(unmapped_cols)} columns not found in mapping:")
    for col in unmapped_cols:
        print(f"  - {col}")

# Calculate total_kentosan from sisip_kentosan columns
kentosan_cols = ['sisip_kentosan_2023', 'sisip_kentosan_2024', 'sisip_kentosan_2025']
existing_kentosan = [col for col in kentosan_cols if col in df_renamed.columns]

if existing_kentosan:
    print(f"\n🔄 Calculating total_kentosan from: {existing_kentosan}")
    df_renamed['total_kentosan'] = df_renamed[existing_kentosan].fillna(0).sum(axis=1)
    # Replace 0 with empty string
    df_renamed.loc[df_renamed['total_kentosan'] == 0, 'total_kentosan'] = ''
    
    # Count non-empty values
    non_empty = (df_renamed['total_kentosan'] != '').sum()
    print(f"✅ Calculated total_kentosan for {non_empty} blocks")

# Save the final data
output_file = 'output/normalized_production_data_final.csv'
df_renamed.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n✅ Saved final data: {output_file}")

# Create summary
print("\n" + "=" * 100)
print("✅ FINAL MAPPING COMPLETE")
print("=" * 100)
print(f"\n📊 Summary:")
print(f"  - Total rows: {len(df_renamed)}")
print(f"  - Total columns: {len(df_renamed.columns)}")
print(f"  - Mapped columns: {len(final_column_mapping)}")
print(f"  - Unmapped columns: {len(unmapped_cols)}")

print(f"\n📋 Final column names (first 25):")
for i, col in enumerate(df_renamed.columns[:25], 1):
    print(f"  {i:2d}. {col}")

print(f"\n📋 Final column names (26-51):")
for i, col in enumerate(df_renamed.columns[25:], 26):
    print(f"  {i:2d}. {col}")

# Show sample data
print(f"\n📊 Sample data (first 3 rows, first 10 columns):")
print(df_renamed.iloc[:3, :10].to_string())
