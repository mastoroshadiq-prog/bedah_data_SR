from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

blocks = supabase.table('blocks').select('id, block_code, division').execute()
df = pd.DataFrame(blocks.data)

df['estate_letter'] = df['block_code'].str[0]
estate_map = {
    'A': 'AME', 'B': 'AME', 'E': 'AME', 'F': 'AME',
    'O': 'OLE', 'C': 'OLE', 'K': 'OLE', 'L': 'OLE',
    'D': 'DBE', 'M': 'DBE', 'N': 'DBE'
}
df['estate'] = df['estate_letter'].map(estate_map)

divs = df[df['division'].notna()]['division'].unique()
print('All divisions:', sorted(divs))

print('\nDivisions per estate (by naming):')
for e in ['AME', 'OLE', 'DBE']:
    edivs = [d for d in divs if d.startswith(e)]
    print(f'{e}: {len(edivs)} divisions')
    print(f'  {sorted(edivs)}')

print('\nDREAMMARIGGING check - blocks in wrong estate:')
for e in ['AME', 'OLE', 'DBE']:
    df_estate = df[df['estate'] == e]
    wrong_divs = df_estate[~df_estate['division'].str.startswith(e, na=False)]
    if len(wrong_divs) > 0:
        print(f'\n{e} estate has {len(wrong_divs)} blocks with wrong divisions:')
        wrong_div_list = wrong_divs['division'].unique()
        for wd in sorted(wrong_div_list):
            count = len(wrong_divs[wrong_divs['division'] == wd])
            print(f'  {wd}: {count} blocks')
