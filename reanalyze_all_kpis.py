"""
COMPREHENSIVE KPI RE-ANALYSIS
After fixing Total Area calculation, verify all other KPIs
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("COMPREHENSIVE KPI RE-ANALYSIS")
print("="*80)

# Load all data
print("\nLoading data...")
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
df_blocks = pd.DataFrame(supabase.table('blocks').select('*').execute().data)
df_infra = pd.DataFrame(supabase.table('block_land_infrastructure').select('*').execute().data)

# Merge
df = df_prod.merge(
    df_blocks[['id', 'block_code']].rename(columns={'id': 'blocks_id'}), 
    left_on='block_id', right_on='blocks_id', how='left'
)
df = df.merge(df_infra[['block_id', 'total_luas_sd_2025_ha']], on='block_id', how='left')

# Calculate gap percentage
df['gap_pct_ton'] = ((df['real_ton'] - df['potensi_ton']) / df['potensi_ton'] * 100)

print(f"Loaded {len(df)} production records")
print(f"Years: {sorted(df['year'].unique())}")
print(f"Unique blocks: {df['block_id'].nunique()}")

print("\n" + "="*80)
print("1. TOTAL AREA (FIXED)")
print("="*80)

# Deduplicate blocks
df_unique = df.drop_duplicates(subset=['block_id'])
total_area_correct = df_unique['total_luas_sd_2025_ha'].sum()
total_area_wrong = df['total_luas_sd_2025_ha'].sum()

print(f"\nWRONG (before fix): {total_area_wrong:,.2f} Ha")
print(f"  → Counted each block 3x (2023, 2024, 2025)")
print(f"\nCORRECT (after fix): {total_area_correct:,.2f} Ha")
print(f"  → Counts unique blocks only")
print(f"\nDifference: {total_area_wrong - total_area_correct:,.2f} Ha removed")

print("\n" + "="*80)
print("2. PRODUCTION ACTUAL (No change - already correct)")
print("="*80)

actual_total = df['real_ton'].sum()
target_total = df['potensi_ton'].sum()
achievement = (actual_total / target_total * 100)

print(f"\nTotal Production Actual: {actual_total:,.0f} Ton")
print(f"Total Production Target: {target_total:,.0f} Ton")
print(f"Achievement: {achievement:.1f}% of target")

print("\nBreakdown by Year:")
for year in sorted(df['year'].unique()):
    dy = df[df['year'] == year]
    actual_y = dy['real_ton'].sum()
    target_y = dy['potensi_ton'].sum()
    gap_y = actual_y - target_y
    ach_y = (actual_y / target_y * 100) if target_y > 0 else 0
    print(f"  {year}: {actual_y:,} Ton (Target: {target_y:,}, Gap: {gap_y:+,}, {ach_y:.1f}%)")

print("\nVERIFICATION:")
print(f"  Dashboard shows: 418,134 Ton (74.0%)")
print(f"  Calculated: {actual_total:,.0f} Ton ({achievement:.1f}%)")
print(f"  ✓ Match: {abs(actual_total - 418134) < 1}")

print("\n" + "="*80)
print("3. PRODUCTION GAP (No change - already correct)")
print("="*80)

total_gap = actual_total - target_total
gap_pct = (total_gap / target_total * 100)

print(f"\nProduction Gap: {total_gap:,.0f} Ton")
print(f"Gap Percentage: {gap_pct:.1f}%")
print(f"\nInterpretation:")
print(f"  • We are {abs(gap_pct):.1f}% BELOW target")
print(f"  • OR achieving only {achievement:.1f}% of target")
print(f"  • These are two sides of same metric: {achievement:.1f}% + {abs(gap_pct):.1f}% = 100%")

print("\nBreakdown by Year:")
for year in sorted(df['year'].unique()):
    dy = df[df['year'] == year]
    gap_y = dy['real_ton'].sum() - dy['potensi_ton'].sum()
    gap_pct_y = (gap_y / dy['potensi_ton'].sum() * 100) if dy['potensi_ton'].sum() > 0 else 0
    print(f"  {year}: {gap_y:+,} Ton ({gap_pct_y:+.1f}%)")

print("\nVERIFICATION:")
print(f"  Dashboard shows: -146,644 Ton (-26.0%)")
print(f"  Calculated: {total_gap:,.0f} Ton ({gap_pct:.1f}%)")
print(f"  ✓ Match: {abs(total_gap - (-146644)) < 1}")

print("\n" + "="*80)
print("4. RISK EXPOSURE (Needs verification)")
print("="*80)

# Count risk blocks
critical = len(df[df['gap_pct_ton'] < -20])
high_risk = len(df[(df['gap_pct_ton'] >= -20) & (df['gap_pct_ton'] < -10)])
medium_risk = len(df[(df['gap_pct_ton'] >= -10) & (df['gap_pct_ton'] < -5)])
low_risk = len(df[df['gap_pct_ton'] >= -5])
total_risk = critical + high_risk
total_records = len(df)

print(f"\nRisk Classification (per RECORD):")
print(f"  Critical (< -20%): {critical:,} records")
print(f"  High Risk (-20% to -10%): {high_risk:,} records")
print(f"  Medium Risk (-10% to -5%): {medium_risk:,} records")
print(f"  Low Risk (>= -5%): {low_risk:,} records")
print(f"  ---")
print(f"  Total RISK (Critical + High): {total_risk:,} records")
print(f"  Total Records: {total_records:,}")
print(f"  Risk %: {total_risk/total_records*100:.1f}%")

print(f"\n⚠️  ISSUE IDENTIFIED:")
print(f"  Dashboard counts RECORDS (includes duplicates across years)")
print(f"  Should we count UNIQUE BLOCKS instead?")

# Count unique blocks
df['is_risk'] = df['gap_pct_ton'] < -10
df['is_critical'] = df['gap_pct_ton'] < -20
df['is_high_risk'] = (df['gap_pct_ton'] >= -20) & (df['gap_pct_ton'] < -10)

# Method A: Count records (current dashboard)
risk_records = len(df[df['is_risk']])
risk_pct_records = (risk_records / len(df) * 100)

# Method B: Count unique blocks
unique_blocks = df['block_id'].nunique()
risk_blocks_unique = df[df['is_risk']]['block_id'].nunique()
risk_pct_unique = (risk_blocks_unique / unique_blocks * 100)

print(f"\nMETHOD A - Count Records (current):")
print(f"  Risk records: {risk_records:,}")
print(f"  Total records: {len(df):,}")
print(f"  Risk %: {risk_pct_records:.1f}%")

print(f"\nMETHOD B - Count Unique Blocks (proposed):")
print(f"  Risk blocks: {risk_blocks_unique}")
print(f"  Total unique blocks: {unique_blocks}")
print(f"  Risk %: {risk_pct_unique:.1f}%")

print(f"\nDashboard shows: 1335 Blocks (69.7%)")
print(f"Method A result: {risk_records} records ({risk_pct_records:.1f}%)")
print(f"Method B result: {risk_blocks_unique} blocks ({risk_pct_unique:.1f}%)")

if abs(risk_records - 1335) < 5:
    print(f"\n✓ Dashboard is using Method A (counting records)")
    print(f"  This means same block counted 3x if it's at risk in all 3 years")
elif abs(risk_blocks_unique - 1335) < 5:
    print(f"\n✓ Dashboard is using Method B (counting unique blocks)")
    print(f"  This is the correct approach for portfolio-level metrics")

# Analyze year-by-year
print(f"\n" + "="*80)
print("RISK BREAKDOWN BY YEAR:")
print("="*80)
for year in sorted(df['year'].unique()):
    dy = df[df['year'] == year]
    risk_y = len(dy[dy['is_risk']])
    total_y = len(dy)
    risk_pct_y = (risk_y / total_y * 100)
    print(f"\n{year}:")
    print(f"  Risk records: {risk_y} / {total_y} ({risk_pct_y:.1f}%)")
    print(f"  Critical: {len(dy[dy['is_critical']])}")
    print(f"  High Risk: {len(dy[dy['is_high_risk']])}")

print("\n" + "="*80)
print("SUMMARY & RECOMMENDATIONS")
print("="*80)

print(f"""
✅ FIXED:
   Total Area: {total_area_wrong:,.0f} Ha → {total_area_correct:,.0f} Ha
   (Removed duplicate counting)

✓ CORRECT (No change needed):
   Production Actual: {actual_total:,.0f} Ton ({achievement:.1f}%)
   Production Gap: {total_gap:,.0f} Ton ({gap_pct:.1f}%)

⚠️  NEEDS CLARIFICATION:
   Risk Exposure: Currently {risk_records} records ({risk_pct_records:.1f}%)
   
   QUESTION: Should we count unique blocks instead?
   If YES → {risk_blocks_unique} blocks ({risk_pct_unique:.1f}%)
   If NO → Keep {risk_records} records ({risk_pct_records:.1f}%)

RECOMMENDATION:
   For consistency with Total Area fix (unique blocks),
   Risk Exposure should also count UNIQUE BLOCKS.
""")

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
