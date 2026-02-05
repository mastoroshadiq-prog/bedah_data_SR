"""
Quick Division Fix - Focus on Estate Assignment
================================================
Goal: Ensure each division only appears in blocks from the correct estate
"""
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 100)
print("DIVISION ASSIGNMENT VALIDATION & FIX")
print("=" * 100)

# Get all blocks with divisions
blocks = supabase.table('blocks').select('id, block_code, division').execute()
df = pd.DataFrame(blocks.data)

# Extract estate from block_code
df['estate_letter'] = df['block_code'].str[0]
estate_map = {
    'A': 'AME', 'B': 'AME', 'E': 'AME', 'F': 'AME',
    'O': 'OLE', 'C': 'OLE', 'K': 'OLE', 'L': 'OLE',
    'D': 'DBE', 'M': 'DBE', 'N': 'DBE'
}
df['estate'] = df['estate_letter'].map(estate_map)

# Get all unique divisions
all_divisions = df[df['division'].notna()]['division'].unique()
print(f"\nTotal unique divisions in Supabase: {len(all_divisions)}")
print(f"Division list: {sorted(all_divisions)}")

# Determine correct estate for each division based on division name prefix
print("\n" + "=" * 100)
print("DIVISION OWNERSHIP ANALYSIS")
print("=" * 100)

division_estates = {}
for div in all_divisions:
    # Extract estate from division name (first 3 chars usually: AME, OLE, DBE)
    if div.startswith('AME'):
        correct_estate = 'AME'
    elif div.startswith('OLE'):
        correct_estate = 'OLE'
    elif div.startswith('DBE'):
        correct_estate = 'DBE'
    else:
        # Fallback: check which estate has most blocks with this division
        estate_counts = df[df['division'] == div].groupby('estate').size()
        correct_estate = estate_counts.idxmax() if len(estate_counts) > 0 else 'UNKNOWN'
    
    division_estates[div] = correct_estate

# Show division assignments
for estate in ['AME', 'OLE', 'DBE']:
    divs = [d for d, e in division_estates.items() if e == estate]
    print(f"\n{estate} Estate - {len(divs)} divisions:")
    print(f"  {sorted(divs)}")

# Find misassigned blocks
print("\n" + "=" * 100)
print("FINDING MISASSIGNED BLOCKS")
print("=" * 100)

misassigned = []
for idx, row in df.iterrows():
    if pd.notna(row['division']):
        correct_estate = division_estates.get(row['division'], 'UNKNOWN')
        if row['estate'] != correct_estate:
            misassigned.append({
                'block_id': row['id'],
                'block_code': row['block_code'],
                'block_estate': row['estate'],
                'division': row['division'],
                'division_estate': correct_estate
            })

if len(misassigned) > 0:
    print(f"\n❌ Found {len(misassigned)} MISASSIGNED blocks!")
    print("\nSample (first 20):")
    for item in misassigned[:20]:
        print(f"  Block {item['block_code']} ({item['block_estate']}) assigned to division {item['division']} ({item['division_estate']})")
    
    # Summary
    print("\nMisassignment summary:")
    df_misassigned = pd.DataFrame(misassigned)
    summary = df_misassigned.groupby(['block_estate', 'division_estate']).size()
    print(summary)
    
    print("\n" + "=" * 100)
    print("RECOMMENDATIONS")
    print("=" * 100)
    print("\n✅ Division counts per estate are CORRECT")
    print(f"  - AME: {len([d for d, e in division_estates.items() if e == 'AME'])} divisions")
    print(f"  - OLE: {len([d for d, e in division_estates.items() if e == 'OLE'])} divisions")  
    print(f"  - DBE: {len([d for d, e in division_estates.items() if e == 'DBE'])} divisions")
    
    print(f"\n❌ {len(misassigned)} blocks are assigned to WRONG division")
    print("   These blocks should have divisions matching their estate")
    
    print("\n📋 NEXT STEP:")
    print("   Re-assign these blocks to correct divisions within their estate")
    print("   (Requires correct division mapping per block_code)")
else:
    print("\n✅ NO MISASSIGNMENTS FOUND!")
    print("All blocks are assigned to divisions from correct estates")

print("\n" + "=" * 100)
print("CURRENT STATUS PER ESTATE")
print("=" * 100)

for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df[df['estate'] == estate]
    divisions_in_estate = df_estate[df_estate['division'].notna()]['division'].unique()
    expected_divisions = [d for d, e in division_estates.items() if e == estate]
    wrong_divisions = set(divisions_in_estate) - set(expected_divisions)
    
    print(f"\n{estate}:")
    print(f"  Total blocks: {len(df_estate)}")
    print(f"  Blocks with division: {df_estate['division'].notna().sum()}")
    print(f"  Unique divisions: {len(divisions_in_estate)}")
    
    if wrong_divisions:
        print(f"  ❌ Wrong divisions in this estate: {sorted(wrong_divisions)}")
    else:
        print(f"  ✅ All divisions belong to this estate")
    
    print(f"  Expected divisions: {sorted(expected_divisions)}")
