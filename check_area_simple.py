import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("AREA CALCULATION CHECK")
print("="*70)

# Method 1: Direct from infrastructure (CORRECT)
df_infra = pd.DataFrame(supabase.table('block_land_infrastructure').select('*').execute().data)
total_area_correct = df_infra['total_luas_sd_2025_ha'].sum()
unique_blocks = len(df_infra)

print(f"\nCORRECT METHOD:")
print(f"  Source: block_land_infrastructure table")
print(f"  Unique blocks: {unique_blocks}")
print(f"  Total Area (SD 2025): {total_area_correct:,.2f} Ha")

# Method 2: What dashboard currently does (merge with production - WRONG if not deduped)
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
df_merged = df_prod.merge(df_infra[['block_id', 'total_luas_sd_2025_ha']], on='block_id', how='left')

total_area_if_sum_all = df_merged['total_luas_sd_2025_ha'].sum()
total_records = len(df_merged)

print(f"\nWRONG METHOD (if summing all records):")
print(f"  Total records after merge: {total_records}")
print(f"  Years in production: {sorted(df_prod['year'].unique())}")
print(f"  If we SUM all: {total_area_if_sum_all:,.2f} Ha")
print(f"  Ratio: {total_area_if_sum_all / total_area_correct:.1f}x")

print(f"\nDASHBOARD SHOWS: 29,474 Ha")
print(f"CORRECT VALUE: {total_area_correct:,.2f} Ha")

if abs(total_area_if_sum_all - 29474) < 1:
    print(f"\n⚠️  PROBLEM CONFIRMED!")
    print(f"    Dashboard is summing area across ALL years")
    print(f"    This counts each block 3 times (2023, 2024, 2025)")
    print(f"    Should only count unique blocks once!")
else:
    print(f"\n✓  Dashboard calculation seems correct")

print("\n" + "="*70)
