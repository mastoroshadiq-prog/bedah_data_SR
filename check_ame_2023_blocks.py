"""
CHECK AME 2023 BLOCKS IN SUPABASE
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("CHECKING AME 2023 BLOCKS IN SUPABASE")
print("="*80)

# Load production data
print("\nLoading production_annual data...")
all_prod = []
page = 0
while True:
    start = page * 1000
    end = start + 999
    response = supabase.table('production_annual').select('*').range(start, end).execute()
    if not response.data:
        break
    all_prod.extend(response.data)
    if len(response.data) < 1000:
        break
    page += 1

df_prod = pd.DataFrame(all_prod)
print(f"Total production records: {len(df_prod)}")

# Load blocks
print("Loading blocks table...")
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
print(f"Total blocks in database: {len(df_blocks)}")

# Merge to get block codes
df = df_prod.merge(df_blocks[['id', 'block_code']], 
                   left_on='block_id', right_on='id', 
                   suffixes=('', '_block'), how='left')

# Filter for AME 2023
# AME blocks start with: A, B, C, E, F
df_ame_2023 = df[(df['year'] == 2023) & 
                  (df['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F']))].copy()

print("\n" + "="*80)
print("AME 2023 DATA IN SUPABASE")
print("="*80)

print(f"\nTotal AME 2023 records: {len(df_ame_2023)}")
print(f"Unique blocks: {df_ame_2023['block_code'].nunique()}")

# Summary stats
total_actual = df_ame_2023['real_ton'].sum()
total_target = df_ame_2023['potensi_ton'].sum()
total_gap = total_actual - total_target

print(f"\nProduction Summary:")
print(f"  Actual: {total_actual:,.2f} Ton")
print(f"  Target: {total_target:,.2f} Ton")
print(f"  Gap: {total_gap:,.2f} Ton ({total_gap/total_target*100:.1f}%)")

# List all unique block codes
print("\n" + "="*80)
print("LIST OF AME 2023 BLOCKS:")
print("="*80)

blocks_list = sorted(df_ame_2023['block_code'].unique())
print(f"\nTotal unique blocks: {len(blocks_list)}")

# Group by first letter
print("\nBreakdown by prefix:")
for prefix in ['A', 'B', 'C', 'E', 'F']:
    prefix_blocks = [b for b in blocks_list if b.startswith(prefix)]
    if len(prefix_blocks) > 0:
        print(f"  {prefix}xxx: {len(prefix_blocks)} blocks")

# Show all blocks in columns
print("\nAll blocks:")
print("-" * 80)

# Display in columns (5 per row)
for i in range(0, len(blocks_list), 5):
    row = blocks_list[i:i+5]
    print("  " + "  ".join(f"{b:8s}" for b in row))

# Check for blocks with zero or null production
print("\n" + "="*80)
print("DATA QUALITY CHECK:")
print("="*80)

null_actual = df_ame_2023[df_ame_2023['real_ton'].isna()]
null_target = df_ame_2023[df_ame_2023['potensi_ton'].isna()]
zero_actual = df_ame_2023[df_ame_2023['real_ton'] == 0]
zero_target = df_ame_2023[df_ame_2023['potensi_ton'] == 0]

print(f"\nNULL values:")
print(f"  real_ton: {len(null_actual)}")
print(f"  potensi_ton: {len(null_target)}")

print(f"\nZERO values:")
print(f"  real_ton: {len(zero_actual)}")
print(f"  potensi_ton: {len(zero_target)}")

if len(zero_actual) > 0:
    print(f"\nBlocks with ZERO actual production:")
    for _, row in zero_actual.iterrows():
        print(f"  {row['block_code']}: actual=0, target={row['potensi_ton']}")

# Export to CSV
output_file = 'output/AME_2023_blocks_in_supabase.csv'
df_ame_2023[['block_code', 'real_ton', 'potensi_ton', 'id']].sort_values('block_code').to_csv(output_file, index=False)
print(f"\n✓ Exported to: {output_file}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"AME 2023 Blocks in Supabase: {df_ame_2023['block_code'].nunique()}")
print(f"Total Production: {total_actual:,.2f} Ton")
print(f"Data Quality: {'✓ Good' if len(zero_actual) == 0 else f'⚠️  {len(zero_actual)} blocks with zero'}")

print("\nDONE")
