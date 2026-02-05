"""
Check actual divisions in Supabase for each estate
Compare with source data expectation:
- AME: correct
- OLE: should have 4 divisions
- DBE: should have 5 divisions
"""
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 80)
print("CHECKING DIVISIONS IN SUPABASE")
print("=" * 80)

# Get all blocks with division
blocks_data = supabase.table('blocks').select('id, block_code, division').execute()
df_blocks = pd.DataFrame(blocks_data.data)

print(f"\nTotal blocks in Supabase: {len(df_blocks)}")
print(f"Blocks with division: {df_blocks['division'].notna().sum()}")

# Extract estate from block_code first character
df_blocks['estate_letter'] = df_blocks['block_code'].str[0]

# Map to estate names
estate_map = {
    'A': 'AME', 'B': 'AME', 'E': 'AME', 'F': 'AME',
    'O': 'OLE', 'C': 'OLE', 'K': 'OLE', 'L': 'OLE',
    'D': 'DBE', 'M': 'DBE', 'N': 'DBE'
}

df_blocks['estate'] = df_blocks['estate_letter'].map(estate_map)

print("\n" + "=" * 80)
print("DIVISIONS PER ESTATE")
print("=" * 80)

for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df_blocks[df_blocks['estate'] == estate]
    
    print(f"\n{estate} Estate:")
    print(f"  Total blocks: {len(df_estate)}")
    
    # Get unique divisions (not null)
    divisions = df_estate[df_estate['division'].notna()]['division'].unique()
    print(f"  Unique divisions: {len(divisions)}")
    print(f"  Division list: {sorted(divisions)}")
    
    # Show division breakdown
    if len(divisions) > 0:
        div_counts = df_estate[df_estate['division'].notna()].groupby('division').size()
        print(f"\n  Blocks per division:")
        for div, count in sorted(div_counts.items()):
            print(f"    {div}: {count} blocks")

print("\n" + "=" * 80)
print("SAMPLE BLOCK CODES PER ESTATE")
print("=" * 80)

for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df_blocks[df_blocks['estate'] == estate]
    samples = df_estate[['block_code', 'division']].head(10)
    print(f"\n{estate} samples:")
    print(samples.to_string(index=False))

print("\n" + "=" * 80)
print("EXPECTED vs ACTUAL")
print("=" * 80)
print("\nExpected (from data_gabungan.xlsx):")
print("  AME: correct")
print("  OLE: 4 divisions")
print("  DBE: 5 divisions")
print("\nActual (from Supabase):")
for estate in ['AME', 'OLE', 'DBE']:
    df_estate = df_blocks[df_blocks['estate'] == estate]
    divisions = df_estate[df_estate['division'].notna()]['division'].unique()
    print(f"  {estate}: {len(divisions)} divisions")
