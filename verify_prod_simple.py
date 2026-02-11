import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("PRODUCTION VERIFICATION")
print("="*60)

# Load all production data
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
print(f"\nTotal records: {len(df)}")

# Check each year
print("\nYEAR-BY-YEAR DETAILS:")
print("="*60)

for year in [2023, 2024, 2025]:
    dy = df[df['year'] == year]
    actual = dy['real_ton'].sum()
    target = dy['potensi_ton'].sum()
    gap = actual - target
    gap_pct = (gap / target * 100) if target > 0 else 0
    
    print(f"\n{year}:")
    print(f"  Records: {len(dy)}")
    print(f"  Actual:  {actual:,.2f} Ton")
    print(f"  Target:  {target:,.2f} Ton")
    print(f"  Gap:     {gap:,.2f} Ton")
    print(f"  Gap %%:   {gap_pct:.2f}%%")

# Total
print("\n" + "="*60)
print("TOTAL (ALL YEARS):")
actual_all = df['real_ton'].sum()
target_all = df['potensi_ton'].sum()
gap_all = actual_all - target_all
print(f"  Actual: {actual_all:,.2f} Ton")
print(f"  Target: {target_all:,.2f} Ton")
print(f"  Gap:    {gap_all:,.2f} Ton")

# User's manual numbers
print("\n" + "="*60)
print("COMPARISON WITH MANUAL COUNT:")
print("="*60)

user_2023_actual = 141984
user_2023_target = 188208
my_2023_actual = df[df['year'] == 2023]['real_ton'].sum()
my_2023_target = df[df['year'] == 2023]['potensi_ton'].sum()

print(f"\n2023 ACTUAL:")
print(f"  Manual:     {user_2023_actual:,} Ton")
print(f"  DB Query:   {my_2023_actual:,.2f} Ton")
print(f"  Diff:       {user_2023_actual - my_2023_actual:,.2f} Ton")

print(f"\n2023 TARGET:")
print(f"  Manual:     {user_2023_target:,} Ton")
print(f"  DB Query:   {my_2023_target:,.2f} Ton")
print(f"  Diff:       {user_2023_target - my_2023_target:,.2f} Ton")

# Check for data quality issues
print("\n" + "="*60)
print("DATA QUALITY CHECK:")
print("="*60)
print(f"Null real_ton: {df['real_ton'].isna().sum()}")
print(f"Null potensi_ton: {df['potensi_ton'].isna().sum()}")
print(f"Zero real_ton: {(df['real_ton'] == 0).sum()}")
print(f"Zero potensi_ton: {(df['potensi_ton'] == 0).sum()}")

# Check very small values
small_vals = df[(df['real_ton'] < 0.1) | (df['potensi_ton'] < 0.1)]
if len(small_vals) > 0:
    print(f"\nRecords with values < 0.1: {len(small_vals)}")
    print("Top 5:")
    for idx, row in small_vals.head(5).iterrows():
        print(f"  Year {row['year']}, Block {row['block_id']}: real={row['real_ton']:.4f}, target={row['potensi_ton']:.4f}")

print("\nDONE")
