import pandas as pd

print("Analyzing Realisasi vs Potensi PT SR.xlsx...")
print("=" * 80)

# Try different header rows
for header_row in range(10):
    print(f"\n--- Testing Header at Row {header_row} ---")
    try:
        df = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', 
                           header=header_row, nrows=5)
        print(f"Columns: {df.columns.tolist()[:15]}")
        print(f"First few values:")
        print(df.iloc[0, :10].to_dict())
    except Exception as e:
        print(f"Error: {str(e)[:100]}")
