from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Excel
df_excel = pd.read_excel('source/data_produksi_OLE_2023.xlsx')
if df_excel.iloc[0].isna().any():
    df_excel = df_excel.iloc[1:].reset_index(drop=True)
df_excel['Realisasi'] = pd.to_numeric(df_excel['Realisasi'], errors='coerce')
df_excel = df_excel.dropna(subset=['BLOCK'])

row = df_excel[df_excel['BLOCK'] == 'F005A'].iloc[0]

# Supabase
db_record = supabase.table('production_annual').select('*').eq('year', 2023).eq('block_code', 'F005A').execute()

print("F005A 2023 COMPARISON:")
print("="*60)
print(f"\nExcel:")
print(f"  Actual: {row['Realisasi']:.2f} Ton")
print(f"  Target: {row['Potensi']:.2f} Ton")

if db_record.data:
    db = db_record.data[0]
    print(f"\nSupabase (id {db['id']}):")
    print(f"  Actual: {db['real_ton']:.2f} Ton" if db['real_ton'] else "  Actual: NULL")
    print(f"  Target: {db['potensi_ton']:.2f} Ton" if db['potensi_ton'] else "  Target: NULL")
    
    diff = row['Realisasi'] - (db['real_ton'] or 0)
    
    if abs(diff) > 0.01:
        print(f"\n⚠️ DIFFERENT! Need UPDATE")
        print(f"  Diff: {diff:.2f} Ton")
        
        # Update
        print(f"\nUpdating...")
        try:
            result = supabase.table('production_annual').update({
                'real_ton': float(row['Realisasi']),
                'potensi_ton': float(row['Potensi']),
                'gap_ton': float(row['Realisasi'] - row['Potensi']),
                'gap_pct_ton': float((row['Realisasi'] - row['Potensi']) / row['Potensi'] * 100)
            }).eq('id', db['id']).execute()
            
            if result.data:
                print("✓ Updated!")
            else:
                print("✗ Update failed")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("\n✓ Values match!")
else:
    print("\n⚠️ Not in Supabase")

print("\nDONE")
