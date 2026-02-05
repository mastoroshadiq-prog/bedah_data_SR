"""
Database Normalization Analysis & Schema Design
Analyze merged data and propose normalized database schema
"""

import pandas as pd
import json
from datetime import datetime

print("=" * 100)
print("DATABASE NORMALIZATION ANALYSIS")
print("=" * 100)

# ============================================================================
# STEP 1: ANALYZE CURRENT STRUCTURE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 1: ANALYZING CURRENT MERGED DATA STRUCTURE")
print("=" * 100)

# Load merged data
df_merged = pd.read_csv('output/merged_full_data.csv')
print(f"\n📊 Current Structure:")
print(f"  Total rows: {df_merged.shape[0]}")
print(f"  Total columns: {df_merged.shape[1]}")
print(f"  File size: {df_merged.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# Analyze column groups
gabungan_cols = [col for col in df_merged.columns if '_gabungan' in col.lower() or 
                 col in ['id_gabungan', 'k001', 'k002', 'k001_clean', 'nomor']]
realisasi_cols = [col for col in df_merged.columns if '_realisasi' in col.lower() or 
                  col in ['id_realisasi', 'estate', 'blok', 'ha', 'blok_clean']]
data_cols = [col for col in df_merged.columns if col not in gabungan_cols and col not in realisasi_cols]

print(f"\n📋 Column Groups:")
print(f"  Gabungan-specific: {len(gabungan_cols)} columns")
print(f"  Realisasi-specific: {len(realisasi_cols)} columns")
print(f"  Data/Other: {len(data_cols)} columns")

# ============================================================================
# STEP 2: IDENTIFY DATA ENTITIES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: IDENTIFYING DATA ENTITIES (Normalization)")
print("=" * 100)

print("""
🎯 PROPOSED NORMALIZED SCHEMA (3NF):

Based on the data analysis, we should split into these entities:

1. **blocks** (Master Data - Block Information)
   - Primary Key: block_code
   - Attributes: estate, area_ha, year_planted, etc.
   - Purpose: Core block identification

2. **production_data** (Fact Table - Gabungan Data)
   - Foreign Key: block_code → blocks.block_code
   - Attributes: All production/operational metrics from gabungan
   - Purpose: Detailed production records

3. **realisasi_potensi** (Fact Table - Realisasi vs Potensi)
   - Foreign Key: block_code → blocks.block_code
   - Attributes: Yearly realisasi vs potensi data (2014-2025)
   - Purpose: Performance comparison by year

4. **estates** (Dimension Table - Optional)
   - Primary Key: estate_code
   - Attributes: estate_name, region, etc.
   - Purpose: Estate master data

Benefits:
✅ Easier to query specific metrics
✅ Reduced data redundancy
✅ Better performance (smaller tables)
✅ Easier to maintain and update
✅ Scalable for future data additions
✅ Clear data relationships
""")

# ============================================================================
# STEP 3: DESIGN NORMALIZED TABLES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: CREATING NORMALIZED TABLES")
print("=" * 100)

# Table 1: BLOCKS (Master Data)
print("\n📦 Creating Table 1: BLOCKS (Master Data)")

blocks_columns = ['block_code', 'estate', 'area_ha', 'year_planted', 'number']

# Extract blocks data
df_blocks = df_merged[['k001', 'estate', 'ha', 'k002', 'nomor']].copy()
df_blocks.columns = blocks_columns
df_blocks = df_blocks.drop_duplicates(subset=['block_code'])
df_blocks = df_blocks.dropna(subset=['block_code'])
df_blocks = df_blocks.reset_index(drop=True)
df_blocks.insert(0, 'id', range(1, len(df_blocks) + 1))

print(f"  ✓ Created: {df_blocks.shape[0]} rows × {df_blocks.shape[1]} columns")
print(f"  Primary Key: block_code")
print(f"  Sample data:")
print(df_blocks.head())

# Table 2: ESTATES (Dimension)
print("\n📦 Creating Table 2: ESTATES (Dimension)")

df_estates = df_blocks[['estate']].drop_duplicates().dropna()
df_estates = df_estates.reset_index(drop=True)
df_estates.insert(0, 'id', range(1, len(df_estates) + 1))
df_estates.columns = ['id', 'estate_code']

print(f"  ✓ Created: {df_estates.shape[0]} rows × {df_estates.shape[1]} columns")
print(f"  Primary Key: estate_code")
print(f"  Estates: {sorted(df_estates['estate_code'].unique().tolist())}")

# Table 3: PRODUCTION_DATA (from Gabungan)
print("\n📦 Creating Table 3: PRODUCTION_DATA (from Gabungan)")

# Select gabungan columns (exclude realisasi columns)
production_cols = ['id_gabungan', 'k001'] + [col for col in df_merged.columns 
                                               if col.startswith('c0') or col.startswith('p0') 
                                               or col in ['created_at', 'updated_at', 'data_source']]

# Filter to only include columns that exist
production_cols = [col for col in production_cols if col in df_merged.columns]

df_production = df_merged[production_cols].copy()
df_production = df_production.rename(columns={'k001': 'block_code', 'id_gabungan': 'id'})
df_production = df_production.dropna(subset=['block_code'])

print(f"  ✓ Created: {df_production.shape[0]} rows × {df_production.shape[1]} columns")
print(f"  Foreign Key: block_code → blocks.block_code")
print(f"  First 5 columns: {list(df_production.columns[:5])}")

# Table 4: REALISASI_POTENSI (Time Series Data)
print("\n📦 Creating Table 4: REALISASI_POTENSI (Time Series)")

# Get realisasi-specific numeric columns (likely year-based data)
# These are columns from realisasi file that aren't in the core columns
realisasi_data_cols = [col for col in df_merged.columns 
                       if col not in ['id_gabungan', 'id_realisasi', 'estate', 'blok', 'ha', 
                                     'k001', 'k002', 'nomor', 'k001_clean', 'blok_clean',
                                     'created_at', 'updated_at', 'data_source_realisasi']
                       and col not in production_cols[2:]]  # Exclude production cols

df_realisasi = df_merged[['k001', 'blok'] + realisasi_data_cols[:50]].copy()  # Take first 50 data cols
df_realisasi = df_realisasi[df_realisasi['blok'].notna()]  # Only matched records
df_realisasi = df_realisasi.rename(columns={'k001': 'block_code'})
df_realisasi = df_realisasi.drop(columns=['blok'], errors='ignore')
df_realisasi.insert(0, 'id', range(1, len(df_realisasi) + 1))

print(f"  ✓ Created: {df_realisasi.shape[0]} rows × {df_realisasi.shape[1]} columns")
print(f"  Foreign Key: block_code → blocks.block_code")
print(f"  Contains: Yearly realisasi vs potensi metrics")

# ============================================================================
# STEP 4: ANALYZE NORMALIZATION BENEFITS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: NORMALIZATION BENEFITS ANALYSIS")
print("=" * 100)

# Calculate storage comparison
original_size = df_merged.memory_usage(deep=True).sum() / 1024 / 1024
normalized_size = (df_blocks.memory_usage(deep=True).sum() + 
                   df_estates.memory_usage(deep=True).sum() +
                   df_production.memory_usage(deep=True).sum() +
                   df_realisasi.memory_usage(deep=True).sum()) / 1024 / 1024

print(f"\n💾 Storage Comparison:")
print(f"  Single merged table: {original_size:.2f} MB")
print(f"  Normalized tables: {normalized_size:.2f} MB")
print(f"  Difference: {original_size - normalized_size:.2f} MB ({(original_size - normalized_size)/original_size*100:.1f}% reduction)")

print(f"\n📊 Table Sizes:")
print(f"  blocks: {df_blocks.shape[0]} rows × {df_blocks.shape[1]} cols")
print(f"  estates: {df_estates.shape[0]} rows × {df_estates.shape[1]} cols")
print(f"  production_data: {df_production.shape[0]} rows × {df_production.shape[1]} cols")
print(f"  realisasi_potensi: {df_realisasi.shape[0]} rows × {df_realisasi.shape[1]} cols")

print(f"\n✅ Benefits:")
print(f"  1. Query Performance: Smaller, focused tables")
print(f"  2. Maintainability: Clear data boundaries")
print(f"  3. Scalability: Easy to add new metrics")
print(f"  4. Data Integrity: Foreign key constraints")
print(f"  5. Flexibility: Mix and match tables as needed")

# ============================================================================
# STEP 5: GENERATE SQL SCHEMA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: GENERATING SQL SCHEMA (PostgreSQL/Supabase)")
print("=" * 100)

sql_schema = """
-- ============================================================================
-- NORMALIZED DATABASE SCHEMA FOR SUPABASE
-- Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
-- ============================================================================

-- Table 1: ESTATES (Dimension)
CREATE TABLE IF NOT EXISTS estates (
    id SERIAL PRIMARY KEY,
    estate_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_estates_code ON estates(estate_code);

-- Table 2: BLOCKS (Master Data)
CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) UNIQUE NOT NULL,
    estate_code VARCHAR(50) REFERENCES estates(estate_code),
    area_ha DECIMAL(10, 2),
    year_planted INTEGER,
    number INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blocks_code ON blocks(block_code);
CREATE INDEX idx_blocks_estate ON blocks(estate_code);
CREATE INDEX idx_blocks_year ON blocks(year_planted);

-- Table 3: PRODUCTION_DATA (Fact Table from Gabungan)
CREATE TABLE IF NOT EXISTS production_data (
    id INTEGER PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL REFERENCES blocks(block_code),
    -- Add all production metrics columns here (c001-c056, p001-p115, etc.)
    -- Example columns:
    -- c001 DECIMAL(15, 6),
    -- c002 DECIMAL(15, 6),
    -- ... (add all your specific columns)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    data_source VARCHAR(255)
);

CREATE INDEX idx_production_block ON production_data(block_code);

-- Table 4: REALISASI_POTENSI (Fact Table - Time Series)
CREATE TABLE IF NOT EXISTS realisasi_potensi (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL REFERENCES blocks(block_code),
    -- Add year-specific columns here
    -- Example structure for each year (2014-2025):
    -- year_2014_real DECIMAL(15, 2),
    -- year_2014_potensi DECIMAL(15, 2),
    -- year_2014_variance DECIMAL(15, 2),
    -- ... repeat for each year
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_realisasi_block ON realisasi_potensi(block_code);

-- Create view for easy joining
CREATE OR REPLACE VIEW v_complete_data AS
SELECT 
    b.block_code,
    b.estate_code,
    e.estate_code as estate_name,
    b.area_ha,
    b.year_planted,
    pd.*,
    rp.*
FROM blocks b
LEFT JOIN estates e ON b.estate_code = e.estate_code
LEFT JOIN production_data pd ON b.block_code = pd.block_code
LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code;

-- Row Level Security (RLS) - Optional
ALTER TABLE estates ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE production_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE realisasi_potensi ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (adjust per your needs)
CREATE POLICY "Enable read access for all users" ON estates FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON blocks FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON production_data FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON realisasi_potensi FOR SELECT USING (true);
"""

# Save SQL schema
with open('output/normalized_schema.sql', 'w', encoding='utf-8') as f:
    f.write(sql_schema)

print("✓ Generated: output/normalized_schema.sql")
print("\nSchema includes:")
print("  - 4 normalized tables (estates, blocks, production_data, realisasi_potensi)")
print("  - Indexes for performance")
print("  - Foreign key relationships")
print("  - View for easy data access")
print("  - RLS policies (optional)")

# ============================================================================
# STEP 6: EXPORT NORMALIZED CSV FILES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: EXPORTING NORMALIZED CSV FILES")
print("=" * 100)

# Export each table
df_estates.to_csv('output/normalized_estates.csv', index=False)
print(f"✓ Exported: output/normalized_estates.csv ({df_estates.shape[0]} rows)")

df_blocks.to_csv('output/normalized_blocks.csv', index=False)
print(f"✓ Exported: output/normalized_blocks.csv ({df_blocks.shape[0]} rows)")

df_production.to_csv('output/normalized_production_data.csv', index=False)
print(f"✓ Exported: output/normalized_production_data.csv ({df_production.shape[0]} rows)")

df_realisasi.to_csv('output/normalized_realisasi_potensi.csv', index=False)
print(f"✓ Exported: output/normalized_realisasi_potensi.csv ({df_realisasi.shape[0]} rows)")

# ============================================================================
# STEP 7: GENERATE UPLOAD GUIDE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: GENERATING UPLOAD GUIDE")
print("=" * 100)

upload_guide = f"""
# NORMALIZED DATA UPLOAD GUIDE

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 NORMALIZATION SUMMARY

### Original Structure:
- **Single table**: 645 rows × 301 columns
- **Size**: {original_size:.2f} MB
- **Issues**: Very wide, hard to maintain, redundant data

### Normalized Structure:
- **4 tables**: estates, blocks, production_data, realisasi_potensi
- **Total size**: {normalized_size:.2f} MB
- **Benefits**: Easier queries, better performance, maintainable

---

## 🎯 UPLOAD SEQUENCE (IMPORTANT!)

**Follow this order due to foreign key dependencies:**

### 1. Upload ESTATES first (Dimension Table)
```bash
# File: output/normalized_estates.csv
# Table: estates
# Rows: {df_estates.shape[0]}
# Columns: {df_estates.shape[1]} (id, estate_code)
```

**Supabase Upload:**
1. Go to Supabase Dashboard → Table Editor
2. Click "New Table" → Name: `estates`
3. Import CSV: `normalized_estates.csv`
4. Set `id` as Primary Key
5. Set `estate_code` as UNIQUE

### 2. Upload BLOCKS second (Master Data)
```bash
# File: output/normalized_blocks.csv
# Table: blocks
# Rows: {df_blocks.shape[0]}
# Columns: {df_blocks.shape[1]} (id, block_code, estate_code, area_ha, etc.)
```

**Supabase Upload:**
1. Create Table: `blocks`
2. Import CSV: `normalized_blocks.csv`
3. Set `id` as Primary Key
4. Set `block_code` as UNIQUE
5. Add Foreign Key: `estate_code` → `estates.estate_code`

### 3. Upload PRODUCTION_DATA third (Fact Table)
```bash
# File: output/normalized_production_data.csv
# Table: production_data
# Rows: {df_production.shape[0]}
# Columns: {df_production.shape[1]}
```

**Supabase Upload:**
1. Create Table: `production_data`
2. Import CSV: `normalized_production_data.csv`
3. Set `id` as Primary Key
4. Add Foreign Key: `block_code` → `blocks.block_code`

### 4. Upload REALISASI_POTENSI last (Fact Table)
```bash
# File: output/normalized_realisasi_potensi.csv
# Table: realisasi_potensi
# Rows: {df_realisasi.shape[0]}
# Columns: {df_realisasi.shape[1]}
```

**Supabase Upload:**
1. Create Table: `realisasi_potensi`
2. Import CSV: `normalized_realisasi_potensi.csv`
3. Set `id` as Primary Key
4. Add Foreign Key: `block_code` → `blocks.block_code`

---

## 📝 QUERY EXAMPLES

### Example 1: Get all data for a specific block
```sql
SELECT 
    b.*,
    e.estate_code as estate_name,
    pd.*,
    rp.*
FROM blocks b
LEFT JOIN estates e ON b.estate_code = e.estate_code
LEFT JOIN production_data pd ON b.block_code = pd.block_code
LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code
WHERE b.block_code = 'A001A';
```

### Example 2: Get all blocks for an estate
```sql
SELECT * FROM blocks 
WHERE estate_code = 'AME001'
ORDER BY block_code;
```

### Example 3: Get production data with block info
```sql
SELECT 
    b.block_code,
    b.estate_code,
    b.area_ha,
    pd.*
FROM production_data pd
JOIN blocks b ON pd.block_code = b.block_code
WHERE b.estate_code = 'AME001';
```

### Example 4: Compare realisasi vs potensi
```sql
SELECT 
    b.block_code,
    b.estate_code,
    rp.*
FROM realisasi_potensi rp
JOIN blocks b ON rp.block_code = b.block_code
ORDER BY b.estate_code, b.block_code;
```

---

## ✅ ADVANTAGES OF NORMALIZED SCHEMA

1. **Performance**
   - Smaller tables = faster queries
   - Targeted indexes on specific columns
   - Less data to scan

2. **Maintainability**
   - Clear data boundaries
   - Easy to update specific metrics
   - Reduced redundancy

3. **Scalability**
   - Add new tables without affecting existing ones
   - Easy to extend with new metrics
   - Flexible schema evolution

4. **Data Integrity**
   - Foreign key constraints ensure consistency
   - No orphaned records
   - Referential integrity maintained

5. **Flexibility**
   - Query only what you need
   - Join tables as required
   - Create views for common patterns

---

## 🔄 ALTERNATIVE: Use View for Compatibility

If you still need the "wide table" format for some analysis:

```sql
-- Create a view that mimics the original merged structure
CREATE OR REPLACE VIEW v_merged_data AS
SELECT 
    b.id as block_id,
    b.block_code,
    b.estate_code,
    b.area_ha,
    b.year_planted,
    pd.*,
    rp.*
FROM blocks b
LEFT JOIN production_data pd ON b.block_code = pd.block_code
LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code;

-- Then query like a normal table:
SELECT * FROM v_merged_data WHERE estate_code = 'AME001';
```

**Benefits of View:**
- Acts like merged table for queries
- Data stays normalized in background
- Best of both worlds!

---

## 📞 NEXT STEPS

Choose your approach:

### Option A: Normalized Upload (RECOMMENDED) ✅
- Upload 4 separate CSVs in order
- Better for long-term maintenance
- Optimal performance
- **Files ready in output/ directory**

### Option B: Merged Upload (Simple)
- Upload single merged CSV
- Easier initial setup
- Can normalize later
- Use `merged_full_data.csv`

### Option C: Hybrid (Best of Both)
- Upload normalized tables
- Create view for compatibility
- Recommended for production

---

**Status**: ✅ Normalization Complete - Ready for Upload

Choose Option A for best practices! 🚀
"""

with open('output/normalized_upload_guide.md', 'w', encoding='utf-8') as f:
    f.write(upload_guide)

print("✓ Generated: output/normalized_upload_guide.md")

#============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("NORMALIZATION ANALYSIS COMPLETE!")
print("=" * 100)

print(f"""
📊 SUMMARY:

Original Merged Data:
  - 1 table: {df_merged.shape[0]} rows × {df_merged.shape[1]} columns
  - Size: {original_size:.2f} MB
  - Issues: Very wide, denormalized

Normalized Schema:
  - 4 tables: {df_estates.shape[0] + df_blocks.shape[0] + df_production.shape[0] + df_realisasi.shape[0]} total rows
  - Size: {normalized_size:.2f} MB
  - Benefits: Maintainable, performant, scalable

📁 Files Generated:
  ✓ normalized_estates.csv ({df_estates.shape[0]} rows)
  ✓ normalized_blocks.csv ({df_blocks.shape[0]} rows)
  ✓ normalized_production_data.csv ({df_production.shape[0]} rows)
  ✓ normalized_realisasi_potensi.csv ({df_realisasi.shape[0]} rows)
  ✓ normalized_schema.sql (PostgreSQL/Supabase schema)
  ✓ normalized_upload_guide.md (Complete guide)

🎯 RECOMMENDATION:
  Upload normalized files for BEST PRACTICES!
  - Easier to maintain
  - Better performance
  - More flexible for analysis

""")

print("Ready to upload! Check output/ directory for all files.")
print("=" * 100)
