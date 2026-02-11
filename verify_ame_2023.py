import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("VERIFYING AME 2023 TOTALS")
print("="*60)

# Load all data
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

df = df_prod.merge(df_blocks[['id', 'block_code']], left_on='block_id', right_on='id', suffixes=('', '_block'), how='left')

# AME 2023
df_ame_2023 = df[(df['year'] == 2023) & (df['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F']))]
ame_actual = df_ame_2023['real_ton'].sum()
ame_target = df_ame_2023['potensi_ton'].sum()

print(f"\nAME 2023 (After Fix):")
print(f"  Records: {len(df_ame_2023)}")
print(f"  Actual: {ame_actual:,.2f} Ton")
print(f"  Target: {ame_target:,.2f} Ton")

print("\nDONE")
