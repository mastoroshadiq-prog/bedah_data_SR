"""
Script untuk upload data yang sudah dibersihkan ke Supabase
"""

from supabase import create_client, Client
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for bulk insert

# Table name
TABLE_NAME = "data_gabungan"

def upload_to_supabase(csv_file='output/data_cleaned_latest.csv', batch_size=500):
    """
    Upload cleaned data to Supabase
    
    Args:
        csv_file: Path to cleaned CSV file
        batch_size: Number of rows per batch (max 1000)
    """
    
    print("=" * 80)
    print("SUPABASE UPLOAD SCRIPT")
    print("=" * 80)
    
    # Validate credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n❌ ERROR: Missing Supabase credentials!")
        print("\nPlease create a .env file with:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_SERVICE_KEY=your-service-key")
        return False
    
    print(f"\n✓ Supabase URL: {SUPABASE_URL}")
    print(f"✓ Table name: {TABLE_NAME}")
    
    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client initialized")
    except Exception as e:
        print(f"❌ Error initializing Supabase client: {str(e)}")
        return False
    
    # Load cleaned data
    try:
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df)} rows from {csv_file}")
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        return False
    
    # Convert datetime columns to ISO format
    datetime_cols = ['created_at', 'updated_at']
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Convert to list of dictionaries
    data_records = df.to_dict('records')
    
    # Batch insert
    total_rows = len(data_records)
    total_batches = (total_rows + batch_size - 1) // batch_size
    
    print(f"\n📤 Starting upload...")
    print(f"   Total rows: {total_rows:,}")
    print(f"   Batch size: {batch_size}")
    print(f"   Total batches: {total_batches}")
    print("")
    
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    for i in range(0, total_rows, batch_size):
        batch_num = i // batch_size + 1
        batch = data_records[i:i + batch_size]
        
        try:
            response = supabase.table(TABLE_NAME).insert(batch).execute()
            success_count += len(batch)
            
            # Progress indicator
            progress = (batch_num / total_batches) * 100
            elapsed = time.time() - start_time
            rows_per_sec = success_count / elapsed if elapsed > 0 else 0
            
            print(f"✓ Batch {batch_num}/{total_batches} ({progress:.1f}%) | "
                  f"{len(batch)} rows | "
                  f"{rows_per_sec:.1f} rows/sec | "
                  f"Total: {success_count:,}/{total_rows:,}")
            
        except Exception as e:
            error_count += len(batch)
            print(f"✗ Batch {batch_num}/{total_batches} FAILED: {str(e)}")
            
            # Log error details
            with open('output/upload_errors.log', 'a') as f:
                f.write(f"\n[{datetime.now()}] Batch {batch_num} error:\n")
                f.write(f"{str(e)}\n")
                f.write("-" * 80 + "\n")
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully uploaded: {success_count:,} rows")
    print(f"✗ Failed: {error_count:,} rows")
    print(f"⏱  Time elapsed: {elapsed_time:.2f} seconds")
    print(f"⚡ Average speed: {(success_count / elapsed_time):.1f} rows/sec")
    
    if error_count > 0:
        print(f"\n⚠️  Error log saved to: output/upload_errors.log")
    
    if success_count == total_rows:
        print("\n✅ ALL DATA UPLOADED SUCCESSFULLY!")
        return True
    else:
        print("\n⚠️  PARTIAL UPLOAD - Some rows failed")
        return False


def verify_upload():
    """Verify data in Supabase"""
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    try:
        supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        # Count total rows
        response = supabase.table(TABLE_NAME).select("*", count='exact').execute()
        count = response.count
        
        print(f"\n✓ Total rows in Supabase: {count:,}")
        
        # Get first 5 rows
        response = supabase.table(TABLE_NAME).select("*").limit(5).execute()
        
        print(f"✓ Sample data retrieved: {len(response.data)} rows")
        print("\nFirst row sample:")
        if response.data:
            first_row = response.data[0]
            for key, value in list(first_row.items())[:10]:
                print(f"  {key}: {value}")
        
        print("\n✅ Verification completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Verification error: {str(e)}")
        return False


def create_indexes():
    """Create recommended indexes"""
    
    print("\n" + "=" * 80)
    print("CREATING INDEXES")
    print("=" * 80)
    
    print("\nℹ️  Please run these SQL commands in Supabase SQL Editor:")
    print("\n```sql")
    print(f"-- Index for primary key (auto-created)")
    print(f"-- CREATE INDEX idx_{TABLE_NAME}_id ON {TABLE_NAME}(id);")
    print(f"\n-- Indexes for common queries")
    print(f"CREATE INDEX idx_{TABLE_NAME}_k001 ON {TABLE_NAME}(k001);")
    print(f"CREATE INDEX idx_{TABLE_NAME}_c001 ON {TABLE_NAME}(c001);")
    print(f"CREATE INDEX idx_{TABLE_NAME}_created ON {TABLE_NAME}(created_at);")
    print(f"\n-- Composite index")
    print(f"CREATE INDEX idx_{TABLE_NAME}_composite ON {TABLE_NAME}(c001, c002, created_at);")
    print("```\n")


def main():
    """Main function"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "SUPABASE UPLOADER" + " " * 34 + "║")
    print("║" + " " * 20 + "Data Upload & Verification" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Step 1: Upload
    success = upload_to_supabase()
    
    if not success:
        print("\n❌ Upload failed or incomplete!")
        return False
    
    # Step 2: Verify
    verify_upload()
    
    # Step 3: Show index creation commands
    create_indexes()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. ✅ Data uploaded to Supabase")
    print("2. 🔜 Create indexes (run SQL commands above)")
    print("3. 🔜 Setup Row Level Security (if needed)")
    print("4. 🔜 Start your data analysis!")
    print("\n📊 You can now query your data in Supabase SQL Editor")
    print("📈 Or connect via Python client for analysis")
    print("")
    
    return True


if __name__ == "__main__":
    main()
