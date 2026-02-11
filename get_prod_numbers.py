import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
import sys

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# Load all production data
print("Loading data...", file=sys.stderr)
all_data = []
page = 0
while True:
    start = page * 1000
    end = start + 999
    response = supabase.table('production_annual').select('*').range(start, end).execute()
    if not response.data:
        break
    all_data.extend(response.data)
    if len(response.data) < 1000:
        break
    page += 1

df = pd.DataFrame(all_data)

# Output results
print("\n2023:")
dy = df[df['year'] == 2023]
print(f"Records: {len(dy)}")
print(f"Actual: {dy['real_ton'].sum():.2f}")
print(f"Target: {dy['potensi_ton'].sum():.2f}")

print("\n2024:")
dy = df[df['year'] == 2024]
print(f"Records: {len(dy)}")
print(f"Actual: {dy['real_ton'].sum():.2f}")
print(f"Target: {dy['potensi_ton'].sum():.2f}")

print("\n2025:")
dy = df[df['year'] == 2025]
print(f"Records: {len(dy)}")
print(f"Actual: {dy['real_ton'].sum():.2f}")
print(f"Target: {dy['potensi_ton'].sum():.2f}")

print("\nTOTAL:")
print(f"Actual: {df['real_ton'].sum():.2f}")
print(f"Target: {df['potensi_ton'].sum():.2f}")

print("\nDATA ISSUES:")
print(f"NULL values: {df['real_ton'].isna().sum()}")
print(f"ZERO values: {(df['real_ton'] == 0).sum()}")
