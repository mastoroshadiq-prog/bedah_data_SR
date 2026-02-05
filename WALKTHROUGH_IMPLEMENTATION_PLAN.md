# 🎯 WALKTHROUGH IMPLEMENTATION PLAN
## Normalisasi Data: 156 Kolom → 7 Normalized Tables

---

## 📋 **OVERVIEW**

**Goal:** Transform `normalized_production_data_COMPLETE.csv` (156 columns) menjadi 7 normalized tables yang database-ready.

**Timeline:** 3-4 fase, bisa diselesaikan bertahap
**Approach:** Incremental, dengan validation di setiap fase

---

## 🚀 **PHASE 1: Foundation & Core Tables**
**Duration:** ~15 menit
**Risk:** Low
**Deliverables:** 3 core tables + SQL schema

### **1.1 Preparation** ✅
```
Input:
- normalized_production_data_COMPLETE.csv (156 columns)
- column_name_mapping_fixed.csv (mapping dictionary)

Tasks:
□ Load and inspect data
□ Identify column groups
□ Create mapping strategy
```

### **1.2 Create Core Tables** ✅
```
Output Files:
1. estates.csv (13 rows)
   - id, estate_code, division_code
   
2. blocks.csv (592 rows)
   - id, estate_id, block_code, block_code_new
   - year_planted, seed_variety, area_ha
   
3. block_land_infrastructure.csv (592 rows)
   - id, block_id
   - luas_tanam_sd_2024_ha, penambahan_luas_ha
   - total_luas_sd_2025_ha, empls, bbt, pks
   - jalan_parit_ha, areal_cadangan_ha, total_luas_keseluruhan_ha

SQL Schema:
- phase1_schema.sql
```

### **1.3 Validation** ✅
```
Checks:
□ Row counts match expectations
□ No NULL in primary keys
□ Foreign keys integrity
□ No duplicate IDs
□ Data types correct

Output:
- phase1_validation_report.md
```

**✅ Checkpoint:** Review hasil Phase 1 sebelum lanjut

---

## 🌱 **PHASE 2: Historical & Monitoring Data**
**Duration:** ~20 menit
**Risk:** Medium
**Deliverables:** 2 tables dengan time-series data

### **2.1 Planting History Transformation** 🔄
```
Transform FROM (Wide):
- realisasi_tanam_komposisi_pokok_2009 (1 column)
- realisasi_tanam_komposisi_pokok_2010 (1 column)
- ... (11 columns total untuk 2009-2019)
- tanam_2020, sisip_2020 (2 columns)
- ... (12 columns untuk 2020-2025)

Transform TO (Long):
block_planting_history.csv (~6,512 rows)
- id, block_id, year
- komposisi_pokok (untuk 2009-2019)
- tanam, sisip, sisip_kentosan (untuk 2020-2025)
- sph, total_pkk

Example transformation:
FROM:
| block_id | komposisi_2009 | komposisi_2010 | tanam_2020 | sisip_2020 |
|----------|----------------|----------------|------------|------------|
| 1        | 100            | 150            | 50         | 10         |

TO:
| id | block_id | year | komposisi_pokok | tanam | sisip |
|----|----------|------|-----------------|-------|-------|
| 1  | 1        | 2009 | 100             | NULL  | NULL  |
| 2  | 1        | 2010 | 150             | NULL  | NULL  |
| 3  | 1        | 2020 | NULL            | 50    | 10    |
```

### **2.2 Pest & Disease Data** 🐛
```
Output:
block_pest_disease.csv (592 rows)
- id, block_id, recorded_date
- serangan_ganoderma_stadium_1_2
- serangan_ganoderma_stadium_3_4  
- total_serangan, pct_serangan

Note: recorded_date = current date (snapshot)
```

### **2.3 SQL Schema Update** 📝
```
- phase2_schema.sql (append to phase1_schema)
- Add indexes for year columns
- Add constraints
```

### **2.4 Validation** ✅
```
Checks:
□ Total rows = blocks × years
□ No gaps in year sequence
□ Valid year range (2009-2025)
□ Foreign keys valid
□ Sum of yearly data matches totals

Output:
- phase2_validation_report.md
```

**✅ Checkpoint:** Review time-series data transformation

---

## 📊 **PHASE 3: Production Data (CRITICAL)**
**Duration:** ~30 menit
**Risk:** High (complex transformation)
**Deliverables:** 1 large table dengan monthly production data

