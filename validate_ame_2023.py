"""
VALIDATE AME 2023 DATA - EXCEL vs SUPABASE
Compare Boss's Excel data (from Realisasi vs Potensi PT. SR) with current Supabase data
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

def validate_ame_2023(excel_file_path):
    """
    Validate AME 2023 production data
    
    Args:
        excel_file_path: Path to Excel file from Boss
    """
    
    load_dotenv()
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    
    print("="*80)
    print("VALIDASI DATA AME 2023 - EXCEL vs SUPABASE")
    print("="*80)
    
    # ========================================================================
    # STEP 1: LOAD EXCEL DATA
    # ========================================================================
    print("\nSTEP 1: Loading Excel data...")
    print("-" * 80)
    
    try:
        df_excel = pd.read_excel(excel_file_path)
        print(f"✓ Excel loaded: {len(df_excel)} rows")
        print(f"  Columns: {df_excel.columns.tolist()}")
        
        # Check for header row
        if df_excel.iloc[0].isna().any():
            print("  Removing header row...")
            df_excel = df_excel.iloc[1:].reset_index(drop=True)
        
        # Clean data
        for col in df_excel.columns:
            if 'real' in str(col).lower() or 'potensi' in str(col).lower():
                df_excel[col] = pd.to_numeric(df_excel[col], errors='coerce')
        
        df_excel = df_excel.dropna(subset=df_excel.columns[1:], how='all')
        
        print(f"  After cleaning: {len(df_excel)} rows")
        print(f"\n  Sample data:")
        print(df_excel.head(3))
        
    except Exception as e:
        print(f"✗ ERROR loading Excel: {e}")
        return
    
    # ========================================================================
    # STEP 2: LOAD SUPABASE DATA
    # ========================================================================
    print(f"\n{'='*80}")
    print("STEP 2: Loading Supabase data...")
    print("-" * 80)
    
    # Load production data
    all_prod = []
    page = 0
    while True:
        start = page * 1000
        end = start + 999
        response = supabase.table('production_annual').select('*').range(start, end).execute()
        if not response.data:
            break
        all_prod.extend(response.data)
        if len(response.data) < 1000:
            break
        page += 1
    
    df_prod = pd.DataFrame(all_prod)
    
    # Load blocks
    blocks_data = supabase.table('blocks').select('*').execute()
    df_blocks = pd.DataFrame(blocks_data.data)
    
    # Merge
    df_db = df_prod.merge(df_blocks[['id', 'block_code']], 
                          left_on='block_id', right_on='id', 
                          suffixes=('', '_block'), how='left')
    
    # Filter AME 2023
    df_db_ame = df_db[(df_db['year'] == 2023) & 
                       (df_db['block_code'].str[0].isin(['A', 'B', 'C', 'E', 'F']))].copy()
    
    print(f"✓ Supabase AME 2023: {len(df_db_ame)} records")
    
    # ========================================================================
    # STEP 3: COMPARE TOTALS
    # ========================================================================
    print(f"\n{'='*80}")
    print("STEP 3: Comparing Totals...")
    print("-" * 80)
    
    # Identify production columns in Excel
    excel_real_col = [c for c in df_excel.columns if 'real' in str(c).lower() or 'realisasi' in str(c).lower()]
    excel_target_col = [c for c in df_excel.columns if 'potensi' in str(c).lower() or 'target' in str(c).lower()]
    
    if excel_real_col and excel_target_col:
        excel_actual = df_excel[excel_real_col[0]].sum()
        excel_target = df_excel[excel_target_col[0]].sum()
    else:
        print("⚠️  Could not identify production columns in Excel")
        excel_actual = 0
        excel_target = 0
    
    db_actual = df_db_ame['real_ton'].sum()
    db_target = df_db_ame['potensi_ton'].sum()
    
    print(f"\nEXCEL (Source of Truth):")
    print(f"  Blocks: {len(df_excel)}")
    print(f"  Actual: {excel_actual:,.2f} Ton")
    print(f"  Target: {excel_target:,.2f} Ton")
    
    print(f"\nSUPABASE (Current):")
    print(f"  Blocks: {len(df_db_ame)}")
    print(f"  Actual: {db_actual:,.2f} Ton")
    print(f"  Target: {db_target:,.2f} Ton")
    
    print(f"\nDISCREPANCY:")
    actual_diff = excel_actual - db_actual
    target_diff = excel_target - db_target
    block_diff = len(df_excel) - len(df_db_ame)
    
    print(f"  Blocks: {block_diff:+d}")
    print(f"  Actual: {actual_diff:+,.2f} Ton ({actual_diff/excel_actual*100 if excel_actual > 0 else 0:.2f}%)")
    print(f"  Target: {target_diff:+,.2f} Ton ({target_diff/excel_target*100 if excel_target > 0 else 0:.2f}%)")
    
    # ========================================================================
    # STEP 4: BLOCK-BY-BLOCK COMPARISON
    # ========================================================================
    print(f"\n{'='*80}")
    print("STEP 4: Block-by-Block Analysis...")
    print("-" * 80)
    
    # Identify block code column in Excel
    excel_block_col = [c for c in df_excel.columns if 'block' in str(c).lower()]
    
    if excel_block_col:
        excel_blocks = set(df_excel[excel_block_col[0]].unique())
        db_blocks = set(df_db_ame['block_code'].unique())
        
        missing_in_db = excel_blocks - db_blocks
        extra_in_db = db_blocks - excel_blocks
        common = excel_blocks & db_blocks
        
        print(f"\nBlocks in Excel: {len(excel_blocks)}")
        print(f"Blocks in Supabase: {len(db_blocks)}")
        print(f"Common blocks: {len(common)}")
        
        if missing_in_db:
            print(f"\n⚠️  MISSING in Supabase ({len(missing_in_db)} blocks):")
            for block in sorted(missing_in_db)[:20]:
                print(f"  - {block}")
            if len(missing_in_db) > 20:
                print(f"  ... and {len(missing_in_db) - 20} more")
        
        if extra_in_db:
            print(f"\n⚠️  EXTRA in Supabase ({len(extra_in_db)} blocks):")
            for block in sorted(extra_in_db)[:20]:
                print(f"  - {block}")
            if len(extra_in_db) > 20:
                print(f"  ... and {len(extra_in_db) - 20} more")
    
    # ========================================================================
    # STEP 5: VERDICT
    # ========================================================================
    print(f"\n{'='*80}")
    print("VERDICT")
    print("="*80)
    
    if abs(actual_diff) < 100 and abs(target_diff) < 100 and abs(block_diff) < 5:
        print("\n✅ DATA MATCH!")
        print("   Excel and Supabase are in sync (< 1% difference)")
    else:
        print("\n⚠️  DISCREPANCY FOUND!")
        print(f"   Actual difference: {actual_diff:,.2f} Ton")
        print(f"   Target difference: {target_diff:,.2f} Ton")
        print(f"   Block difference: {block_diff} blocks")
        print("\n   RECOMMENDATION: Update Supabase with Excel data")
    
    print("\n" + "="*80)
    print("DONE")
    print("="*80)

if __name__ == "__main__":
    print("\nWAITING FOR EXCEL FILE...")
    print("\nExpected file:")
    print("  source/AME_2023_validation.xlsx")
    print("  (or any Excel file Boss provides)")
    
    # Check for file
    possible_files = [
        'source/AME_2023_validation.xlsx',
        'source/data_produksi_AME_2023.xlsx',
        'source/AME_2023.xlsx'
    ]
    
    for file_path in possible_files:
        if os.path.exists(file_path):
            print(f"\n✓ Found: {file_path}")
            print("\nStarting validation...")
            validate_ame_2023(file_path)
            break
    else:
        print("\n⏳ File not found yet.")
        print("   Boss, please upload Excel file to 'source/' folder")
        print("   Then run: python validate_ame_2023.py")
