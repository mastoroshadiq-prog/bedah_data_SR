import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

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

# Load blocks & infrastructure
df_blocks = pd.DataFrame(supabase.table('blocks').select('*').execute().data)
df_infra = pd.DataFrame(supabase.table('block_land_infrastructure').select('*').execute().data)

# Merge
df = df_prod.merge(df_blocks[['id', 'block_code']].rename(columns={'id': 'blocks_id'}), 
                   left_on='block_id', right_on='blocks_id', how='left')
df = df.merge(df_infra[['block_id', 'total_luas_sd_2025_ha']], on='block_id', how='left')

# Calculate
df['gap_pct_ton'] = ((df['real_ton'] - df['potensi_ton']) / df['potensi_ton'] * 100)

print("KEY PERFORMANCE INDICATORS VERIFICATION")
print("="*60)

# 1. Total Area
total_area = df['total_luas_sd_2025_ha'].sum()
print(f"\n1. TOTAL AREA: {total_area:,.0f} Ha")
print(f"   Dashboard: 29,474 Ha")
print(f"   Match: {abs(total_area - 29474) < 1}")

# 2. Production Actual
actual = df['real_ton'].sum()
target = df['potensi_ton'].sum()
achievement = (actual / target * 100)
print(f"\n2. PRODUCTION ACTUAL: {actual:,.0f} Ton")
print(f"   Achievement: {achievement:.1f}%")
print(f"   Dashboard: 418,134 Ton (74.0%)")
print(f"   Match: {abs(actual - 418134) < 1}")

# 3. Production Gap
gap = actual - target
gap_pct = (gap / target * 100)
print(f"\n3. PRODUCTION GAP: {gap:,.0f} Ton ({gap_pct:.1f}%)")
print(f"   Dashboard: -146,644 Ton (-26.0%)")
print(f"   Match: {abs(gap - (-146644)) < 1}")

# 4. Risk Exposure
critical = len(df[df['gap_pct_ton'] < -20])
high_risk = len(df[(df['gap_pct_ton'] >= -20) & (df['gap_pct_ton'] < -10)])
total_risk = critical + high_risk
risk_pct = (total_risk / len(df) * 100)
print(f"\n4. RISK EXPOSURE: {total_risk} blocks ({risk_pct:.1f}%)")
print(f"   Critical (<-20%): {critical}")
print(f"   High Risk (-20 to -10%): {high_risk}")
print(f"   Dashboard: 1335 Blocks (69.7%)")
print(f"   Match: {abs(total_risk - 1335) < 1}")

print("\n" + "="*60)
print("BY YEAR:")
for year in sorted(df['year'].unique()):
    dy = df[df['year'] == year]
    print(f"  {year}: {dy['real_ton'].sum():,.0f} Ton (Gap: {dy['real_ton'].sum() - dy['potensi_ton'].sum():,.0f})")

print("\nDONE!")
