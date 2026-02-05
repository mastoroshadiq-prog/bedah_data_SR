from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("BLOCK-DIVISION MAPPING STATUS")
print("=" * 80)

# Get blocks and divisions
blocks = supabase.table('blocks').select('id, block_code, division_id').execute()
df_blocks = pd.DataFrame(blocks.data)

divisions = supabase.table('divisions').select('*').execute()
df_divs = pd.DataFrame(divisions.data)

# Stats
total_blocks = len(df_blocks)
assigned = df_blocks['division_id'].notna().sum()
unassigned = total_blocks - assigned

print(f"\nTotal blocks: {total_blocks}")
print(f"Assigned to division: {assigned} ({assigned/total_blocks*100:.1f}%)")
print(f"NOT assigned (NULL): {unassigned} ({unassigned/total_blocks*100:.1f}%)")

# Check assigned blocks per division
if assigned > 0:
    print("\n" + "=" * 80)
    print("BLOCKS PER DIVISION")
    print("=" * 80)
    
    df_assigned = df_blocks[df_blocks['division_id'].notna()].merge(
        df_divs[['id', 'division_code']], 
        left_on='division_id', 
        right_on='id',
        suffixes=('_block', '_div')
    )
    
    div_counts = df_assigned.groupby('division_code').size().sort_index()
    for div, count in div_counts.items():
        print(f"{div}: {count} blocks")

# Sample unassigned blocks
if unassigned > 0:
    print("\n" + "=" * 80)
    print("SAMPLE UNASSIGNED BLOCKS (first 30)")
    print("=" * 80)
    
    unassigned_blocks = df_blocks[df_blocks['division_id'].isna()]['block_code'].head(30)
    for code in unassigned_blocks:
        print(f"  {code}")

print("\n" + "=" * 80)
print("QUESTION FOR USER")
print("=" * 80)
print("\nApakah ada PATTERN atau RULE untuk assign blocks ke divisions?")
print("Contoh:")
print("  - Block code A001A, A002A, A003A → AME001")
print("  - Block code A004A, A005A, A006A → AME002")
print("  - dll")
print("\nAtau perlu MANUAL MAPPING per block?")