### **3.1 Column Analysis** 🔍
```
Analyze production columns (64-156):
- Pattern: real_bjr_kg, jum_jjg, ton (repeating)
- Identify month groupings
- Map to month names (Jan, Feb, ..., Dec)

Create column mapping:
{
  'col_64_66': {'month': 'January', 
                'metrics': ['real_bjr_kg', 'real_jum_jjg', 'real_ton']},
  'col_67_69': {'month': 'January',
                'metrics': ['potensi_bjr_kg', 'potensi_jum_jjg', 'potensi_ton']},
  ...
}
```

### **3.2 WIDE → LONG Transformation** 🔄
```
Transform FROM (Wide):
156 columns with monthly data spread across:
- real_bjr_kg (12 months)
- real_jum_jjg (12 months)
- real_ton (12 months)
- potensi_bjr_kg (12 months)
- potensi_jum_jjg (12 months)
- potensi_ton (12 months)
- real_vs_potensi_bjr_kg (12 months)
- ... etc

Transform TO (Long):
production_monthly.csv (~7,104 rows = 592 blocks × 12 months)
- id, block_id, year, month
- real_bjr_kg, real_jum_jjg, real_ton
- potensi_bjr_kg, potensi_jum_jjg, potensi_ton
- gap_bjr_kg, gap_jum_jjg, gap_ton
- gap_pct_bjr, gap_pct_jjg, gap_pct_ton

Example:
FROM (1 row):
| block_id | jan_real_bjr | jan_real_jjg | feb_real_bjr | ... |
|----------|--------------|--------------|--------------|-----|
| 1        | 10.5         | 1000         | 11.2         | ... |

TO (12 rows):
| id | block_id | month | real_bjr_kg | real_jum_jjg | potensi_bjr_kg | gap_bjr_kg |
|----|----------|-------|-------------|--------------|----------------|------------|
| 1  | 1        | Jan   | 10.5        | 1000         | 12.0           | -1.5       |
| 2  | 1        | Feb   | 11.2        | 1100         | 13.0           | -1.8       |
| ...
```

### **3.3 Calculate Gap Metrics** 📈
```
For each monthly record:
gap_bjr_kg = real_bjr_kg - potensi_bjr_kg
gap_jum_jjg = real_jum_jjg - potensi_jum_jjg
gap_ton = real_ton - potensi_ton

gap_pct_bjr = (gap_bjr_kg / potensi_bjr_kg) × 100
gap_pct_jjg = (gap_jum_jjg / potensi_jum_jjg) × 100
gap_pct_ton = (gap_ton / potensi_ton) × 100
```

### **3.4 SQL Schema** 📝
```
- phase3_schema.sql
- Indexes on: block_id, year, month
- Partitioning consideration for large data
```

### **3.5 Validation** ✅
```
Checks:
□ Row count = 592 blocks × 12 months = 7,104 rows
□ All months present (Jan-Dec)
□ No NULL in core metrics
□ Gap calculations correct
□ Percentages in valid range
□ Foreign keys valid

Sample checks:
□ Sum(monthly_ton) ≈ expected annual production
□ No negative values where impossible
□ Realistic BJR values (5-15 kg range)

Output:
- phase3_validation_report.md
- production_data_statistics.md
```

**✅ Checkpoint:** CRITICAL - Verify production data accuracy!

---

## 🔗 **PHASE 4: Integration & Final Schema**
**Duration:** ~15 menit
**Risk:** Low
**Deliverables:** Complete SQL schema + upload guide

### **4.1 Merge All Schemas** 📋
```
Combine:
- phase1_schema.sql
- phase2_schema.sql  
- phase3_schema.sql

Into:
- supabase_complete_schema.sql

Add:
- Row Level Security policies
- Indexes for common queries
- Views for common joins
- Triggers (if needed)
```

### **4.2 Create Helper Views** 👁️
```sql
-- Complete block view
CREATE VIEW v_block_complete AS
SELECT 
    b.*,
    bli.*,
    e.estate_code,
    e.division_code
FROM blocks b
LEFT JOIN block_land_infrastructure bli ON b.id = bli.block_id
LEFT JOIN estates e ON b.estate_id = e.id;

-- Monthly production summary
CREATE VIEW v_production_summary AS
SELECT 
    block_id,
    year,
    month,
    real_ton,
    potensi_ton,
    gap_ton,
    gap_pct_ton
FROM production_monthly
ORDER BY block_id, year, month;
```

