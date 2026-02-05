"""
PHASE 1: FOUNDATION & BLOCK RECONCILIATION
==========================================
Purpose: Create master blocks list from both sources
         Handle F005A duplicate
         Prepare foundation tables

Input:
- source/data_gabungan.xlsx (649 rows, has duplicate)
- source/Realisasi vs Potensi PT SR.xlsx (628 rows, clean)
- output/normalized_estates_v2.csv (existing)

Output:
- output/normalized_tables/phase1_core/estates.csv
- output/normalized_tables/phase1_core/blocks.csv
- output/normalized_tables/phase1_core/block_reconciliation_report.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

print("=" * 100)
print("PHASE 1: FOUNDATION & BLOCK RECONCILIATION")
print("=" * 100)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Create output directory
os.makedirs('output/normalized_tables/phase1_core', exist_ok=True)

# ============================================================================
# STEP 1: Load Estates (already normalized)
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1: Loading Estates")
print("=" * 100)

df_estates = pd.read_csv('output/normalized_estates_v2.csv')
print(f"✅ Loaded estates: {len(df_estates)} estates")
print(df_estates.head())

# Save to phase1 output
df_estates.to_csv('output/normalized_tables/phase1_core/estates.csv', index=False)
print(f"✅ Saved: output/normalized_tables/phase1_core/estates.csv")

# ============================================================================
# STEP 2: Extract Blocks from data_gabungan.xlsx
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: Extracting Blocks from data_gabungan.xlsx")
print("=" * 100)

# Load with multi-row header handling
# Based on our previous normalized file, we know the structure
df_gabungan_raw = pd.read_excel('source/data_gabungan.xlsx', sheet_name='Lembar1')
print(f"✅ Loaded data_gabungan.xlsx: {df_gabungan_raw.shape}")

# Try to identify block-related columns
print("\nFirst 5 column names:")
for i, col in enumerate(df_gabungan_raw.columns[:10], 1):
    print(f"  {i}. {col}")

# Based on normalized_production_data_COMPLETE.csv structure,
# we know columns should include estate, divisi, blok codes
# Let's use our existing normalized_blocks_v2.csv as primary source
# and cross-reference with data_gabungan

print("\nUsing existing normalized_blocks_v2.csv as foundation...")
df_blocks_base = pd.read_csv('output/normalized_blocks_v2.csv')
print(f"✅ Loaded existing blocks: {len(df_blocks_base)} blocks")

# ============================================================================
# STEP 3: Extract Blocks from Realisasi vs Potensi PT SR.xlsx
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: Extracting Blocks from Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

# Load Inti sheet
df_realisasi_inti = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', 
                                   sheet_name='Real VS Potensi Inti')
print(f"✅ Loaded Inti sheet: {df_realisasi_inti.shape}")

# Load Plasma sheet
df_realisasi_plasma = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx',
                                     sheet_name='Real VS Potensi Plasma')
print(f"✅ Loaded Plasma sheet: {df_realisasi_plasma.shape}")

print("\nInti columns (first 10):")
for i, col in enumerate(df_realisasi_inti.columns[:10], 1):
    print(f"  {i}. {col}")

print("\nPlasma columns (first 10):")
for i, col in enumerate(df_realisasi_plasma.columns[:10], 1):
    print(f"  {i}. {col}")

# ============================================================================
# STEP 4: Identify Block Code Columns
# ============================================================================
print("\n" + "=" * 100)
print("STEP 4: Identifying Block Codes")
print("=" * 100)

# From Inti sheet - look for block/blok column
block_col_inti = None
for col in df_realisasi_inti.columns:
    if 'blok' in str(col).lower() or 'block' in str(col).lower():
        block_col_inti = col
        break

if block_col_inti:
    print(f"✅ Found block column in Inti: '{block_col_inti}'")
    blocks_inti = df_realisasi_inti[block_col_inti].dropna().unique()
    print(f"   Total blocks in Inti: {len(blocks_inti)}")
    print(f"   Sample: {list(blocks_inti[:5])}")
else:
    print("⚠️  Block column not found, using first column as block identifier")
    # Assume second column might be block code (first might be estate)
    block_col_inti = df_realisasi_inti.columns[1]
    blocks_inti = df_realisasi_inti[block_col_inti].dropna().unique()

# From Plasma sheet
block_col_plasma = None
for col in df_realisasi_plasma.columns:
    if 'blok' in str(col).lower() or 'block' in str(col).lower():
        block_col_plasma = col
        break

if block_col_plasma:
    print(f"✅ Found block column in Plasma: '{block_col_plasma}'")
    blocks_plasma = df_realisasi_plasma[block_col_plasma].dropna().unique()
    print(f"   Total blocks in Plasma: {len(blocks_plasma)}")
    print(f"   Sample: {list(blocks_plasma[:5])}")
else:
    block_col_plasma = df_realisasi_plasma.columns[1]
    blocks_plasma = df_realisasi_plasma[block_col_plasma].dropna().unique()

# Combine all blocks from Realisasi file
all_blocks_realisasi = set(list(blocks_inti) + list(blocks_plasma))
print(f"\n✅ Total unique blocks in Realisasi PT SR: {len(all_blocks_realisasi)}")

# ============================================================================
# STEP 5: Check for F005A Duplicate in data_gabungan
# ============================================================================
print("\n" + "=" * 100)
print("STEP 5: Checking for F005A Duplicate")
print("=" * 100)

# Check in existing normalized blocks
if 'block_code' in df_blocks_base.columns:
    f005a_count = (df_blocks_base['block_code'] == 'F005A').sum()
    print(f"F005A occurrences in normalized_blocks_v2.csv: {f005a_count}")
    
    if f005a_count > 1:
        print(f"⚠️  Found {f005a_count} F005A entries - will keep first occurrence")
        # Keep first, drop duplicates
        df_blocks_master = df_blocks_base.drop_duplicates(subset=['block_code'], keep='first').copy()
        duplicates_removed = len(df_blocks_base) - len(df_blocks_master)
        print(f"✅ Removed {duplicates_removed} duplicate(s)")
    else:
        df_blocks_master = df_blocks_base.copy()
        print("✅ No duplicates found")
else:
    df_blocks_master = df_blocks_base.copy()
    print("⚠️  block_code column not found, using data as-is")

# ============================================================================
# STEP 6: Block Reconciliation
# ============================================================================
print("\n" + "=" * 100)
print("STEP 6: Block Reconciliation")
print("=" * 100)

blocks_normalized = set(df_blocks_master['block_code'].values)
blocks_realisasi = all_blocks_realisasi

print(f"\nBlock counts:")
print(f"  Normalized blocks (master): {len(blocks_normalized)}")
print(f"  Realisasi PT SR blocks: {len(blocks_realisasi)}")

# Find differences
only_in_normalized = blocks_normalized - blocks_realisasi
only_in_realisasi = blocks_realisasi - blocks_normalized
in_both = blocks_normalized & blocks_realisasi

print(f"\nReconciliation:")
print(f"  ✅ Blocks in BOTH sources: {len(in_both)}")
print(f"  ⚠️  Only in Normalized: {len(only_in_normalized)}")
print(f"  ⚠️  Only in Realisasi: {len(only_in_realisasi)}")

if only_in_normalized:
    print(f"\n  Blocks only in Normalized (sample): {list(only_in_normalized)[:10]}")
    
if only_in_realisasi:
    print(f"\n  Blocks only in Realisasi (sample): {list(only_in_realisasi)[:10]}")

# ============================================================================
# STEP 7: Create Master Blocks Table
# ============================================================================
print("\n" + "=" * 100)
print("STEP 7: Creating Master Blocks Table")
print("=" * 100)

# Add category column to indicate if block has production data
df_blocks_master['has_production_data'] = df_blocks_master['block_code'].isin(blocks_realisasi)
df_blocks_master['in_realisasi_file'] = df_blocks_master['block_code'].isin(blocks_realisasi)

# Determine category (Inti or Plasma)
df_blocks_master['category'] = df_blocks_master['block_code'].apply(
    lambda x: 'Inti' if x in blocks_inti else ('Plasma' if x in blocks_plasma else 'Unknown')
)

print(f"\nMaster blocks table:")
print(f"  Total blocks: {len(df_blocks_master)}")
print(f"  With production data: {df_blocks_master['has_production_data'].sum()}")
print(f"  Without production data: {(~df_blocks_master['has_production_data']).sum()}")
print(f"\nCategory distribution:")
print(df_blocks_master['category'].value_counts())

# Save master blocks
df_blocks_master.to_csv('output/normalized_tables/phase1_core/blocks.csv', index=False)
print(f"\n✅ Saved: output/normalized_tables/phase1_core/blocks.csv")

# ============================================================================
# STEP 8: Generate Reconciliation Report
# ============================================================================
print("\n" + "=" * 100)
print("STEP 8: Generating Reconciliation Report")
print("=" * 100)

report = f"""# PHASE 1: BLOCK RECONCILIATION REPORT

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

