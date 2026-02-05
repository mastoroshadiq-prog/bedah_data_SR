# 📊 EXCEL FILES COMPARISON & RECOMMENDATION

## 📁 **FILE COMPARISON RESULTS**

### **File 1: data_gabungan.xlsx**
```
Location: source/data_gabungan.xlsx
Sheets: 1 (Lembar1)
Dimensions: 649 rows × 177 columns
✅ Pros:
  - More columns (177 vs 116) - likely more comprehensive
  - More rows (649 vs 628) - includes more blocks
  - Single sheet - easier to process
  
⚠️ Cons:
  - Has duplicate block F005A (need to handle)
  - Might have redundant data
```

### **File 2: Realisasi vs Potensi PT SR.xlsx**
```
Location: source/Realisasi vs Potensi PT SR.xlsx
Sheets: 2
  1. Real VS Potensi Inti (628 rows × 116 columns)
  2. Real VS Potensi Plasma
Dimensions: 628 rows × 116 columns (first sheet)
✅ Pros:
  - Focused on Realisasi vs Potensi (perfect for your use case!)
  - Separated Inti vs Plasma (clear categorization)
  - Clean structure (116 cols - manageable)
  - No duplicate issues mentioned
  
⚠️ Cons:
  - Fewer rows (might miss some blocks)
  - Fewer columns (might miss some data fields)
```

---

## 🎯 **RECOMMENDATION**

### **Primary Choice: Realisasi vs Potensi PT SR.xlsx** ✅

**Reasons:**
1. **Purpose-built** untuk Realisasi vs Potensi analysis
2. **Cleaner data** - no duplicates
3. **Organized** - separated by Inti/Plasma
4. **Focused** - 116 columns more manageable than 177
5. **Name suggests** this is specifically for production data

**But we should:**
- ✅ Use untuk production data (2023, 2024, 2025)
- ✅ Process both sheets (Inti + Plasma)
- ✅ Verify tahun 2023-2025 ada di file ini

### **Secondary/Complementary: data_gabungan.xlsx**

**Use for:**
- Missing blocks (21 blocks difference: 649 - 628 = 21)
- Cross-validation
- Additional metadata columns

**Handle F005A duplicate:**
- Keep first occurrence only
- Or choose based on completeness

---

## 📋 **EXTRACTION PLAN**

### **Step 1: Extract from "Realisasi vs Potensi PT SR.xlsx"**

```python
# Sheet 1: Real VS Potensi Inti
df_inti_2023 = extract_year(sheet='Real VS Potensi Inti', year=2023)
df_inti_2024 = extract_year(sheet='Real VS Potensi Inti', year=2024)
df_inti_2025 = extract_year(sheet='Real VS Potensi Inti', year=2025)

# Sheet 2: Real VS Potensi Plasma
df_plasma_2023 = extract_year(sheet='Real VS Potensi Plasma', year=2023)
df_plasma_2024 = extract_year(sheet='Real VS Potensi Plasma', year=2024)
df_plasma_2025 = extract_year(sheet='Real VS Potensi Plasma', year=2025)

# Combine
df_all = pd.concat([df_inti_2023, df_inti_2024, df_inti_2025,
                    df_plasma_2023, df_plasma_2024, df_plasma_2025])
```

### **Step 2: Structure untuk production_monthly**

```
Target: production_monthly table

Expected rows: ~21,000 rows
- 628 blocks (Inti + Plasma)
- × 3 years (2023, 2024, 2025)
- × 12 months
- = 628 × 3 × 12 = 22,608 rows

Columns:
- id (auto)
- block_id (FK to blocks table)
- block_category (Inti/Plasma) 
- year (2023/2024/2025)
- month (Jan-Dec)
- real_bjr_kg
- real_jum_jjg
- real_ton
- potensi_bjr_kg
- potensi_jum_jjg
- potensi_ton
- gap_bjr_kg (real - potensi)
- gap_jum_jjg
- gap_ton
- gap_pct_bjr ((real-potensi)/potensi × 100)
- gap_pct_jjg
- gap_pct_ton
- created_at
```

### **Step 3: Cross-check with data_gabungan.xlsx**

```python
# Identify missing blocks
blocks_in_realisasi = set(df_realisasi['block_code'])
blocks_in_gabungan = set(df_gabungan['block_code'])

missing_blocks = blocks_in_gabungan - blocks_in_realisasi
# 21 blocks might be here

# Extract production data for missing blocks from data_gabungan
if missing_blocks:
    df_missing = extract_from_gabungan(missing_blocks, years=[2023,2024,2025])
    df_all = pd.concat([df_all, df_missing])
```

---

## ✅ **NEXT ACTIONS**

### **Immediate (Need to verify):**

1. ✅ **Check year structure** in both files
   - Are years in separate sheets?
   - Are years in columns (e.g., Jan-2023, Feb-2023, etc.)?
   - Are years stacked in rows?

2. ✅ **Verify 2023-2025 data exists**
   - Load sample data
   - Identify year columns/patterns
   - Confirm all 3 years present

3. ✅ **Map columns to our schema**
   - Identify BJR columns
   - Identify Jumlah Janjang columns
   - Identify Ton columns
   - Separate Real vs Potensi

### **Script to Create:**

```
extract_production_2023_2025.py
├── Load: Realisasi vs Potensi PT SR.xlsx
├── Extract: Years 2023, 2024, 2025
├── Transform: WIDE → LONG format
├── Add: Gap calculations
├── Output: production_2023_2025_raw.csv
└── Validate: Row counts, data completeness
```

---

## 🎯 **DECISION NEEDED**

**Konfirmasi yang saya butuhkan:**

1. ✅ **Setuju gunakan "Realisasi vs Potensi PT SR.xlsx" as primary source?**
2. ✅ **Process both sheets (Inti + Plasma)?**
3. ✅ **Tambahkan missing 21 blocks dari data_gabungan.xlsx?**
4. ✅ **Prioritas: Extract 2023-2025 dulu, atau include semua tahun sejak 2014 untuk archive?**

---

## 📌 **MY RECOMMENDATION**

**Start with:**
1. Use **"Realisasi vs Potensi PT SR.xlsx"** ✅
2. Extract **years 2023, 2024, 2025** only
3. Process **both Inti + Plasma** sheets
4. Cross-check **missing blocks** with data_gabungan.xlsx
5. **Skip duplicate F005A** (use first occurrence)

**This will give you:**
- Clean 3-year production trend data
- Realisasi vs Potensi comparison
- Gap analysis ready
- ~22,000 rows of monthly production data

**Lanjutkan?** 🚀
