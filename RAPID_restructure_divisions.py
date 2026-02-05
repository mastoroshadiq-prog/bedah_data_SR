"""
RAPID DATABASE RESTRUCTURE - 5 Minutes
=======================================
1. Create divisions table
2. Populate 13 divisions (4 AME + 4 OLE + 5 DBE)
3. Add division_id to blocks
4. Migrate data
5. Update dashboard
"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("STEP 1: Create divisions table")
print("=" * 80)

# Create table via SQL
create_table_sql = """
CREATE TABLE IF NOT EXISTS divisions (
    id SERIAL PRIMARY KEY,
    division_code VARCHAR(10) UNIQUE NOT NULL,
    division_name VARCHAR(100) NOT NULL,
    estate_id INTEGER REFERENCES estates(id),
    created_at TIMESTAMP DEFAULT NOW()
);
"""

try:
    supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
    print("✅ Table created")
except Exception as e:
    print(f"Note: {e}")

print("\nSTEP 2: Insert 13 divisions")
print("=" * 80)

# Get estate IDs
estates = supabase.table('estates').select('id, estate_code').execute()
estate_map = {e['estate_code']: e['id'] for e in estates.data}

divisions_data = [
    # AME divisions
    {'division_code': 'AME001', 'division_name': 'AME Division 001', 'estate_id': estate_map.get('AME')},
    {'division_code': 'AME002', 'division_name': 'AME Division 002', 'estate_id': estate_map.get('AME')},
    {'division_code': 'AME003', 'division_name': 'AME Division 003', 'estate_id': estate_map.get('AME')},
    {'division_code': 'AME004', 'division_name': 'AME Division 004', 'estate_id': estate_map.get('AME')},
    
    # OLE divisions
    {'division_code': 'OLE001', 'division_name': 'OLE Division 001', 'estate_id': estate_map.get('OLE')},
    {'division_code': 'OLE002', 'division_name': 'OLE Division 002', 'estate_id': estate_map.get('OLE')},
    {'division_code': 'OLE003', 'division_name': 'OLE Division 003', 'estate_id': estate_map.get('OLE')},
    {'division_code': 'OLE004', 'division_name': 'OLE Division 004', 'estate_id': estate_map.get('OLE')},
    
    # DBE divisions
    {'division_code': 'DBE001', 'division_name': 'DBE Division 001', 'estate_id': estate_map.get('DBE')},
    {'division_code': 'DBE002', 'division_name': 'DBE Division 002', 'estate_id': estate_map.get('DBE')},
    {'division_code': 'DBE003', 'division_name': 'DBE Division 003', 'estate_id': estate_map.get('DBE')},
    {'division_code': 'DBE004', 'division_name': 'DBE Division 004', 'estate_id': estate_map.get('DBE')},
    {'division_code': 'DBE005', 'division_name': 'DBE Division 005', 'estate_id': estate_map.get('DBE')},
]

# Insert divisions
for div in divisions_data:
    try:
        supabase.table('divisions').upsert(div, on_conflict='division_code').execute()
        print(f"✅ {div['division_code']}")
    except Exception as e:
        print(f"❌ {div['division_code']}: {e}")

print("\nSTEP 3: Add division_id column to blocks")
print("=" * 80)

alter_sql = """
ALTER TABLE blocks ADD COLUMN IF NOT EXISTS division_id INTEGER REFERENCES divisions(id);
"""

try:
    supabase.rpc('exec_sql', {'sql': alter_sql}).execute()
    print("✅ Column added")
except Exception as e:
    print(f"Note: {e}")

print("\nSTEP 4: Migrate data - assign division_id to blocks")
print("=" * 80)

# Get all divisions
divs = supabase.table('divisions').select('id, division_code').execute()
div_map = {d['division_code']: d['id'] for d in divs.data}

# Get all blocks
blocks = supabase.table('blocks').select('id, division').execute()
print(f"Total blocks to update: {len(blocks.data)}")

update_count = 0
for block in blocks.data:
    if block.get('division'):
        div_id = div_map.get(block['division'])
        if div_id:
            try:
                supabase.table('blocks').update({'division_id': div_id}).eq('id', block['id']).execute()
                update_count += 1
                if update_count % 100 == 0:
                    print(f"  Updated {update_count}...")
            except Exception as e:
                print(f"Error: {e}")

print(f"✅ Updated {update_count} blocks")

print("\nSTEP 5: Verify")
print("=" * 80)

# Check assignment
verify = supabase.table('blocks').select('division_id').execute()
assigned = sum(1 for b in verify.data if b.get('division_id'))
print(f"Blocks with division_id: {assigned}/{len(verify.data)}")

print("\n✅ RESTRUCTURE COMPLETE!")
print("Next: Update dashboard to use divisions table")
