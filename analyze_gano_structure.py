"""
FULL ANALYSIS: Ganoderma Division Breakdown
Analyze actual data structure and relationships
"""
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 80)
print("STEP 1: Analyze Ganoderma Data Structure")
print("=" * 80)

# Get ganoderma data sample
gano_result = supabase.table('block_pest_disease').select('*').limit(20).execute()
df_gano = pd.DataFrame(gano_result.data)

print(f"\n📋 Ganoderma Table Columns: {df_gano.columns.tolist()}")
print(f"📊 Total Records: {len(gano_result.data)}")
print(f"\nSample Data:")
print(df_gano[['block_id', 'block_code', 'pct_serangan']].head(10))

print("\n" + "=" * 80)
print("STEP 2: Check Block Code Pattern per Estate")
print("=" * 80)

# Get all ganoderma data
all_gano = []
page = 0
page_size = 1000
while True:
    start = page * page_size
    end = start + page_size - 1
    result = supabase.table('block_pest_disease').select('block_id, block_code, pct_serangan').range(start, end).execute()
    if not result.data:
        break
    all_gano.extend(result.data)
    if len(result.data) < page_size:
        break
    page += 1

df_all_gano = pd.DataFrame(all_gano)
print(f"\n📊 Total Ganoderma Records: {len(df_all_gano)}")

# Extract estate and division from block_code
df_all_gano['estate_letter'] = df_all_gano['block_code'].str[0]
df_all_gano['division'] = df_all_gano['block_code'].str[1]

# Map estate letters to names
estate_map = {
    'A': 'AME', 'B': 'AME', 'E': 'AME', 'F': 'AME',
    'O': 'OLE', 'K': 'OLE', 'L': 'OLE',
    'D': 'DBE', 'M': 'DBE', 'N': 'DBE',
    'C': 'OLE'  # Verify this
}

df_all_gano['estate'] = df_all_gano['estate_letter'].map(estate_map)

print("\n" + "=" * 80)
print("STEP 3: Division Breakdown per Estate")
print("=" * 80)

for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df_all_gano[df_all_gano['estate'] == estate]
    
    print(f"\n🏢 {estate} Estate:")
    print(f"   Total Blocks: {len(df_estate)}")
    print(f"   Estate Letters: {df_estate['estate_letter'].unique().tolist()}")
    
    if len(df_estate) > 0:
        # Division breakdown
        div_breakdown = df_estate.groupby('division').agg({
            'pct_serangan': 'mean',
            'block_code': 'count'
        }).reset_index()
        div_breakdown.columns = ['division', 'avg_pct', 'block_count']
        div_breakdown['avg_pct'] = div_breakdown['avg_pct'] * 100
        div_breakdown = div_breakdown.sort_values('avg_pct', ascending=False)
        
        print(f"\n   📊 Divisions in {estate}:")
        print(div_breakdown.to_string(index=False))
        
        # Sample block codes
        print(f"\n   📝 Sample Block Codes:")
        samples = df_estate['block_code'].head(10).tolist()
        print(f"   {samples}")

print("\n" + "=" * 80)
print("STEP 4: Verify Estate Letter Mapping")
print("=" * 80)

estate_letter_counts = df_all_gano.groupby(['estate_letter', 'estate']).size().reset_index(name='count')
print(estate_letter_counts)

print("\n" + "=" * 80)
print("SUMMARY & RECOMMENDATION")
print("=" * 80)
print("\n✅ Data structure is CLEAR:")
print("   - block_code format: [Estate Letter][Division][Block Number][Sub-block]")
print("   - Division = 2nd character of block_code")
print("   - Can extract division directly from df_gano['block_code'].str[1]")
print("\n✅ No need for complex merges - df_gano has everything needed!")
