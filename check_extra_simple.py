import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Load Excel
df_excel = pd.read_excel('source/data_produksi_AME_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)
df_excel = df_excel.dropna(subset=['BLOCK'])
excel_blocks = set(df_excel['BLOCK'].unique())

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

# Find extras
extra = sorted(supabase_blocks - excel_blocks)
missing = sorted(excel_blocks - supabase_blocks)

print("EXTRA IN SUPABASE (not in Excel):", len(extra))
print("="*60)

by_prefix = {}
for block in extra:
    prefix = block[0]
    if prefix not in by_prefix:
        by_prefix[prefix] = []
    by_prefix[prefix].append(block)

for prefix in sorted(by_prefix.keys()):
    blocks = by_prefix[prefix]
    print(f"\n{prefix}xxx: {len(blocks)} blocks")
    print(", ".join(sorted(blocks)))

print("\n" + "="*60)
print("MISSING IN SUPABASE (in Excel not DB):", len(missing))
if missing:
    print(", ".join(missing[:30]))

print("\n" + "="*60)
print("ALL EXTRA BLOCKS ARE AME" if all(b[0] in ['A','B','C','E','F'] for b in extra) else "SOME NON-AME BLOCKS")
