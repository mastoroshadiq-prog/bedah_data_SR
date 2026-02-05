"""
FIX: Re-upload block_pest_disease from correct CSV
Root cause: Supabase data was overwritten with zeros
"""
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 80)
print("RE-UPLOADING BLOCK_PEST_DISEASE FROM CORRECT CSV")
print("=" * 80)

# Read correct CSV
csv_path = 'output/normalized_tables/phase2_metadata/block_pest_disease.csv'
df = pd.read_csv(csv_path)

print(f"\nCSV data:")
print(f"  Total records: {len(df)}")
print(f"  Columns: {df.columns.tolist()}")

# Sample G001A
g001a = df[df['block_id'] == 236]
if len(g001a) > 0:
    print(f"\nSample G001A (block_id=236):")
    print(f"  pct_serangan: {g001a['pct_serangan'].values[0]}")
    print(f"  As percentage: {g001a['pct_serangan'].values[0] * 100:.2f}%")

proceed = input("\n⚠️ This will REPLACE all Ganoderma data in Supabase. Proceed? (yes/no): ")

if proceed.lower() == 'yes':
    print("\nDeleting existing data...")
    try:
        # Delete all existing records
        supabase.table('block_pest_disease').delete().neq('id', 0).execute()
        print("✅ Deleted")
    except Exception as e:
        print(f"Note: {e}")
    
    print("\nUploading new data...")
    records = df.to_dict('records')
    
    # Upload in batches
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            supabase.table('block_pest_disease').insert(batch).execute()
            print(f"  Uploaded {i+len(batch)}/{len(records)}")
        except Exception as e:
            print(f"  Error at batch {i}: {e}")
    
    print("\n✅ Upload complete!")
    
    # Verify G001A
    print("\nVerifying G001A...")
    blocks = supabase.table('blocks').select('id').eq('block_code', 'G001A').execute()
    if blocks.data:
        block_id = blocks.data[0]['id']
        gano = supabase.table('block_pest_disease').select('pct_serangan').eq('block_id', block_id).execute()
        if gano.data:
            val = gano.data[0]['pct_serangan']
            print(f"  pct_serangan: {val}")
            print(f"  As percentage: {val * 100:.2f}%")
            
            if abs(val - 0.00339558) < 0.0001:
                print("  ✅ CORRECT!")
            else:
                print("  ❌ Still wrong!")
else:
    print("\n❌ Upload cancelled")
