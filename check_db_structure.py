"""
CHECK PROPER ESTATE RELATIONSHIP
Using: blocks -> division -> estate
"""

import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

print("="*80)
print("CHECKING DATABASE STRUCTURE: Estate -> Division -> Blocks")
print("="*80)

# Load all tables
print("\nLoading tables...")

# Blocks table
blocks_data = supabase.table('blocks').select('*').execute()
df_blocks = pd.DataFrame(blocks_data.data)
print(f"  Blocks: {len(df_blocks)}")
print(f"  Columns: {df_blocks.columns.tolist()}")

# Check if we have division info
if 'division' in df_blocks.columns or 'division_id' in df_blocks.columns:
    print("\n  Block has division reference!")
    
    # Check divisions table
    try:
        divisions_data = supabase.table('divisions').select('*').execute()
        df_divisions = pd.DataFrame(divisions_data.data)
        print(f"\n  Divisions table: {len(df_divisions)}")
        print(f"  Columns: {df_divisions.columns.tolist()}")
        
        # Sample
        print("\n  Sample divisions:")
        print(df_divisions.head(10))
        
    except Exception as e:
        print(f"\n  Could not load divisions table: {e}")
        df_divisions = None
else:
    print("\n  No division reference in blocks table")
    df_divisions = None

# Check estates table
try:
    estates_data = supabase.table('estates').select('*').execute()
    df_estates = pd.DataFrame(estates_data.data)
    print(f"\n  Estates table: {len(df_estates)}")
    print(f"  Columns: {df_estates.columns.tolist()}")
    print("\n  Sample estates:")
    print(df_estates)
except Exception as e:
    print(f"\n  Could not load estates table: {e}")
    df_estates = None

print("\n" + "="*80)
print("CHECKING BLOCK->DIVISION->ESTATE RELATIONSHIPS")
print("="*80)

# Show sample blocks with their divisions
print("\nSample blocks (first 10):")
print(df_blocks[['id', 'block_code', 'division', 'division_id']].head(10))

# If we have divisions table, join to see estate
if df_divisions is not None:
    # Merge blocks with divisions
    df_full = df_blocks.merge(df_divisions, left_on='division_id', right_on='id', 
                              suffixes=('_block', '_division'), how='left')
    
    print("\nSample blocks with division info:")
    cols_to_show = ['block_code', 'division_block', 'division_id']
    if 'name' in df_divisions.columns:
        cols_to_show.append('name')
    if 'estate' in df_divisions.columns:
        cols_to_show.append('estate')
    if 'estate_id' in df_divisions.columns:
        cols_to_show.append('estate_id')
    
    print(df_full[cols_to_show].head(15))
    
    # Check if division has estate reference
    if 'estate' in df_divisions.columns or 'estate_id' in df_divisions.columns:
        print("\n✓ Division table has estate reference!")
        
        # Merge with estates if available
        if df_estates is not None and 'estate_id' in df_divisions.columns:
            df_full = df_full.merge(df_estates, left_on='estate_id', right_on='id',
                                   suffixes=('_division', '_estate'), how='left')
            
            print("\nFull hierarchy sample:")
            print(df_full[['block_code', 'division_block', 'name_estate']].head(15))

print("\n" + "="*80)
print("RECOMMENDATION FOR FILTERING AME BLOCKS")
print("="*80)

if df_divisions is not None and ('estate' in df_divisions.columns or 'estate_id' in df_divisions.columns):
    print("\nUse proper join:")
    print("  blocks -> division_id -> divisions -> estate/estate_id -> estates")
    print("\nThis will give accurate estate assignment, not based on prefix!")
else:
    print("\nNeed to check database schema:")
    print("  1. Does divisions table have estate reference?")
    print("  2. Or do we need different approach?")

print("\nDONE")
