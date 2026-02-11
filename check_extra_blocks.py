import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("CHECKING 60 EXTRA BLOCKS IN SUPABASE")
print("="*60)

# Load Excel
df_excel = pd.read_excel('source/data_produksi_AME_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)
df_excel = df_excel.dropna(subset=['BLOCK'])

excel_blocks = set(df_excel['BLOCK'].unique())
print(f"\nExcel blocks: {len(excel_blocks)}")

# Load Supabase
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
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)

df = df_prod.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', suffixes=('', '_b'), how='left')
df_ame = df[(df['year'] == 2023) & (df['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F']))]

supabase_blocks = set(df_ame['block_code'].unique())
print(f"Supabase AME 2023 blocks: {len(supabase_blocks)}")

# Find extras
extra_in_supabase = supabase_blocks - excel_blocks
missing_in_supabase = excel_blocks - supabase_blocks

print(f"\n{'='*60}")
print(f"EXTRA BLOCKS IN SUPABASE (not in Excel): {len(extra_in_supabase)}")
print(f"{'='*60}")

if extra_in_supabase:
    # Analyze by prefix
    by_prefix = {}
    for block in extra_in_supabase:
        prefix = block[0]
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append(block)
    
    print(f"\nBreakdown by prefix:")
    for prefix in sorted(by_prefix.keys()):
        blocks = by_prefix[prefix]
        estate = 'AME' if prefix in ['A','B','C','E','F'] else 'OTHER'
        print(f"  {prefix}xxx ({estate}): {len(blocks)} blocks")
    
    print(f"\nList of extra blocks:")
    for prefix in sorted(by_prefix.keys()):
        blocks = sorted(by_prefix[prefix])
        print(f"\n  {prefix}xxx blocks ({len(blocks)}):")
        for i in range(0, len(blocks), 5):
            row = blocks[i:i+5]
            print(f"    {', '.join(row)}")

print(f"\n{'='*60}")
print(f"MISSING IN SUPABASE (in Excel but not DB): {len(missing_in_supabase)}")
print(f"{'='*60}")

if missing_in_supabase:
    print("\nList:")
    for block in sorted(missing_in_supabase)[:20]:
        print(f"  - {block}")
    if len(missing_in_supabase) > 20:
        print(f"  ... and {len(missing_in_supabase) - 20} more")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")

all_prefixes_extra = set(b[0] for b in extra_in_supabase)
if all_prefixes_extra.issubset({'A', 'B', 'C', 'E', 'F'}):
    print("\n✓ ALL 60 extra blocks are AME blocks")
    print("  (Prefix: A, B, C, E, or F)")
else:
    non_ame = [b for b in extra_in_supabase if b[0] not in ['A','B','C','E','F']]
    if non_ame:
        print(f"\n⚠️  Some extra blocks are NOT AME:")
        print(f"  Non-AME blocks: {non_ame}")
    else:
        print("\n✓ ALL extra blocks are AME")

print("\nDONE")