### Estates
- Total estates: {len(df_estates)}
- File: estates.csv

### Blocks
- Total blocks in master list: {len(df_blocks_master)}
- Blocks with production data: {df_blocks_master['has_production_data'].sum()}
- Blocks without production data: {(~df_blocks_master['has_production_data']).sum()}
- File: blocks.csv

## Data Sources

### Source 1: normalized_blocks_v2.csv
- Original count: {len(df_blocks_base)}
- After deduplication: {len(df_blocks_master)}
- Duplicates removed: {len(df_blocks_base) - len(df_blocks_master)}

### Source 2: Realisasi vs Potensi PT SR.xlsx
- Inti blocks: {len(blocks_inti)}
- Plasma blocks: {len(blocks_plasma)}
- Total unique: {len(all_blocks_realisasi)}

## Block Reconciliation

### Matches
- Blocks found in BOTH sources: {len(in_both)}
- These blocks will have complete data (metadata + production)

### Only in Normalized Master
- Count: {len(only_in_normalized)}
- These blocks will have metadata only (no production data from Realisasi file)
- Sample: {list(only_in_normalized)[:20]}

### Only in Realisasi File
- Count: {len(only_in_realisasi)}
- These blocks have production data but might lack metadata
- Sample: {list(only_in_realisasi)[:20]}

