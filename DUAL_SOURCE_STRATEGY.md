# 🎯 COMPREHENSIVE DATA STRATEGY - DUAL SOURCE APPROACH

## ❓ **USER CONCERN**

**Question:** "Jika kita gunakan Realisasi vs Potensi PT SR.xlsx, apakah hanya data produksi saja? 
Bagaimana dengan data SPH, ganoderma, TBM, kentosan, sisipan?"

**Answer:** **CORRECT!** Kita perlu **BOTH files** untuk data lengkap!

---

## 📊 **DATA DISTRIBUTION STRATEGY**

### **APPROACH: Dual-Source Integration** ✅

```
┌─────────────────────────────────────────────────────────────┐
│  DATA SOURCE MAPPING                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 data_gabungan.xlsx (177 cols)                           │
│  ├── ✅ SPH (Standar Pokok per Hektar)                      │
│  ├── ✅ Ganoderma (Stadium 1-4)                             │
│  ├── ✅ TBM (Tanaman Belum Menghasilkan)                    │
│  ├── ✅ Kentosan                                            │
│  ├── ✅ Sisipan                                             │
│  ├── ✅ Planting history (2009-2025)                        │
│  ├── ✅ Land infrastructure                                 │
│  ├── ⚠️  Production data (might be older/less detailed)     │
│  └── ⚠️  Has F005A duplicate                                │
│                                                              │
│  📁 Realisasi vs Potensi PT SR.xlsx (116 cols)              │
│  ├── ✅ Production data (DETAILED, LATEST)                  │
│  ├── ✅ Realisasi (Real BJR, Janjang, Ton)                  │
│  ├── ✅ Potensi (Target BJR, Janjang, Ton)                  │
│  ├── ✅ Gap analysis ready                                  │
│  ├── ✅ Separated Inti/Plasma                               │
│  ├── ✅ Multi-year (2023-2025)                              │
│  └── ❌ Missing: SPH, Ganoderma, TBM, etc.                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ **RECOMMENDED SOLUTION**

### **Use BOTH Files with Clear Separation** 🎯

```
Source 1: data_gabungan.xlsx
Purpose: METADATA & OPERATIONAL DATA
Extract:
  ├── SPH (per block)
  ├── Ganoderma stadium 1-4 (per block)
  ├── TBM count
  ├── Kentosan (total per block)
  ├── Sisipan (total per block)
  ├── Planting history (yearly 2009-2025)
  └── Land infrastructure

→ Tables:
   - block_land_infrastructure
   - block_planting_history
   - block_pest_disease
   - block_planting_yearly

Source 2: Realisasi vs Potensi PT SR.xlsx
Purpose: PRODUCTION DATA (PRIMARY)
Extract:
  ├── Monthly production 2023-2025
  ├── Realisasi vs Potensi
  ├── Gap analysis
  └── Inti + Plasma separation

→ Table:
   - production_monthly (2023-2025)
```

---

## 📋 **REVISED NORMALIZATION PLAN**

### **Phase 1: Foundation** (unchanged)
```
✅ estates.csv (13 rows)
✅ blocks.csv (592 rows)
```

### **Phase 2: Metadata from data_gabungan.xlsx**
```
Source: data_gabungan.xlsx
Extract:
1. block_land_infrastructure.csv
   - SPH, land area, infrastructure
   
2. block_pest_disease.csv
   - Ganoderma stadium_1_2
   - Ganoderma stadium_3_4
   - Total serangan, % serangan
   
3. block_planting_history.csv
   - Komposisi pokok 2009-2019
   - TBM count
   
4. block_planting_yearly.csv
   - Yearly: Tanam, Sisip, Kentosan
   - Years: 2020-2025
```

### **Phase 3: Production from Realisasi vs Potensi PT SR.xlsx**
```
Source: Realisasi vs Potensi PT SR.xlsx
Sheets: Both (Inti + Plasma)
Years: 2023, 2024, 2025

Extract:
production_monthly.csv
   - block_id
   - block_category (Inti/Plasma)
   - year (2023/2024/2025)
   - month (Jan-Dec)
   - real_bjr_kg, real_jum_jjg, real_ton
   - potensi_bjr_kg, potensi_jum_jjg, potensi_ton
   - gap_bjr_kg, gap_jum_jjg, gap_ton
   - gap_pct_bjr, gap_pct_jjg, gap_pct_ton
```

---

## 🔄 **DATA RECONCILIATION**

### **Handling Block Mismatches:**

```python
# Step 1: Get blocks from both sources
blocks_gabungan = extract_blocks('data_gabungan.xlsx')  # 649 blocks
blocks_realisasi = extract_blocks('Realisasi PT SR.xlsx')  # 628 blocks

