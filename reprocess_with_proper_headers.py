"""
Re-process Data dengan PROPER MULTI-ROW HEADER PARSING
Berdasarkan screenshot yang diberikan user
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 100)
print("RE-PROCESSING DATA DENGAN PROPER MULTI-ROW HEADERS")
print("=" * 100)

# ============================================================================
# STEP 1: ANALYZE MULTI-ROW HEADER STRUCTURE
# ============================================================================
print("\n" + "=" * 100)
print("STEP 1: ANALYZING HEADER STRUCTURE - data_gabungan.xlsx")
print("=" * 100)

# Read first 10 rows without header to see structure
df_raw = pd.read_excel('source/data_gabungan.xlsx', header=None, nrows=10)

print("\n📋 First 10 rows (raw):")
print(df_raw.iloc[:, :20])  # Show first 20 columns

# Identify header rows
print("\n\n🔍 Detecting header rows...")
for i in range(10):
    row_values = df_raw.iloc[i, :20].values
    non_null_count = pd.notna(row_values).sum()
    print(f"Row {i}: {non_null_count} non-null values | Sample: {row_values[:5]}")

# ============================================================================
# STEP 2: BUILD MULTI-ROW HEADER MAPPING
# ============================================================================
print("\n" + "=" * 100)
print("STEP 2: BUILDING MULTI-ROW HEADER MAPPING")
print("=" * 100)

# Based on screenshot, it looks like:
# Row 0-2: Empty or metadata
# Row 3: Category headers (ESTATE, DIVISI, BLOK, TT, VARIETAS BIBIT, HA STATEMENT, etc.)
# Row 4-5: Sub-headers (LABA, BARU, LUAS TANAM, SD THN 2024, etc.)
# Row 6: Code identifiers (K001, K002, NOMOR, C001, C002, etc.)
# Row 7+: Actual data

# Let's read header rows separately
header_row1 = pd.read_excel('source/data_gabungan.xlsx', header=None, nrows=1, skiprows=3).iloc[0]
header_row2 = pd.read_excel('source/data_gabungan.xlsx', header=None, nrows=1, skiprows=4).iloc[0]
header_row3 = pd.read_excel('source/data_gabungan.xlsx', header=None, nrows=1, skiprows=5).iloc[0]
code_row = pd.read_excel('source/data_gabungan.xlsx', header=None, nrows=1, skiprows=6).iloc[0]

print("\n📋 Header Row 1 (Category):")
print(header_row1[:20].values)

print("\n📋 Header Row 2 (Sub-category):")
print(header_row2[:20].values)

print("\n📋 Header Row 3 (Details):")
print(header_row3[:20].values)

print("\n📋 Code Row (K001, C001, etc.):")
print(code_row[:20].values)

# ============================================================================
# STEP 3: CREATE MEANINGFUL COLUMN NAMES
# ============================================================================
print("\n" + "=" * 100)
print("STEP 3: CREATING MEANINGFUL COLUMN NAMES")
print("=" * 100)

def combine_headers(h1, h2, h3, code):
    """Combine multi-row headers into meaningful column name"""
    parts = []
    
    # Add each header level if not null
    for h in [h1, h2, h3]:
        if pd.notna(h) and str(h).strip() and str(h) not in ['nan', '']:
            cleaned = str(h).strip()
            # Skip if it's just a number or looks like data
            if not cleaned.replace('.', '').replace('-', '').isdigit():
                parts.append(cleaned)
    
    # Combine with underscore
    if parts:
        combined = '_'.join(parts)
        # Clean up the name
        combined = combined.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
        combined = combined.replace('.', '').replace('-', '_').lower()
        # Remove multiple underscores
        while '__' in combined:
            combined = combined.replace('__', '_')
        return combined.strip('_')
    else:
        # If no meaningful headers, use the code
        return str(code).lower() if pd.notna(code) else f'col_{len(parts)}'

# Build column name mapping
column_mapping = {}
meaningful_columns = []

for i in range(len(code_row)):
    code = code_row[i]
    h1 = header_row1[i] if i < len(header_row1) else np.nan
    h2 = header_row2[i] if i < len(header_row2) else np.nan
    h3 = header_row3[i] if i < len(header_row3) else np.nan
    
    meaningful_name = combine_headers(h1, h2, h3, code)
    column_mapping[str(code)] = meaningful_name
    meaningful_columns.append(meaningful_name)

print("\n📋 Sample Column Mappings (first 30):")
for i, (code, name) in enumerate(list(column_mapping.items())[:30], 1):
    print(f"{i:3d}. {code:10s} → {name}")

# ============================================================================
# STEP 4: SAVE COLUMN MAPPING
# ============================================================================
print("\n" + "=" * 100)
print("STEP 4: SAVING COLUMN MAPPING")
print("=" * 100)

mapping_df = pd.DataFrame({
    'code': list(column_mapping.keys()),
    'meaningful_name': list(column_mapping.values())
})

mapping_df.to_csv('output/column_name_mapping.csv', index=False, encoding='utf-8')
print("✅ Column mapping saved to: output/column_name_mapping.csv")

# Also save as readable text
with open('output/column_name_mapping.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 100 + "\n")
    f.write("COLUMN NAME MAPPING: CODE → MEANINGFUL NAME\n")
    f.write("=" * 100 + "\n\n")
    
    for i, (code, name) in enumerate(column_mapping.items(), 1):
        f.write(f"{i:3d}. {code:10s} → {name}\n")

print("✅ Column mapping saved to: output/column_name_mapping.txt")

# ============================================================================
# STEP 5: RE-LOAD DATA WITH MEANINGFUL COLUMNS
# ============================================================================
print("\n" + "=" * 100)
print("STEP 5: RE-LOADING DATA WITH MEANINGFUL COLUMNS")
print("=" * 100)

# Read actual data (skip header rows, start from row 7)
df_data = pd.read_excel('source/data_gabungan.xlsx', header=None, skiprows=7)

# Assign meaningful column names
df_data.columns = meaningful_columns[:len(df_data.columns)]

print(f"\n✅ Data loaded: {len(df_data)} rows × {len(df_data.columns)} columns")
print("\n📋 Sample data with meaningful columns:")
print(df_data.head(10))

# Save with meaningful columns
df_data.to_csv('output/data_gabungan_meaningful_columns.csv', index=False, encoding='utf-8')
print("\n✅ Data saved to: output/data_gabungan_meaningful_columns.csv")

print("\n" + "=" * 100)
print("COMPLETE! Now you have data with proper meaningful column names!")
print("=" * 100)
