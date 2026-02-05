"""
Quick comparison of Excel files
"""
import pandas as pd

print("Checking File 1: data_gabungan.xlsx")
try:
    xls1 = pd.ExcelFile('source/data_gabungan.xlsx')
    print(f"Sheets: {len(xls1.sheet_names)}")
    for sheet in xls1.sheet_names:
        print(f"  - {sheet}")
        
    # Load first sheet for analysis
    df1 = pd.read_excel('source/data_gabungan.xlsx', sheet_name=xls1.sheet_names[0])
    print(f"First sheet shape: {df1.shape}")
    print(f"Columns: {len(df1.columns)}")
    
except Exception as e:
    print(f"Error: {e}")

print("\nChecking File 2: Realisasi vs Potensi PT SR.xlsx")
try:
    xls2 = pd.ExcelFile('source/Realisasi vs Potensi PT SR.xlsx')
    print(f"Sheets: {len(xls2.sheet_names)}")
    for sheet in xls2.sheet_names:
        print(f"  - {sheet}")
        
    # Load first sheet for analysis
    df2 = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', sheet_name=xls2.sheet_names[0])
    print(f"First sheet shape: {df2.shape}")
    print(f"Columns: {len(df2.columns)}")
    
except Exception as e:
    print(f"Error: {e}")
