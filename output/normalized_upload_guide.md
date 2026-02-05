
# NORMALIZED DATA UPLOAD GUIDE

Generated: 2026-02-03 11:29:12

---

## 📊 NORMALIZATION SUMMARY

### Original Structure:
- **Single table**: 645 rows × 301 columns
- **Size**: 3.26 MB
- **Issues**: Very wide, hard to maintain, redundant data

### Normalized Structure:
- **4 tables**: estates, blocks, production_data, realisasi_potensi
- **Total size**: 1.79 MB
- **Benefits**: Easier queries, better performance, maintainable

---

## 🎯 UPLOAD SEQUENCE (IMPORTANT!)

**Follow this order due to foreign key dependencies:**

### 1. Upload ESTATES first (Dimension Table)
```bash
# File: output/normalized_estates.csv
# Table: estates
# Rows: 14
# Columns: 2 (id, estate_code)
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
# Rows: 641
# Columns: 6 (id, block_code, estate_code, area_ha, etc.)
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
# Rows: 645
# Columns: 156
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
# Rows: 616
# Columns: 52
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
