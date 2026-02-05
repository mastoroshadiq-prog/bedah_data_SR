"""
Investigate Block G001A Ganoderma Data Discrepancy
Dashboard: 0%
Source: 0.3%
"""
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 80)
print("INVESTIGATING BLOCK G001A GANODERMA DATA")
print("=" * 80)

# 1. Get block_id for G001A
blocks = supabase.table('blocks').select('*').eq('block_code', 'G001A').execute()
if len(blocks.data) > 0:
    block = blocks.data[0]
    block_id = block['id']
    print(f"\nBlock found in database:")
    print(f"  ID: {block_id}")
    print(f"  Code: {block['block_code']}")
    print(f"  Division ID: {block.get('division_id')}")
else:
    print("\n❌ Block G001A NOT FOUND in blocks table!")
    exit(1)

# 2. Get Ganoderma data from Supabase
gano = supabase.table('block_pest_disease').select('*').eq('block_id', block_id).execute()
if len(gano.data) > 0:
    gano_data = gano.data[0]
    print(f"\nGanoderma data in Supabase:")
    print(f"  pct_serangan: {gano_data.get('pct_serangan')}")
    print(f"  pct_serangan * 100: {gano_data.get('pct_serangan') * 100}%")
    
    # Show all fields
    print(f"\n  All fields:")
    for key, val in gano_data.items():
        print(f"    {key}: {val}")
else:
    print("\n❌ No Ganoderma data found in block_pest_disease table!")

# 3. Check source Excel
print("\n" + "=" * 80)
print("CHECKING SOURCE FILE: data_gabungan.xlsx")
print("=" * 80)

df = pd.read_excel('source/data_gabungan.xlsx', header=6)

# Find G001A in source - it should be in one of the block columns
# Let's search across all columns
found = False
for col in df.columns:
    if 'G001A' in df[col].astype(str).values:
        row_idx = df[df[col].astype(str).str.contains('G001A', na=False)].index[0]
        print(f"\nFound G001A in column: {col}")
        print(f"Row index: {row_idx}")
        
        # Show surrounding columns to find Ganoderma %
        print(f"\nRow {row_idx} data (first 30 columns):")
        for i, (c, v) in enumerate(df.iloc[row_idx].items()):
            if i < 30:
                print(f"  {c}: {v}")
        
        # Look for Ganoderma column (usually marked as "% GANO" or similar)
        # Based on previous structure, let's check specific pattern
        print(f"\nSearching for Ganoderma % in nearby columns...")
        # Check columns after the block code
        col_idx = df.columns.get_loc(col)
        for offset in range(1, 20):
            if col_idx + offset < len(df.columns):
                next_col = df.columns[col_idx + offset]
                val = df.iloc[row_idx, col_idx + offset]
                if pd.notna(val) and isinstance(val, (int, float)):
                    if 0 <= val <= 100:  # Likely a percentage
                        print(f"  Column {next_col}: {val}")
        
        found = True
        break

if not found:
    print("\n❌ G001A not found in source file!")

# 4. Check normalized CSV files
print("\n" + "=" * 80)
print("CHECKING NORMALIZED CSV FILES")
print("=" * 80)

import glob
csv_files = glob.glob('output/normalized_tables/**/*.csv', recursive=True)
for csv_file in csv_files:
    if 'pest' in csv_file.lower() or 'disease' in csv_file.lower() or 'gano' in csv_file.lower():
        print(f"\nChecking: {csv_file}")
        try:
            df_csv = pd.read_csv(csv_file)
            # Search for block with G001A
            if 'block_id' in df_csv.columns:
                # Need to match block_id, not block_code
                print(f"  Has block_id column, {len(df_csv)} rows")
                # Show first few rows
                if len(df_csv) > 0:
                    print(f"  Sample columns: {df_csv.columns.tolist()}")
        except Exception as e:
            print(f"  Error reading: {e}")
