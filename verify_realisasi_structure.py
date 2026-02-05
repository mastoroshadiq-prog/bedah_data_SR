import pandas as pd

# Read the Excel file header
print("Checking 'Realisasi vs Potensi PT SR.xlsx' structure...")
print("=" * 100)

# Read first few rows to see structure
df = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', 
                   sheet_name='Real VS Potensi Inti',
                   header=None,
                   nrows=10)

print("\nFirst 10 rows (showing first 50 columns):")
print("=" * 100)

for i in range(10):
    print(f"\nRow {i}:")
    row_data = df.iloc[i, :50].tolist()
    for j, val in enumerate(row_data[:50]):
        if pd.notna(val):
            print(f"  Col {j}: {val}")

print("\n" + "=" * 100)
print("Checking if there are MONTH indicators in headers...")
print("=" * 100)

# Check all cells in first 5 rows for month names
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
          'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

found_months = []
for i in range(5):
    for j in range(len(df.columns)):
        val = str(df.iloc[i, j])
        for month in months:
            if month.lower() in val.lower():
                found_months.append({
                    'row': i,
                    'col': j,
                    'value': df.iloc[i, j],
                    'month': month
                })

if found_months:
    print(f"\n✅ Found {len(found_months)} month indicators:")
    for item in found_months[:20]:
        print(f"  Row {item['row']}, Col {item['col']}: {item['value']}")
else:
    print("\n❌ NO MONTH INDICATORS FOUND!")
    print("This file does NOT contain monthly data!")

# Check column count
print(f"\n" + "=" * 100)
print(f"Total columns in file: {len(df.columns)}")
print(f"If monthly: expected ~216 columns (3 years × 12 months × 6 metrics)")
print(f"If annual: expected ~18 columns (3 years × 6 metrics)")
