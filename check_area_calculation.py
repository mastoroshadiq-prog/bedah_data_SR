import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECKING TOTAL AREA CALCULATION")
print("="*70)

# Load production data
all_data = []
page = 0
while True:
    start = page * 1000
    end = start + 999
    response = supabase.table('production_annual').select('*').range(start, end).execute()
    if not response.data:
        break
    all_data.extend(response.data)
    if len(response.data) < 1000:
        break
    page += 1

df_prod = pd.DataFrame(all_data)
print(f"\n1. Production records: {len(df_prod)}")
print(f"   Years: {sorted(df_prod['year'].unique())}")

# Load infrastructure
df_infra = pd.DataFrame(supabase.table('block_land_infrastructure').select('*').execute().data)
print(f"\n2. Infrastructure records: {len(df_infra)}")

# Merge
df = df_prod.merge(df_infra[['block_id', 'total_luas_sd_2025_ha']], on='block_id', how='left')

print(f"\n3. WRONG METHOD (Current Dashboard - SUM across all years):")
total_area_wrong = df['total_luas_sd_2025_ha'].sum()
print(f"   = SUM all records with area")
print(f"   = {total_area_wrong:,.0f} Ha")
print(f"   This is WRONG because it counts each block 3 times (2023, 2024, 2025)")

print(f"\n4. CORRECT METHOD (Should only count unique blocks):")
# Get unique blocks
unique_blocks = df_infra['block_id'].nunique()
print(f"   Unique blocks: {unique_blocks}")

# Method A: Direct from infrastructure table
total_area_correct_A = df_infra['total_luas_sd_2025_ha'].sum()
print(f"\n   Method A - Direct from infrastructure table:")
print(f"   = SUM(total_luas_sd_2025_ha) from block_land_infrastructure")
print(f"   = {total_area_correct_A:,.2f} Ha")

# Method B: From merged data but deduplicated
df_unique = df.drop_duplicates(subset=['block_id'])
total_area_correct_B = df_unique['total_luas_sd_2025_ha'].sum()
print(f"\n   Method B - Deduplicated merged data:")
print(f"   = SUM(total_luas_sd_2025_ha) for unique blocks only")
print(f"   = {total_area_correct_B:,.2f} Ha")

print(f"\n5. VERIFICATION:")
print(f"   Dashboard shows: 29,474 Ha")
print(f"   Wrong calculation: {total_area_wrong:,.0f} Ha")
print(f"   Correct should be: {total_area_correct_A:,.2f} Ha")
print(f"   Difference: {total_area_wrong - total_area_correct_A:,.2f} Ha")

# Check if wrong is 3x correct (because 3 years)
ratio = total_area_wrong / total_area_correct_A if total_area_correct_A > 0 else 0
print(f"\n   Ratio (wrong/correct): {ratio:.2f}x")
if 2.9 < ratio < 3.1:
    print(f"   ✓ CONFIRMED: Area is being counted 3x (once per year)!")

print("\n" + "="*70)
print("CORRECT TOTAL AREA BY ESTATE:")
print("="*70)

# Load blocks to get estate mapping
df_blocks = pd.DataFrame(supabase.table('blocks').select('*').execute().data)
df_full = df_infra.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', how='left')

# Extract estate code
df_full['estate_code'] = df_full['block_code'].str[0]
estate_map = {'A': 'AME', 'O': 'OLE', 'D': 'DBE', 'B': 'AME', 'E': 'AME', 
              'F': 'AME', 'K': 'OLE', 'L': 'OLE', 'M': 'DBE', 'N': 'DBE'}
df_full['estate'] = df_full['estate_code'].map(estate_map)

# Calculate by estate
for estate in ['AME', 'OLE', 'DBE']:
    estate_area = df_full[df_full['estate'] == estate]['total_luas_sd_2025_ha'].sum()
    estate_blocks = len(df_full[df_full['estate'] == estate])
    print(f"\n{estate}:")
    print(f"  Total Area: {estate_area:,.2f} Ha")
    print(f"  Blocks: {estate_blocks}")

print("\n" + "="*70)
print("SUMMARY:")
print("  CURRENT DASHBOARD = WRONG (counts 3x)")
print("  SHOULD USE = SUM from block_land_infrastructure (unique blocks only)")
print("="*70)
