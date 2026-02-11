import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("DETAILED PRODUCTION VERIFICATION - ALL YEARS")
print("="*80)

# Load ALL production data
print("\nLoading production_annual data...")
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

df = pd.DataFrame(all_data)
print(f"Total records loaded: {len(df)}")
print(f"Years in data: {sorted(df['year'].unique())}")

# Check for any NULL or invalid values
print("\n" + "="*80)
print("DATA QUALITY CHECK")
print("="*80)

print(f"\nNull values in real_ton: {df['real_ton'].isna().sum()}")
print(f"Null values in potensi_ton: {df['potensi_ton'].isna().sum()}")
print(f"Zero values in real_ton: {(df['real_ton'] == 0).sum()}")
print(f"Zero values in potensi_ton: {(df['potensi_ton'] == 0).sum()}")

# Also check for very small values that might be data errors
print(f"\nVery small real_ton (< 0.01): {(df['real_ton'] < 0.01).sum()}")
print(f"Very small potensi_ton (< 0.01): {(df['potensi_ton'] < 0.01).sum()}")

print("\n" + "="*80)
print("YEAR-BY-YEAR BREAKDOWN (ALL DATA - NO FILTERING)")
print("="*80)

total_actual_all = 0
total_target_all = 0

for year in sorted(df['year'].unique()):
    df_year = df[df['year'] == year]
    
    actual_sum = df_year['real_ton'].sum()
    target_sum = df_year['potensi_ton'].sum()
    gap = actual_sum - target_sum
    gap_pct = (gap / target_sum * 100) if target_sum > 0 else 0
    achievement = (actual_sum / target_sum * 100) if target_sum > 0 else 0
    
    total_actual_all += actual_sum
    total_target_all += target_sum
    
    print(f"\n{year}:")
    print(f"  Records: {len(df_year)}")
    print(f"  Actual Production: {actual_sum:,.2f} Ton")
    print(f"  Target Production: {target_sum:,.2f} Ton")
    print(f"  Gap: {gap:,.2f} Ton ({gap_pct:+.2f}%)")
    print(f"  Achievement: {achievement:.2f}%")
    
    # Show sample records
    print(f"\n  Sample records (first 5):")
    for idx, row in df_year.head(5).iterrows():
        print(f"    Block {row['block_id']}: actual={row['real_ton']:.2f}, target={row['potensi_ton']:.2f}")

print("\n" + "="*80)
print("TOTAL ACROSS ALL YEARS")
print("="*80)
print(f"\nTotal Actual: {total_actual_all:,.2f} Ton")
print(f"Total Target: {total_target_all:,.2f} Ton")
print(f"Total Gap: {total_actual_all - total_target_all:,.2f} Ton")
print(f"Overall Achievement: {(total_actual_all/total_target_all*100):.2f}%")

print("\n" + "="*80)
print("COMPARISON WITH USER'S MANUAL CALCULATION")
print("="*80)

user_2023_actual = 141984
user_2023_target = 188208

my_2023_actual = df[df['year'] == 2023]['real_ton'].sum()
my_2023_target = df[df['year'] == 2023]['potensi_ton'].sum()

print(f"\n2023 - Actual Production:")
print(f"  User's manual count: {user_2023_actual:,} Ton")
print(f"  My calculation: {my_2023_actual:,.2f} Ton")
print(f"  Difference: {user_2023_actual - my_2023_actual:,.2f} Ton")

print(f"\n2023 - Target Production:")
print(f"  User's manual count: {user_2023_target:,} Ton")
print(f"  My calculation: {my_2023_target:,.2f} Ton")
print(f"  Difference: {user_2023_target - my_2023_target:,.2f} Ton")

if abs(user_2023_actual - my_2023_actual) > 100:
    print(f"\n⚠️  SIGNIFICANT DIFFERENCE DETECTED!")
    print(f"   Checking for missing records or data quality issues...")
    
    # Check if there are any records with very different values
    df_2023 = df[df['year'] == 2023]
    print(f"\n   2023 Statistics:")
    print(f"   Min actual: {df_2023['real_ton'].min():.2f}")
    print(f"   Max actual: {df_2023['real_ton'].max():.2f}")
    print(f"   Mean actual: {df_2023['real_ton'].mean():.2f}")
    print(f"   Median actual: {df_2023['real_ton'].median():.2f}")

# Check estate breakdown
print("\n" + "="*80)
print("BREAKDOWN BY ESTATE (2023)")
print("="*80)

# Load blocks to get estate info
df_blocks = pd.DataFrame(supabase.table('blocks').select('*').execute().data)
df_full = df.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', how='left')

df_2023 = df_full[df_full['year'] == 2023]
df_2023['estate_code'] = df_2023['block_code'].str[0]
estate_map = {'A': 'AME', 'O': 'OLE', 'D': 'DBE', 'B': 'AME', 'E': 'AME', 
              'F': 'AME', 'K': 'OLE', 'L': 'OLE', 'M': 'DBE', 'N': 'DBE'}
df_2023['estate'] = df_2023['estate_code'].map(estate_map)

for estate in ['AME', 'OLE', 'DBE']:
    df_est = df_2023[df_2023['estate'] == estate]
    if len(df_est) > 0:
        actual = df_est['real_ton'].sum()
        target = df_est['potensi_ton'].sum()
        print(f"\n{estate}:")
        print(f"  Blocks: {len(df_est)}")
        print(f"  Actual: {actual:,.2f} Ton")
        print(f"  Target: {target:,.2f} Ton")

print("\n" + "="*80)
print("CHECKING FOR POTENTIAL DATA ISSUES")
print("="*80)

# Check if there are records where values seem too small (might be in different units)
df_small = df[(df['real_ton'] < 1) | (df['potensi_ton'] < 1)]
if len(df_small) > 0:
    print(f"\n⚠️  Found {len(df_small)} records with values < 1 Ton")
    print(f"   These might be in different units (e.g., kg instead of ton)")
    print(f"\n   Sample:")
    for idx, row in df_small.head(10).iterrows():
        print(f"   Year {row['year']}, Block {row['block_id']}: actual={row['real_ton']}, target={row['potensi_ton']}")

print("\n" + "="*80)
print("FINAL VERIFIED NUMBERS")
print("="*80)

for year in [2023, 2024, 2025]:
    dy = df[df['year'] == year]
    actual = dy['real_ton'].sum()
    target = dy['potensi_ton'].sum()
    gap = actual - target
    
    print(f"\n{year}:")
    print(f"  Actual: {actual:,.2f} Ton")
    print(f"  Target: {target:,.2f} Ton")
    print(f"  Gap: {gap:,.2f} Ton ({gap/target*100:.2f}%)")

print("\n" + "="*80)
print("DONE - Please verify these numbers against your manual calculation")
print("="*80)
