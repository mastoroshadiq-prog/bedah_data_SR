"""
FIX: Re-upload WITHOUT id column (let Supabase auto-generate)
"""
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=" * 80)
print("RE-UPLOAD GANODERMA DATA (WITHOUT ID COLUMN)")
print("=" * 80)

# Read CSV
csv_path = 'output/normalized_tables/phase2_metadata/block_pest_disease.csv'
df = pd.read_csv(csv_path)

print(f"\nOriginal CSV:")
print(f"  Total records: {len(df)}")
print(f"  Columns: {df.columns.tolist()}")

# DROP 'id' column - let Supabase auto-generate
if 'id' in df.columns:
    df = df.drop('id', axis=1)
    print(f"\n✅ Dropped 'id' column")
    print(f"  New columns: {df.columns.tolist()}")

# Sample G001A
g001a = df[df['block_id'] == 236]
if len(g001a) > 0:
    print(f"\nG001A (block_id=236) to upload:")
    print(f"  pct_serangan: {g001a['pct_serangan'].values[0]}")
    print(f"  As percentage: {g001a['pct_serangan'].values[0] * 100:.2f}%")

print("\n" + "=" * 80)
proceed = input("Proceed with re-upload? (yes/no): ")

if proceed.lower() == 'yes':
    print("\n1. Deleting ALL existing records...")
    try:
        # Use a condition that matches all records
        result = supabase.table('block_pest_disease').delete().gte('id', 0).execute()
        print(f"   ✅ Deleted")
    except Exception as e:
        print(f"   Note: {e}")
    
    print("\n2. Uploading fresh data (WITHOUT id column)...")
    records = df.to_dict('records')
    
    # Upload in batches
    batch_size = 100
    uploaded = 0
    errors = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            supabase.table('block_pest_disease').insert(batch).execute()
            uploaded += len(batch)
            print(f"   Uploaded {uploaded}/{len(records)}")
        except Exception as e:
            print(f"   ❌ Error at batch {i}: {e}")
            errors += 1
    
    print(f"\n✅ Upload complete!")
    print(f"   Success: {uploaded}/{len(records)}")
    print(f"   Errors: {errors}")
    
    # Verify G001A
    print("\n3. Verifying G001A...")
    blocks = supabase.table('blocks').select('id').eq('block_code', 'G001A').execute()
    if blocks.data:
        block_id = blocks.data[0]['id']
        gano = supabase.table('block_pest_disease').select('pct_serangan').eq('block_id', block_id).execute()
        if gano.data:
            val = gano.data[0]['pct_serangan']
            print(f"   pct_serangan: {val}")
            print(f"   As percentage: {val * 100:.2f}%")
            
            expected = 0.00339558
            if abs(val - expected) < 0.0001:
                print(f"   ✅ CORRECT! (expected ~{expected*100:.2f}%)")
            else:
                print(f"   ❌ Wrong! (expected ~{expected*100:.2f}%)")
        else:
            print("   ❌ No data found!")
    
    # Verify statistics
    print("\n4. Overall statistics...")
    all_gano = supabase.table('block_pest_disease').select('pct_serangan').execute()
    df_check = pd.DataFrame(all_gano.data)
    print(f"   Total records: {len(df_check)}")
    print(f"   Zero values: {(df_check['pct_serangan'] == 0).sum()}")
    print(f"   Non-zero: {(df_check['pct_serangan'] > 0).sum()}")
    print(f"   Mean: {df_check['pct_serangan'].mean():.4f} ({df_check['pct_serangan'].mean()*100:.2f}%)")
    print(f"   Max: {df_check['pct_serangan'].max():.4f} ({df_check['pct_serangan'].max()*100:.2f}%)")
    
else:
    print("\n❌ Upload cancelled")
