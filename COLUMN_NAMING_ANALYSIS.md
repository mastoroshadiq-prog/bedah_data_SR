# 📌 COLUMN NAMING STRATEGY & RECOMMENDATIONS

## ⚠️ **MASALAH: Cryptic Column Names**

Anda benar! Column names seperti `c007`, `c008`, `p106`, `p107` **SANGAT TIDAK IDEAL** untuk production database.

### **Contoh Query dengan Names Ini:**
```sql
-- ❌ Tidak jelas maksudnya
SELECT c007, c008, p106 
FROM production_data 
WHERE c007 > 100;
```

6 bulan kemudian:
- "c007 itu apa ya?" 😕
- "p106 maksudnya apa?" 🤔
- Sulit untuk onboarding developer baru
- Maintenance jadi nightmare

---

## 📋 **ASAL-USUL COLUMN NAMES**

Column names cryptic ini terjadi karena:

### **Dari Original Excel:**
1. **data_gabungan.xlsx** - Tidak punya proper headers
2. **Realisasi vs Potensi PT SR.xlsx** - Multi-row header yang complex

### **Saat Preprocessing:**
Saya generate automatic names:
- **c001-c156** = Columns dari Data Gabungan (`c` = column auto-generated)
- **p001-p119** = Columns dari Realisasi Potensi (`p` = potensi auto-generated)

---

## ✅ **SOLUSI: 3 OPTIONS**

### **OPTION 1: Column Mapping Dictionary** ⭐ (RECOMMENDED - Quick Fix)

Buat mapping dictionary untuk reference di code/documentation:

```python
# column_mapping.py
PRODUCTION_DATA_COLUMNS = {
    # Core identifiers
    'id': 'Unique identifier',
    'block_code': 'Block identifier (e.g., A001A)',
    
    # Original data_gabungan columns
    'c001': 'Estate name (e.g., AME)',
    'c002': 'Estate group',
    'c003': 'Estate code level 1',
    'c004': 'Estate code level 2',
    'c005': 'Block prefix',
    'c006': 'Block full code',
    'c007': 'Year planted',
    'c008': 'Seed variety',
    'c009': 'Block area (ha)',
    # ... continue mapping
    
    # Realisasi potensi columns
    'p001': 'Estate code',
    'p002': 'Block code',
    'p003': 'Area planted (ha)',
    'p106': 'BJR weight (Kg) - Year X',
    'p107': 'Yield tons - Year Y',
    # ... continue mapping
}

REALISASI_POTENSI_COLUMNS = {
    'id': 'Unique identifier',
    'block_code': 'Block identifier',
    # Actual columns to be mapped based on original Excel
}
```

**Usage:**
```python
# In documentation or code comments
column_name = 'c007'
description = PRODUCTION_DATA_COLUMNS.get(column_name, 'Unknown')
print(f"{column_name}: {description}")  # "c007: Year planted"
```

---

### **OPTION 2: Create SQL Views dengan Meaningful Names** (Best for Queries)

```sql
-- Create a view with meaningful column names
CREATE VIEW vw_production_readable AS
SELECT 
    id,
    block_code,
    c001 AS estate_name,
    c002 AS estate_group,
    c003 AS estate_code_l1,
    c004 AS estate_code_l2,
    c005 AS block_prefix,
    c006 AS block_full_code,
    c007 AS year_planted,
    c008 AS seed_variety,
    c009 AS block_area_ha,
    c011 AS cultivated_area_ha,
    -- Continue with meaningful names
    p106 AS bjr_weight_kg_yearX,
    p107 AS yield_tons_yearY
FROM production_data;

-- Now query is readable:
SELECT year_planted, seed_variety, yield_tons_yearY
FROM vw_production_readable
WHERE year_planted > 2010;
```

✅ **Keuntungan:**
- Original table tetap c001-c156 (tidak perlu migrate data)
- Queries jadi readable
- Easy to maintain
- No data migration risk

---

### **OPTION 3: Rename Columns di Database** (Risky - NOT RECOMMENDED NOW)

```sql
-- Rename actual columns (CAREFUL!)
ALTER TABLE production_data 
RENAME COLUMN c007 TO year_planted;

ALTER TABLE production_data 
RENAME COLUMN c008 TO seed_variety;

-- ... etc for all 156 columns
```

