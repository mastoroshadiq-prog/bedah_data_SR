"""
Upload Normalized Data to Supabase
Complete automated upload for 4 normalized tables
"""

import os
import pandas as pd
import time
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Supabase credentials  
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  ERROR: Supabase credentials not found!")
    print("\nPlease create a .env file with:")
    print("SUPABASE_URL=your_supabase_url")
    print("SUPABASE_KEY=your_supabase_anon_key")
    print("# or")
    print("SUPABASE_SERVICE_KEY=your_service_key")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 100)
print("UPLOAD NORMALIZED DATA TO SUPABASE")
print("=" * 100)

# Upload configuration (in correct order for FK dependencies)
TABLES_CONFIG = [
    {
        'name': 'estates',
        'file': 'output/normalized_estates.csv',
        'description': 'Estate master data (Dimension)',
        'batch_size': 100
    },
    {
        'name': 'blocks',
        'file': 'output/normalized_blocks.csv',
        'description': 'Block master data',
        'batch_size': 100
    },
    {
        'name': 'production_data',
        'file': 'output/normalized_production_data.csv',
        'description': 'Production metrics (Fact)',
        'batch_size': 50
    },
    {
        'name': 'realisasi_potensi',
        'file': 'output/normalized_realisasi_potensi.csv',
        'description': 'Realisasi vs Potensi comparison (Fact)',
        'batch_size': 50
    }
]

def upload_table(table_name, csv_file, description, batch_size=100):
    """Upload CSV data to Supabase table in batches"""
    
    print(f"\n{'=' * 100}")
    print(f"UPLOADING: {table_name}")
    print(f"Description: {description}")
    print(f"File: {csv_file}")
    print(f"{'=' * 100}")
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found - {csv_file}")
        return False
    
    # Load CSV
    print(f"\n📂 Loading CSV file...")
    df = pd.read_csv(csv_file)
    
    # Replace NaN with None for JSON compatibility
    df = df.where(pd.notna(df), None)
    
    total_rows = len(df)
    print(f"   ✓ Loaded: {total_rows} rows × {len(df.columns)} columns")
    
    # Convert to list of dictionaries
    print(f"\n📦 Converting to JSON format...")
    records = df.to_dict('records')
    print(f"   ✓ Converted: {len(records)} records")
    
    # Upload in batches
    print(f"\n⬆️  Uploading to Supabase (batch size: {batch_size})...")
    
    total_batches = (total_rows + batch_size - 1) // batch_size
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    for i in range(0, total_rows, batch_size):
        batch_num = (i // batch_size) + 1
        batch = records[i:i + batch_size]
        
        try:
            # Upload batch
            response = supabase.table(table_name).insert(batch).execute()
            
            success_count += len(batch)
            
            # Progress indicator
            progress = (batch_num / total_batches) * 100
            elapsed = time.time() - start_time
            rate = success_count / elapsed if elapsed > 0 else 0
            
            print(f"   Batch {batch_num}/{total_batches} ({progress:.1f}%): "
                  f"✓ {len(batch)} rows uploaded "
                  f"[{success_count}/{total_rows}] "
                  f"({rate:.1f} rows/sec)")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            error_count += len(batch)
            print(f"   Batch {batch_num}/{total_batches}: ❌ Error - {str(e)[:100]}")
            
            # Continue with next batch
            continue
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 Upload Summary for {table_name}:")
    print(f"   ✓ Success: {success_count} rows")
    print(f"   ❌ Failed: {error_count} rows")
    print(f"   ⏱  Time: {elapsed_time:.2f} seconds")
    print(f"   ⚡ Rate: {success_count / elapsed_time:.1f} rows/sec")
    
    if error_count == 0:
        print(f"\n✅ {table_name} uploaded successfully!")
        return True
    else:
        print(f"\n⚠️  {table_name} uploaded with {error_count} errors")
        return False

# ============================================================================
# MAIN UPLOAD PROCESS
# ============================================================================

def main():
    print("\n🚀 Starting normalized data upload...")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Supabase URL: {SUPABASE_URL}")
    
    # Track results
    results = []
    overall_start = time.time()
    
    for config in TABLES_CONFIG:
        result = upload_table(
            table_name=config['name'],
            csv_file=config['file'],
            description=config['description'],
            batch_size=config['batch_size']
        )
        
        results.append({
            'table': config['name'],
            'success': result
        })
        
        # Pause between tables
        time.sleep(1)
    
    # Overall summary
    overall_elapsed = time.time() - overall_start
    
    print("\n" + "=" * 100)
    print("UPLOAD COMPLETE!")
    print("=" * 100)
    
    print(f"\n📊 Overall Summary:")
    print(f"   Total tables: {len(results)}")
    print(f"   Successful: {sum(1 for r in results if r['success'])}")
    print(f"   Failed: {sum(1 for r in results if not r['success'])}")
    print(f"   Total time: {overall_elapsed:.2f} seconds")
    
    print(f"\n📋 Results by Table:")
    for r in results:
        status = "✅ SUCCESS" if r['success'] else "❌ FAILED"
        print(f"   {r['table']:30s} {status}")
    
    if all(r['success'] for r in results):
        print(f"\n✅ All tables uploaded successfully!")
        print(f"\n🎯 Next Steps:")
        print(f"   1. ✅ Data uploaded to Supabase")
        print(f"   2. 🔜 Run SQL script to create indexes: python run_sql_setup.py")
        print(f"   3. 🔜 Launch Streamlit dashboard: streamlit run dashboard.py")
        print(f"   4. 🔜 Run performance benchmark: python benchmark_performance.py")
    else:
        print(f"\n⚠️  Some tables failed to upload. Please check errors above.")
        print(f"\nℹ️  NOTE: If tables don't exist in Supabase, please:")
        print(f"   1. Go to Supabase Dashboard → SQL Editor")
        print(f"   2. Run: output/normalized_schema.sql")
        print(f"   3. Then run this script again")
    
    print("\n" + "=" * 100)
    
    return all(r['success'] for r in results)

if __name__ == "__main__":
    main()
