# ❓ CLARIFICATION: Production Year Data

## 🤔 **PERTANYAAN PENTING**

User bertanya: **"Mengapa hanya tahun 2025 saja? Padahal kita perlu menampilkan tren produksi / gap yield 3 tahun sebelumnya dari 2023"**

## 📊 **SITUASI SAAT INI**

### **Data yang Ada:**
```
File: normalized_production_data_COMPLETE.csv (156 columns)

Production data columns (~100 columns):
- real_bjr_kg, real_jum_jjg, real_ton (Realisasi)
- potensi_bjr_kg, potensi_jum_jjg, potensi_ton (Potensi)
- real_vs_potensi_bjr_kg, ... (Gap)

Pattern: Appears to be MONTHLY data (12 bulan)
```

### **MASALAH:**
Data produksi **tidak include year dimension explicitly**!
- ❓ Apakah ini data untuk 1 tahun saja? (e.g., 2025)
- ❓ Atau data 12 bulan tapi tahun tidak specified?
- ❓ Atau sebenarnya ada data multi-tahun yang perlu di-extract?

## 🎯 **SOLUSI YANG PERLU**

Untuk **trend analysis 3 tahun**, kita butuh:

### **Option A: Data Memang 1 Tahun Saja (Current Snapshot)**
```
Jika source data hanya untuk 1 tahun:
- Normalize ke: production_monthly (block_id, year=2025, month, metrics)
- Untuk historical trend: Perlu source data tahun sebelumnya
- Limitation: Tidak bisa show trend 3 tahun

Recommendation: Upload dulu 2025, nanti tambah 2024, 2023 dari source lain
```

### **Option B: Data Ada Multi-Tahun (Need to Extract)**
```
Jika source file sebenarnya punya data multi-tahun:
- Identify year columns/patterns
- Extract production data per tahun
- Normalize ke: production_monthly dengan year = 2023, 2024, 2025

Structure:
| block_id | year | month | real_ton | potensi_ton | gap_ton |
|----------|------|-------|----------|-------------|---------|
| 1        | 2023 | Jan   | 100      | 120         | -20     |
| 1        | 2023 | Feb   | 105      | 120         | -15     |
| ...
| 1        | 2024 | Jan   | 110      | 125         | -15     |
| 1        | 2025 | Jan   | 115      | 130         | -15     |
```

### **Option C: Need Different Source Files**
```
Jika normalized_production_data_COMPLETE.csv hanya 2025:
- Cari file untuk 2024: normalized_production_data_2024.csv?
- Cari file untuk 2023: normalized_production_data_2023.csv?
- Merge semua tahun → production_monthly table

OR: Import dari Excel asli untuk tahun 2023, 2024
```

## ❓ **PERTANYAAN UNTUK USER**

**Please clarify:**

1. **Apakah file `normalized_production_data_COMPLETE.csv` berisi:**
   - [ ] Data 1 tahun saja (tahun berapa?)
   - [ ] Data multi-tahun (2023, 2024, 2025) tapi perlu di-extract
   - [ ] Tidak tahu - perlu investigation

2. **Untuk trend 3 tahun, data tahun mana yang Anda butuhkan?**
   - [ ] 2023, 2024, 2025 (current year)
   - [ ] 2022, 2023, 2024
   - [ ] 2021, 2022, 2023
   - [ ] Other: ____________

3. **Source data untuk historical years:**
   - [ ] Sudah ada dalam file yang sama (normalized_production_data_COMPLETE.csv)
   - [ ] Ada di file Excel asli (perlu extract lagi)
   - [ ] Belum ada - akan diinput manual nanti
   - [ ] Other: ____________

## 🔍 **ACTION YANG PERLU DILAKUKAN**

### **Immediate:**
1. ✅ Investigate structure of normalized_production_data_COMPLETE.csv
2. ✅ Check if year dimension exists implicitly
3. ✅ Check original Excel source untuk multi-year data

### **After Clarification:**

**If Single Year Data:**
```python
# Normalize with explicit year
production_monthly.csv:
- block_id, year (2025), month, metrics...
- Can add 2024, 2023 later from other sources
```

**If Multi-Year Data:**
```python
# Extract all years
production_monthly.csv:
- block_id, year (2023/2024/2025), month, metrics...
- Full 3-year trend ready!
```

## 💡 **MY RECOMMENDATION**

**Best Approach for Multi-Year Trend:**

1. **Check Original Excel** untuk tahun 2023, 2024, 2025
2. **Process each year separately** → 3 files
3. **Merge into single production_monthly** table
4. **Structure:**
```sql
CREATE TABLE production_monthly (
    id SERIAL PRIMARY KEY,
    block_id INTEGER REFERENCES blocks(id),
    year INTEGER NOT NULL,  -- 2023, 2024, 2025
    month VARCHAR(10) NOT NULL,  -- Jan, Feb, ..., Dec
    real_bjr_kg DECIMAL(10,2),
    real_jum_jjg INTEGER,
    real_ton DECIMAL(10,2),
    potensi_bjr_kg DECIMAL(10,2),
    potensi_jum_jjg INTEGER,
    potensi_ton DECIMAL(10,2),
    gap_bjr_kg DECIMAL(10,2),
    gap_jum_jjg INTEGER,
    gap_ton DECIMAL(10,2),
    gap_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id, year, month)
);

-- Index for trend queries
CREATE INDEX idx_production_year_month ON production_monthly(year, month);
CREATE INDEX idx_production_block_year ON production_monthly(block_id, year);
```

---

## 🚀 **NEXT STEPS**

**Please provide:**
1. Confirmation: Tahun mana saja yang dibutuhkan? (2023, 2024, 2025?)
2. Data source: Apakah perlu extract dari Excel asli untuk each year?
3. Priority: Mulai dengan 1 tahun dulu, atau tunggu sampai 3 tahun ready?

**Then we can adjust the implementation plan accordingly!**
