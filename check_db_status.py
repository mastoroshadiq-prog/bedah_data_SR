from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'), 
    os.getenv('SUPABASE_SERVICE_KEY')
)

tables = [
    'estates',
    'blocks', 
    'block_land_infrastructure',
    'block_pest_disease',
    'block_planting_history',
    'block_planting_yearly',
    'production_annual',
    'production_monthly'
]

print("=" * 60)
print("CURRENT DATABASE STATUS")
print("=" * 60)

total = 0
for table in tables:
    try:
        count = supabase.table(table).select("id", count="exact").limit(1).execute().count
        print(f"{table:30} {count:>6,} records")
        total += count
    except Exception as e:
        print(f"{table:30} ERROR: {e}")

print("=" * 60)
print(f"{'TOTAL':30} {total:>6,} records")
print("=" * 60)
