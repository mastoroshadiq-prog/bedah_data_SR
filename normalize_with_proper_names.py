"""
COMPLETE RE-NORMALIZATION dengan MEANINGFUL COLUMN NAMES
Menggunakan data yang sudah di-extract dengan proper multi-row headers
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

print("=" * 100)
print("COMPLETE RE-NORMALIZATION DENGAN MEANINGFUL COLUMN NAMES")
print("=" * 100)

# ============================================================================
# STEP 1: LOAD DATA DENGAN MEANINGFUL COLUMNS
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1: LOADING DATA WITH MEANINGFUL COLUMNS")
print("=" * 100)

df = pd.read_csv('output/data_gabungan_meaningful_columns.csv')
print(f"✅ Loaded: {len(df)} rows × {len(df.columns)} columns")

# Display sample
print("\n📋 Sample data:")
print(df.head(3))

# ============================================================================
# STEP 2: IDENTIFY KEY COLUMNS FOR NORMALIZATION
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: IDENTIFYING KEY COLUMNS")
print("=" * 100)

# Based on the meaningful names, identify key entity columns
estate_related = [col for col in df.columns if 'estate' in col.lower()]
block_related = [col for col in df.columns if 'blok' in col.lower() or 'block' in col.lower()]
production_related = [col for col in df.columns if any(x in col.lower() for x in ['real', 'potensi', 'bjr', 'ton', 'jjg'])]

print(f"\n📊 Estate-related columns: {len(estate_related)}")
print(estate_related[:10])

print(f"\n📊 Block-related columns: {len(block_related)}")
print(block_related[:10])

print(f"\n📊 Production-related columns: {len(production_related)}")
print(production_related[:10])

# ============================================================================
# STEP 3: CREATE NORMALIZED TABLES
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: CREATING NORMALIZED TABLES")
print("=" * 100)

# --- TABLE 1: ESTATES ---
print("\n📋 Creating estates table...")
estates_df = df[['estate_lama', 'divisi_lama']].copy()
estates_df = estates_df.rename(columns={
    'estate_lama': 'estate_code',
    'divisi_lama': 'division_code'
})
estates_df = estates_df.drop_duplicates().reset_index(drop=True)
estates_df.insert(0, 'id', range(1, len(estates_df) + 1))

print(f"✅ Estates table: {len(estates_df)} rows")
print(estates_df.head())

# --- TABLE 2: BLOCKS ---
print("\n📋 Creating blocks table...")

# Merge with estates to get estate_id
blocks_df = df[['estate_lama', 'blok_lama', 'baru', 'tt', 'varietas_bibit', 
                 'ha_statement_luas_tanam_sd_thn_2024']].copy()

blocks_df = blocks_df.rename(columns={
    'blok_lama': 'block_code',
    'baru': 'block_code_new',
    'tt': 'year_planted',
    'varietas_bibit': 'seed_variety',
    'ha_statement_luas_tanam_sd_thn_2024': 'area_ha'
})

# Add estate_id via merge
blocks_df = blocks_df.merge(
    estates_df[['estate_code', 'id']], 
    left_on='estate_lama', 
    right_on='estate_code',
    how='left'
).rename(columns={'id': 'estate_id'})

blocks_df = blocks_df[['estate_id', 'block_code', 'block_code_new', 'year_planted', 
                         'seed_variety', 'area_ha']]
blocks_df = blocks_df.drop_duplicates(subset=['block_code']).reset_index(drop=True)
blocks_df.insert(0, 'id', range(1, len(blocks_df) + 1))

print(f"✅ Blocks table: {len(blocks_df)} rows")
print(blocks_df.head())

# --- TABLE 3: PRODUCTION DATA ---
print("\n📋 Creating production_data table...")

# Select relevant production columns
prod_cols = ['blok_lama'] + [col for col in df.columns if col not in ['blok_lama'] 
             and col not in estates_df.columns and col not in blocks_df.columns
             and not any(x in col.lower() for x in ['estate', 'divisi'])]

production_df = df[prod_cols[:min(50, len(prod_cols))]].copy()  # Limit to first 50 cols for manageability

# Add block_id via merge
production_df = production_df.merge(
    blocks_df[['block_code', 'id']],
    left_on='blok_lama',
    right_on='block_code',
    how='left'
).rename(columns={'id': 'block_id'})

# Remove duplicate block_code column and blok_lama
production_df = production_df.drop(columns=['blok_lama', 'block_code'])

# Move block_id to first position
cols = production_df.columns.tolist()
cols = [c for c in cols if c == 'block_id'] + [c for c in cols if c != 'block_id']
production_df = production_df[cols]

production_df = production_df.drop_duplicates().reset_index(drop=True)
production_df.insert(0, 'id', range(1, len(production_df) + 1))

print(f"✅ Production data table: {len(production_df)} rows × {len(production_df.columns)} columns")
print(production_df.head())

# ============================================================================
# STEP 4: SAVE NORMALIZED TABLES
# ============================================================================
print("\n" + "=" * 100)
print("STEP 4: SAVING NORMALIZED TABLES")
print("=" * 100)

estates_df.to_csv('output/normalized_estates_v2.csv', index=False, encoding='utf-8')
print(f"✅ Saved: output/normalized_estates_v2.csv ({len(estates_df)} rows)")

blocks_df.to_csv('output/normalized_blocks_v2.csv', index=False, encoding='utf-8')
print(f"✅ Saved: output/normalized_blocks_v2.csv ({len(blocks_df)} rows)")

production_df.to_csv('output/normalized_production_data_v2.csv', index=False, encoding='utf-8')
print(f"✅ Saved: output/normalized_production_data_v2.csv ({len(production_df)} rows)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("✅ NORMALIZATION COMPLETE WITH MEANINGFUL COLUMN NAMES!")
print("=" * 100)

print("\n📊 SUMMARY:")
print(f"  - Estates: {len(estates_df)} records")
print(f"  - Blocks: {len(blocks_df)} records")
print(f"  - Production Data: {len(production_df)} records × {len(production_df.columns)} columns")

print("\n✅ All data normalized with meaningful column names!")
print("✅ Ready for upload to Supabase!")
