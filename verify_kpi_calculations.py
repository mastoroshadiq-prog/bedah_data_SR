"""
VERIFY KEY PERFORMANCE INDICATORS

Analyzing where the numbers come from:
1. Total Area: 29,474 Ha
2. Production Actual: 418,134 Ton (↑ 74.0% of target)
3. Production Gap: -146,644 Ton (↓ -26.0%)
4. Risk Exposure: 1335 Blocks (↑ 69.7% of portfolio)
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

print("=" * 70)
print("VERIFYING KEY PERFORMANCE INDICATORS")
print("=" * 70)

# Load production data (ALL YEARS)
print("\n1. Loading production_annual data...")
all_data = []
page_size = 1000
page = 0

while True:
    start = page * page_size
    end = start + page_size - 1
    response = supabase.table('production_annual').select('*').range(start, end).execute()
    
    if not response.data:
        break
        
    all_data.extend(response.data)
    
    if len(response.data) < page_size:
        break
        
    page += 1

df_prod = pd.DataFrame(all_data)
print(f"   Loaded {len(df_prod)} production records")

# Load blocks
print("\n2. Loading blocks data...")
response = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(response.data)
print(f"   Loaded {len(df_blocks)} blocks")

# Load infrastructure
print("\n3. Loading infrastructure data...")
response = supabase.table('block_land_infrastructure').select('*').execute()
df_infra = pd.DataFrame(response.data)
print(f"   Loaded {len(df_infra)} infrastructure records")

# Merge data
print("\n4. Merging data...")
df = df_prod.merge(
    df_blocks[['id', 'block_code', 'category']].rename(columns={'id': 'blocks_id'}), 
    left_on='block_id', 
    right_on='blocks_id', 
    how='left',
    suffixes=('_prod', '_block')
)

df = df.merge(df_infra[['block_id', 'total_luas_sd_2025_ha']], 
              on='block_id', how='left')

print(f"   Merged dataframe has {len(df)} records")

# Calculate gap_pct_ton
df['gap_pct_ton'] = ((df['real_ton'] - df['potensi_ton']) / df['potensi_ton'] * 100)

print("\n" + "=" * 70)
print("CALCULATION VERIFICATION (All Years, All Estates)")
print("=" * 70)

# 1. TOTAL AREA
total_area = df['total_luas_sd_2025_ha'].sum()
print(f"\n1. TOTAL AREA")
print(f"   Formula: SUM(total_luas_sd_2025_ha)")
print(f"   Result: {total_area:,.0f} Ha")
print(f"   Dashboard shows: 29,474 Ha")
print(f"   ✓ Match: {abs(total_area - 29474) < 1}")

# 2. PRODUCTION ACTUAL
total_production_actual = df['real_ton'].sum()
print(f"\n2. PRODUCTION ACTUAL")
print(f"   Formula: SUM(real_ton)")
print(f"   Result: {total_production_actual:,.0f} Ton")
print(f"   Dashboard shows: 418,134 Ton")
print(f"   ✓ Match: {abs(total_production_actual - 418134) < 1}")

# 2b. Achievement %
total_production_target = df['potensi_ton'].sum()
achievement_pct = (total_production_actual / total_production_target * 100) if total_production_target > 0 else 0
print(f"\n2b. ACHIEVEMENT %")
print(f"   Formula: (real_ton / potensi_ton) * 100")
print(f"   Actual: {total_production_actual:,.0f} Ton")
print(f"   Target: {total_production_target:,.0f} Ton")
print(f"   Result: {achievement_pct:.1f}%")
print(f"   Dashboard shows: 74.0% of target")
print(f"   ✓ Match: {abs(achievement_pct - 74.0) < 0.5}")

# 3. PRODUCTION GAP
total_gap = total_production_actual - total_production_target
gap_pct = (total_gap / total_production_target * 100)
print(f"\n3. PRODUCTION GAP")
print(f"   Formula: real_ton - potensi_ton")
print(f"   Result: {total_gap:,.0f} Ton")
print(f"   Gap %: {gap_pct:.1f}%")
print(f"   Dashboard shows: -146,644 Ton (-26.0%)")
print(f"   ✓ Match: {abs(total_gap - (-146644)) < 1}")
print(f"   ✓ Gap % Match: {abs(gap_pct - (-26.0)) < 0.5}")

# 4. RISK EXPOSURE
critical_blocks = len(df[df['gap_pct_ton'] < -20])
high_risk_blocks = len(df[(df['gap_pct_ton'] >= -20) & (df['gap_pct_ton'] < -10)])
total_risk_blocks = critical_blocks + high_risk_blocks
total_blocks = len(df)
risk_pct = (total_risk_blocks / total_blocks * 100)

print(f"\n4. RISK EXPOSURE")
print(f"   Formula: COUNT blocks where gap_pct_ton < -10%")
print(f"   Critical (gap < -20%): {critical_blocks} blocks")
print(f"   High Risk (-20% <= gap < -10%): {high_risk_blocks} blocks")
print(f"   Total Risk Blocks: {total_risk_blocks}")
print(f"   Total Blocks: {total_blocks}")
print(f"   Risk %: {risk_pct:.1f}%")
print(f"   Dashboard shows: 1335 Blocks (69.7% of portfolio)")
print(f"   ✓ Match: {abs(total_risk_blocks - 1335) < 1}")
print(f"   ✓ Risk % Match: {abs(risk_pct - 69.7) < 0.5}")

print("\n" + "=" * 70)
print("BREAKDOWN BY YEAR")
print("=" * 70)

for year in sorted(df['year'].unique()):
    df_year = df[df['year'] == year]
    area_year = df_year['total_luas_sd_2025_ha'].sum()
    actual_year = df_year['real_ton'].sum()
    target_year = df_year['potensi_ton'].sum()
    gap_year = actual_year - target_year
    blocks_year = len(df_year)
    
    print(f"\n{year}:")
    print(f"  Area: {area_year:,.0f} Ha")
    print(f"  Actual: {actual_year:,.0f} Ton")
    print(f"  Target: {target_year:,.0f} Ton")
    print(f"  Gap: {gap_year:,.0f} Ton ({gap_year/target_year*100:.1f}%)")
    print(f"  Blocks: {blocks_year}")

print("\n" + "=" * 70)
print("DATA SOURCES")
print("=" * 70)
print("""
1. TOTAL AREA:
   - Table: block_land_infrastructure
   - Column: total_luas_sd_2025_ha
   - Method: SUM of all blocks

2. PRODUCTION ACTUAL:
   - Table: production_annual
   - Column: real_ton
   - Method: SUM of all years' actual production

3. PRODUCTION TARGET:
   - Table: production_annual
   - Column: potensi_ton
   - Method: SUM of all years' potential production

4. PRODUCTION GAP:
   - Formula: real_ton - potensi_ton
   - Gap %: (gap / potensi_ton) * 100

5. RISK EXPOSURE:
   - Formula: gap_pct_ton = ((real_ton - potensi_ton) / potensi_ton) * 100
   - Critical: blocks with gap_pct_ton < -20%
   - High Risk: blocks with -20% <= gap_pct_ton < -10%
   - Total Risk: Critical + High Risk
""")

print("\n✓ Analysis Complete!")