# Step 2: Identify differences
missing_in_realisasi = blocks_gabungan - blocks_realisasi  # 21 blocks
missing_in_gabungan = blocks_realisasi - blocks_gabungan   # Check if any

# Step 3: Decision
For metadata (SPH, Ganoderma, etc.):
  → Use data_gabungan.xlsx for ALL blocks (649)
  → Skip F005A duplicate (keep first occurrence)
  
For production data:
  → Use Realisasi PT SR.xlsx for blocks present (628)
  → For missing 21 blocks:
      Option A: Use production from data_gabungan.xlsx if available
      Option B: Mark as "no production data" (NULL)
      Option C: Exclude from production_monthly table
```

### **Handling F005A Duplicate:**

```python
# In data_gabungan.xlsx
df = pd.read_excel('data_gabungan.xlsx')
df_deduplicated = df.drop_duplicates(subset=['block_code'], keep='first')
# Use deduplicated data for extraction
```

---

## 📊 **FINAL DATABASE SCHEMA**

### **7 Tables (as planned):**

```sql
1. estates (13 rows)
   └── From: existing normalized_estates_v2.csv

2. blocks (592-649 rows - to be confirmed)
   └── From: Merged from both sources

3. block_land_infrastructure (same as blocks)
   ├── Source: data_gabungan.xlsx
   └── Columns: SPH, land areas, infrastructure

4. block_planting_history (~7,000 rows = blocks × 11 years)
   ├── Source: data_gabungan.xlsx
   ├── Years: 2009-2019 (komposisi pokok)
   └── Includes: TBM count per year

5. block_pest_disease (same as blocks)
   ├── Source: data_gabungan.xlsx
   └── Columns: Ganoderma stadium 1-4, total, %

6. block_planting_yearly (~3,700 rows = blocks × 6 years)
   ├── Source: data_gabungan.xlsx
   ├── Years: 2020-2025
   └── Columns: Tanam, Sisip, Kentosan per year

7. production_monthly (~22,000 rows = 628 blocks × 3 years × 12 months)
   ├── Source: Realisasi vs Potensi PT SR.xlsx
   ├── Years: 2023, 2024, 2025
   ├── Both sheets: Inti + Plasma
   └── Columns: Real, Potensi, Gap (BJR, Janjang, Ton)
```

---

## 🎯 **EXTRACTION SEQUENCE**

### **Step 1: Prepare Blocks Master List**
```python
# Merge blocks from both sources
# Handle F005A duplicate
# Create master blocks.csv
```

### **Step 2: Extract Metadata (data_gabungan.xlsx)**
```python
# Tables 3, 4, 5, 6
# SPH, Ganoderma, Planting history, TBM, Kentosan, Sisipan
```

### **Step 3: Extract Production (Realisasi PT SR.xlsx)**
```python
# Table 7
# Years: 2023, 2024, 2025
# Both Inti + Plasma
# Monthly data with Gap analysis
```

### **Step 4: Validate & Cross-check**
```python
# Ensure all foreign keys valid
# Check for missing data
# Validate calculations
```

---

## ✅ **ADVANTAGES OF THIS APPROACH**

1. **Complete Data Coverage**
   - Production: Latest & detailed from Realisasi PT SR
   - Metadata: Comprehensive from data_gabungan
   
2. **Best of Both Worlds**
   - Specialized production analysis (Realisasi PT SR)
   - Rich operational data (data_gabungan)
   
3. **Clean Separation**
   - Production = time-series (monthly)
   - Metadata = semi-static (block attributes)
   
4. **Scalability**
   - Easy to update production monthly
   - Metadata stable, updated less frequently

---

## ❓ **CONFIRMATION NEEDED**

**Please confirm:**

1. ✅ **Use BOTH files as described?**
   - data_gabungan.xlsx → Metadata (SPH, Ganoderma, TBM, etc.)
   - Realisasi PT SR.xlsx → Production (2023-2025)

2. ✅ **For missing 21 blocks in Realisasi file:**
   - Option A: Use production from data_gabungan.xlsx
   - Option B: Skip (no production data)
   - Option C: Mark as "data unavailable"

3. ✅ **F005A duplicate handling:**
   - Keep first occurrence only? ✅

4. ✅ **Block count priority:**
   - Use all 649 blocks for metadata?
   - Use 628 blocks for production?

---

## 🚀 **READY TO PROCEED?**

Once confirmed, I will:
1. ✅ Create block reconciliation script
2. ✅ Extract metadata from data_gabungan.xlsx
3. ✅ Extract production from Realisasi PT SR.xlsx
4. ✅ Generate all 7 normalized tables
5. ✅ Create SQL schema
6. ✅ Prepare for Supabase upload

**Your decision?** 🎯