❌ **Masalah:**
- Risky jika ada existing queries
- Need to migrate 645 rows × 156 columns
- Bisa error di tengah jalan
- Need downtime

---

## 🎯 **RECOMMENDED APPROACH**

### **SHORT TERM (Sekarang):**

1. **Create Column Mapping Document**
   ```markdown
   # production_data.csv Column Reference
   
   | Column Code | Meaningful Name | Description | Example |
   |-------------|----------------|-------------|---------|
   | c007 | year_planted | Tahun tanam | 2012 |
   | c008 | seed_variety | Varietas bibit | Topaz, PPKS |
   | c009 | block_area_ha | Luas blok (Ha) | 7.7 |
   | p106 | bjr_weight_kg | Berat BJR (Kg) | 1002.0 |
   | p107 | yield_tons | Produksi (Ton) | 130.12 |
   ```

2. **Use Views for Queries**
   - Create readable views di Supabase
   - Team query ke views, bukan ke raw table

### **LONG TERM (Nanti jika diperlukan):**

1. **Proper Data Re-import dengan Correct Headers**
   - Go back to source Excel files
   - Identify proper column meanings
   - Re-run preprocessing dengan proper column names
   - Re-upload dengan meaningful names

---

## 📖 **CARA IDENTIFIKASI ACTUAL MEANINGS**

Untuk membuat mapping yang benar, kita perlu:

### **Step 1: Check Original Excel Headers**
```python
import pandas as pd

# Check data_gabungan actual structure
df_gabungan = pd.read_excel('data_gabungan.xlsx')
print("Original columns:", df_gabungan.columns.tolist())

# Check realisasi structure  
df_realisasi = pd.read_excel('Realisasi vs Potensi PT SR.xlsx', header=9)
print("Realisasi columns:", df_realisasi.columns.tolist())
```

### **Step 2: Sample Data Analysis**
```python
# Look at sample data to infer meaning
df_production = pd.read_csv('output/normalized_production_data.csv', nrows=5)
print(df_production[['c007', 'c008', 'c009']].head())

# c007: Shows years like 2012, 2010 → year_planted
# c008: Shows text like 'Topaz', 'PPKS' → seed_variety
# c009: Shows decimals like 7.7, 30.0 → area_ha
```

---

## 💡 **IMMEDIATE ACTION ITEMS**

### **1. Create Mapping Document (30 minutes)**
Mari saya bantu create initial mapping based on sample data I saw:

**Known Mappings:**
- `c001` → Estate name (AME)
- `c002` → Estate group (AME)
- `c003` → Estate level 1 (AME01)
- `c004` → Estate code (AME001)
- `c005` → Block prefix (A 01, C 06)
- `c006` → Block code (A001A, C006A)
- `c007` → Year planted (2012, 2010)
- `c008` → Seed variety (Topaz, PPKS, Slpn. Jaya)
- `c009` → Block area Ha (7.7, 30.0)

### **2. Create SQL Views (10 minutes)**
```sql
-- vw_production_readable.sql
CREATE OR REPLACE VIEW vw_production_summary AS
SELECT 
    id,
    block_code,
    c007 AS year_planted,
    c008 AS seed_variety,
    c009 AS block_area_ha,
    c011 AS cultivated_area_ha
FROM production_data;
```

### **3. Update Dashboard to Use Views**
```python
# In dashboard_app.py
# Instead of:
# df = supabase.table('production_data').select('*')

# Use:
df = supabase.table('vw_production_summary').select('*')
```

---

## ❓ **WHAT DO YOU PREFER?**

**A)** Saya bantu create complete column mapping document dulu

**B)** Create SQL views dengan meaningful names sekarang

**C)** Go back to source Excel dan re-preprocess dengan proper headers

**D)** Tetap pakai c001-c156 for now, document later

Mana yang Anda pilih? Saya akan bantu implement! 😊

---

**Bottom Line:** Anda 100% benar bahwa cryptic names adalah problem. Option 1 (Mapping Doc) + Option 2 (SQL Views) adalah best immediate solution tanpa risk data migration.
