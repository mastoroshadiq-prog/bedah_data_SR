"""
Check complete column structure dari kedua file
"""
import pandas as pd

print("=" * 100)
print("DETAILED COLUMN ANALYSIS")
print("=" * 100)

# File 1: data_gabungan.xlsx
print("\n" + "=" * 100)
print("FILE 1: data_gabungan.xlsx (177 columns)")
print("=" * 100)

try:
    df1 = pd.read_excel('source/data_gabungan.xlsx', sheet_name='Lembar1', nrows=3)
    print(f"\nShape: {df1.shape}")
    print(f"\nALL COLUMNS ({len(df1.columns)}):")
    for i, col in enumerate(df1.columns, 1):
        print(f"  {i:3d}. {col}")
    
    # Look for specific data types
    print("\n" + "-" * 80)
    print("SEARCHING FOR KEY DATA...")
    print("-" * 80)
    
    # SPH
    sph_cols = [c for c in df1.columns if 'sph' in str(c).lower()]
    print(f"\nSPH columns: {sph_cols if sph_cols else 'Not found'}")
    
    # Ganoderma
    gano_cols = [c for c in df1.columns if 'gano' in str(c).lower() or 'stadium' in str(c).lower() or 'serangan' in str(c).lower()]
    print(f"Ganoderma columns: {gano_cols if gano_cols else 'Not found'}")
    
    # Kentosan
    kent_cols = [c for c in df1.columns if 'kent' in str(c).lower()]
    print(f"Kentosan columns: {kent_cols if kent_cols else 'Not found'}")
    
    # Sisipan
    sisip_cols = [c for c in df1.columns if 'sisip' in str(c).lower()]
    print(f"Sisipan columns: {sisip_cols[:10] if sisip_cols else 'Not found'}")
    
    # TBM
    tbm_cols = [c for c in df1.columns if 'tbm' in str(c).lower() or 'belum' in str(c).lower()]
    print(f"TBM columns: {tbm_cols if tbm_cols else 'Not found'}")
    
    # Production
    prod_cols = [c for c in df1.columns if 'real' in str(c).lower() or 'potensi' in str(c).lower() or 'bjr' in str(c).lower()]
    print(f"Production columns: {len(prod_cols)} found")
    if prod_cols:
        print(f"  Sample: {prod_cols[:5]}")

except Exception as e:
    print(f"Error: {e}")

# File 2: Realisasi vs Potensi PT SR.xlsx
print("\n" + "=" * 100)
print("FILE 2: Realisasi vs Potensi PT SR.xlsx")
print("=" * 100)

try:
    # Sheet 1: Inti
    print("\nSHEET 1: Real VS Potensi Inti (116 columns)")
    print("-" * 80)
    df2_inti = pd.read_excel('source/Realisasi vs Potensi PT SR.xlsx', sheet_name='Real VS Potensi Inti', nrows=3)
    print(f"Shape: {df2_inti.shape}")
    print(f"\nALL COLUMNS ({len(df2_inti.columns)}):")
    for i, col in enumerate(df2_inti.columns, 1):
        print(f"  {i:3d}. {col}")
    
    # Look for specific data types
    print("\n" + "-" * 80)
    print("SEARCHING FOR KEY DATA...")
    print("-" * 80)
    
    # SPH
    sph_cols = [c for c in df2_inti.columns if 'sph' in str(c).lower()]
    print(f"\nSPH columns: {sph_cols if sph_cols else 'Not found'}")
    
    # Ganoderma
    gano_cols = [c for c in df2_inti.columns if 'gano' in str(c).lower() or 'stadium' in str(c).lower() or 'serangan' in str(c).lower()]
    print(f"Ganoderma columns: {gano_cols if gano_cols else 'Not found'}")
    
    # Kentosan
    kent_cols = [c for c in df2_inti.columns if 'kent' in str(c).lower()]
    print(f"Kentosan columns: {kent_cols if kent_cols else 'Not found'}")
    
    # Sisipan
    sisip_cols = [c for c in df2_inti.columns if 'sisip' in str(c).lower()]
    print(f"Sisipan columns: {sisip_cols if sisip_cols else 'Not found'}")
    
    # TBM
    tbm_cols = [c for c in df2_inti.columns if 'tbm' in str(c).lower() or 'belum' in str(c).lower()]
    print(f"TBM columns: {tbm_cols if tbm_cols else 'Not found'}")
    
    # Production
    prod_cols = [c for c in df2_inti.columns if 'real' in str(c).lower() or 'potensi' in str(c).lower() or 'bjr' in str(c).lower()]
    print(f"Production columns: {len(prod_cols)} found")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