## Category Distribution

{df_blocks_master['category'].value_counts().to_string()}

## F005A Duplicate

- F005A occurrences in source: {f005a_count if 'block_code' in df_blocks_base.columns else 'N/A'}
- Action: {'Kept first occurrence, removed duplicates' if f005a_count > 1 else 'No duplicates found'}

## Next Steps

1. ✅ Phase 1 complete - Foundation tables created
2. 📋 Phase 2 - Extract metadata from data_gabungan.xlsx
3. 📋 Phase 3 - Extract production from Realisasi vs Potensi PT SR.xlsx
4. 📋 Phase 4 - Integration and schema generation

## Files Created

```
output/normalized_tables/phase1_core/
├── estates.csv ({len(df_estates)} rows)
├── blocks.csv ({len(df_blocks_master)} rows)
└── block_reconciliation_report.md (this file)
```
"""

with open('output/normalized_tables/phase1_core/block_reconciliation_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("✅ Saved: output/normalized_tables/phase1_core/block_reconciliation_report.md")

# ============================================================================
# PHASE 1 COMPLETE
# ============================================================================
print("\n" + "=" * 100)
print("✅ PHASE 1 COMPLETE!")
print("=" * 100)
print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nFiles created:")
print(f"  1. estates.csv - {len(df_estates)} estates")
print(f"  2. blocks.csv - {len(df_blocks_master)} blocks")
print(f"  3. block_reconciliation_report.md - Detailed report")
print(f"\nNext: Phase 2 - Metadata Extraction")