### **4.3 Generate Upload Scripts** 📤
```
Create:
1. upload_to_supabase.py
   - Batch upload dengan transaction
   - Progress tracking
   - Error handling
   - Rollback capability

2. verify_upload.py
   - Count verification
   - Integrity checks
   - Sample data comparison
```

### **4.4 Documentation** 📚
```
Create:
1. SCHEMA_DOCUMENTATION.md
   - Table descriptions
   - Column definitions
   - Relationships diagram
   - Sample queries

2. UPLOAD_GUIDE.md
   - Step-by-step upload process
   - Troubleshooting
   - Rollback procedures

3. API_USAGE_EXAMPLES.md
   - Common queries
   - Supabase client examples
   - Performance tips
```

### **4.5 Final Validation** ✅
```
Complete validation:
□ All 7 tables created
□ All row counts correct
□ All foreign keys valid
□ No orphaned records
□ All indexes created
□ Views working
□ Sample queries successful

Output:
- final_validation_report.md
- migration_summary.md
```

---

## 📊 **DELIVERABLES SUMMARY**

### **Files Created:**
```
📁 output/normalized_tables/
  ├── 1_core/
  │   ├── estates.csv (13 rows)
  │   ├── blocks.csv (592 rows)
  │   └── block_land_infrastructure.csv (592 rows)
  │
  ├── 2_historical/
  │   ├── block_planting_history.csv (~6,512 rows)
  │   └── block_pest_disease.csv (592 rows)
  │
  ├── 3_production/
  │   └── production_monthly.csv (~7,104 rows)
  │
  └── 4_schema/
      ├── supabase_complete_schema.sql
      ├── indexes.sql
      ├── views.sql
      └── policies.sql

📁 scripts/
  ├── phase1_create_core_tables.py
  ├── phase2_create_historical_tables.py
  ├── phase3_create_production_table.py
  ├── phase4_generate_schema.py
  ├── upload_to_supabase.py
  └── verify_upload.py

📁 validation/
  ├── phase1_validation_report.md
  ├── phase2_validation_report.md
  ├── phase3_validation_report.md
  ├── final_validation_report.md
  └── migration_summary.md

📁 docs/
  ├── SCHEMA_DOCUMENTATION.md
  ├── UPLOAD_GUIDE.md
  └── API_USAGE_EXAMPLES.md
```

---

## ⏱️ **ESTIMATED TIMELINE**

**Total Time:** ~1.5 - 2 hours (with reviews)

| Phase | Tasks | Time | Review |
|-------|-------|------|--------|
| Phase 1 | Core tables | 15 min | 5 min |
| Phase 2 | Historical data | 20 min | 10 min |
| Phase 3 | Production data | 30 min | 15 min |
| Phase 4 | Integration | 15 min | 10 min |
| **Total** | | **80 min** | **40 min** |

---

## 🎯 **EXECUTION APPROACH**

### **Option A: Sequential Execution** (Recommended)
```
1. Run Phase 1 → Review → Approve → Continue
2. Run Phase 2 → Review → Approve → Continue  
3. Run Phase 3 → Review → Approve → Continue
4. Run Phase 4 → Final Review → Upload to Supabase
```
**Pros:** Safe, easy to debug, rollback possible
**Cons:** Takes longer (need reviews)

### **Option B: Automated Pipeline**
```
Run all phases automatically with validation gates
Auto-stop if validation fails
```
**Pros:** Fast, consistent
**Cons:** Harder to debug if something fails

---

## ❓ **DECISION POINTS**

Before we start, please decide:

1. **Execution Approach:**
   - [ ] Sequential with reviews (recommended)
   - [ ] Automated pipeline

2. **Year for Production Data:**
   - [ ] Use 2025 for all monthly data
   - [ ] Use current year
   - [ ] Specify year: ________

3. **Validation Level:**
   - [ ] Basic (row counts, NULLs)
   - [ ] Standard (+ data types, ranges)
   - [ ] Comprehensive (+ business logic, statistics)

4. **Upload Method:**
   - [ ] Manual upload with guide
   - [ ] Automated upload script
   - [ ] Both (script + verification)

---

## 🚀 **READY TO START?**

**Saya siap create semua scripts untuk setiap phase!**

Apakah Anda ingin:
1. ✅ **Start dengan Phase 1** (Core tables)?
2. ✅ **Create semua phase scripts sekaligus** (lalu execute bertahap)?
3. ✅ **Customize plan** dulu?

Beri tahu saya pilihan Anda! 😊
