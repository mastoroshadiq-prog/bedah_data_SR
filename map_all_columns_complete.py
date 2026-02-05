"""
COMPLETE MAPPING - ALL 156 COLUMNS
Menggunakan file normalized_production_data.csv yang LENGKAP
dengan mapping dictionary yang lengkap
"""

import pandas as pd
import numpy as np

print("=" * 100)
print("COMPLETE MAPPING FOR ALL PRODUCTION DATA COLUMNS")
print("=" * 100)

# Load mapping dictionary
mapping_df = pd.read_csv('output/column_name_mapping_fixed.csv')
print(f"\n✅ Loaded mapping dictionary: {len(mapping_df)} rows")

# Create mapping dict (code -> meaningful_name)
code_to_name = dict(zip(mapping_df['code'].str.upper(), mapping_df['meaningful_name']))

# Add special mappings for columns tidak ada di dictionary
special_mappings = {
    'ID': 'id',
    'BLOCK_CODE': 'block_code',
    'C010': 'penambahan_luas_ha',  # Missing from dict
}
code_to_name.update(special_mappings)

print(f"✅ Total mappings available: {len(code_to_name)}")

# Load FULL production data (156 columns)
df_full = pd.read_csv('output/normalized_production_data.csv')
print(f"\n✅ Loaded FULL production data: {len(df_full)} rows × {len(df_full.columns)} columns")

print(f"\n📋 Original column names (first 30):")
for i, col in enumerate(df_full.columns[:30], 1):
    print(f"  {i:3d}. {col}")

# Apply mapping to ALL columns
new_columns = []
unmapped = []

for col in df_full.columns:
    col_upper = col.upper()
    
    if col_upper in code_to_name:
        new_columns.append(code_to_name[col_upper])
    else:
        # Keep original if not in mapping
        new_columns.append(col.lower())
        unmapped.append(col)

df_full.columns = new_columns

print(f"\n⚠️  Unmapped columns: {len(unmapped)}")
if unmapped:
    for col in unmapped[:10]:  # Show first 10
        print(f"  - {col}")

# Calculate total_kentosan if columns exist
kentosan_search = [col for col in df_full.columns if 'kentosan' in col.lower() and col != 'total_kentosan']
print(f"\n📊 Found kentosan columns: {len(kentosan_search)}")
for col in kentosan_search:
    print(f"  - {col}")

if kentosan_search and 'total_kentosan' in df_full.columns:
    print(f"\n🔄 Calculating total_kentosan...")
    df_full['total_kentosan'] = df_full[kentosan_search].fillna(0).sum(axis=1)
    df_full.loc[df_full['total_kentosan'] == 0, 'total_kentosan'] = ''
    non_zero = (df_full['total_kentosan'] != '').sum()
    print(f"✅ Calculated for {non_zero} blocks with kentosan data")

# Save COMPLETE mapped data
output_file = 'output/normalized_production_data_COMPLETE.csv'
df_full.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n✅ Saved COMPLETE data: {output_file}")

# Create column summary
summary = pd.DataFrame({
    'column_index': range(1, len(df_full.columns) + 1),
    'column_name': df_full.columns,
    'sample_value': [df_full[col].iloc[0] if len(df_full) > 0 else '' for col in df_full.columns]
})
summary.to_csv('output/complete_column_list.csv', index=False)
print(f"✅ Saved column list: output/complete_column_list.csv")

print("\n" + "=" * 100)
print("✅ COMPLETE MAPPING DONE")
print("=" * 100)
print(f"\nFinal statistics:")
print(f"  - Total rows: {len(df_full)}")
print(f"  - Total columns: {len(df_full.columns)}")
print(f"  - Mapped columns: {len(df_full.columns) - len(unmapped)}")
print(f"  - Unmapped columns: {len(unmapped)}")

# Show final column structure
print(f"\n📊 Final column structure (by category):")

# Group columns by prefix
identifiers = [c for c in df_full.columns if c in ['id', 'block_code', 'block_id', 'nomor', 'kode_blok_lama', 'tahun_tanam', 'nomor_urut']]
estate_info = [c for c in df_full.columns if 'estate' in c or 'divisi' in c or 'blok' in c][:10]
land_area = [c for c in df_full.columns if 'luas' in c or 'ha' in c or 'areal' in c][:10]
realisasi = [c for c in df_full.columns if 'realisasi' in c or 'real_' in c][:10]
potensi = [c for c in df_full.columns if 'potensi' in c][:10]
gap = [c for c in df_full.columns if 'gap' in c or 'vs' in c][:10]
tanam = [c for c in df_full.columns if 'tanam_' in c or 'sisip_' in c][:15]

print(f"\n  Identifiers ({len(identifiers)}): {identifiers}")
print(f"  Estate Info ({len([c for c in df_full.columns if 'estate' in c or 'divisi' in c or 'blok' in c])}): {estate_info}")
print(f"  Land Area ({len([c for c in df_full.columns if 'luas' in c or 'ha' in c or 'areal' in c])}): {land_area}")
print(f"  Realisasi ({len([c for c in df_full.columns if 'realisasi' in c or 'real_' in c])}): {realisasi}")
print(f"  Potensi ({len([c for c in df_full.columns if 'potensi' in c])}): {potensi}")
print(f"  Gap/VS ({len([c for c in df_full.columns if 'gap' in c or 'vs' in c])}): {gap}")
print(f"  Tanam/Sisip ({len([c for c in df_full.columns if 'tanam_' in c or 'sisip_' in c])}): {tanam}")
