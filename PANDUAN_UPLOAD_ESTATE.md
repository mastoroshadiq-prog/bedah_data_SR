# PANDUAN: Upload Excel per Estate untuk Fix Database

## 📋 TUJUAN
Memperbaiki database production_annual dengan data yang benar dari Excel Boss (per estate)

---

## 📁 STRUKTUR FILE YANG DIBUTUHKAN

Boss akan upload **3 file Excel** (atau CSV), satu untuk setiap estate:

### TAHAP 1: Estate AME
**Nama file:** `AME_production.xlsx` (atau `AME_production.csv`)  
**Lokasi:** `source/estate_fix/`  
**Isi:** Data produksi 2023-2025 untuk estate AME

### TAHAP 2: Estate OLE
**Nama file:** `OLE_production.xlsx` (atau `OLE_production.csv`)  
**Lokasi:** `source/estate_fix/`  
**Isi:** Data produksi 2023-2025 untuk estate OLE

### TAHAP 3: Estate DBE
**Nama file:** `DBE_production.xlsx` (atau `DBE_production.csv`)  
**Lokasi:** `source/estate_fix/`  
**Isi:** Data produksi 2023-2025 untuk estate DBE

---

## 📊 FORMAT KOLOM YANG DIBUTUHKAN

Setiap file Excel harus punya kolom berikut (nama bisa fleksibel):

| Kolom | Alternatif Nama | Contoh Isi |
|-------|----------------|------------|
| **block_code** | block, kode_blok | A001A, A002A, O001A |
| **year** | tahun, year | 2023, 2024, 2025 |
| **real_ton** | realisasi, aktual, actual | 245.5, 320.8 |
| **potensi_ton** | potensi, target, potential | 280.0, 350.0 |

### Contoh Data:

```
block_code | year | real_ton | potensi_ton
-----------|------|----------|------------
A001A      | 2023 | 245.50   | 280.00
A001A      | 2024 | 232.10   | 280.00
A001A      | 2025 | 256.80   | 280.00
A002A      | 2023 | 320.80   | 350.00
...
```

---

## ✅ CHECKLIST UNTUK BOSS

### Sebelum Upload:
- [ ] File berformat `.xlsx` atau `.csv`
- [ ] Ada kolom: block_code, year, real_ton, potensi_ton
- [ ] Data lengkap untuk tahun 2023, 2024, 2025
- [ ] Tidak ada baris kosong atau header ganda
- [ ] Angka produksi sudah benar (sesuai source asli)

### Path Upload:
```
F:\PythonProjects\normalisasi_data\source\estate_fix\
```

Contoh:
- `source/estate_fix/AME_production.xlsx`
- `source/estate_fix/OLE_production.xlsx`  
- `source/estate_fix/DBE_production.xlsx`

---

## 🚀 WORKFLOW

### 1. Boss Upload File (Bertahap)
```
TAHAP 1: Upload AME_production.xlsx
         → Run: python process_estate_fix.py
         → Check SQL generated

TAHAP 2: Upload OLE_production.xlsx  
         → Run: python process_estate_fix.py
         → Check SQL generated

TAHAP 3: Upload DBE_production.xlsx
         → Run: python process_estate_fix.py
         → Check SQL generated
```

### 2. Script Auto-Generate SQL
Script akan:
- Baca Excel file
- Compare dengan database
- Generate UPDATE/INSERT statements
- Save ke `fix_production_complete.sql`

### 3. Execute SQL di Supabase
```sql
-- 1. Backup dulu (PENTING!)
CREATE TABLE production_annual_backup AS 
SELECT * FROM production_annual;

-- 2. Run fix script
-- (copy-paste dari fix_production_complete.sql)

-- 3. Verify
SELECT year, 
       COUNT(*) as records,
       SUM(real_ton) as actual,
       SUM(potensi_ton) as target
FROM production_annual
GROUP BY year
ORDER BY year;
```

### 4. Verify Hasil
Harus match dengan Boss's totals:
- 2023: 141,630.61 Ton (actual) | 187,781.70 Ton (target)
- 2024: 136,553.30 Ton (actual) | 190,482.30 Ton (target)
- 2025: 143,382.80 Ton (actual) | 191,449.80 Ton (target)

---

## 📝 CONTOH PENAMAAN FILE

✅ **BENAR:**
- `AME_production.xlsx`
- `OLE_production.csv`
- `DBE_production.xlsx`

❌ **SALAH:**
- `AME.xlsx` (kurang specific)
- `production_ame.xlsx` (format beda)
- `Estate AME Production.xlsx` (ada spasi)

---

## ⚠️ TROUBLESHOOTING

### Error: "Column not found"
→ Pastikan file punya kolom: block_code, year, real_ton, potensi_ton

### Error: "Block code not found"
→ Block code di Excel harus sama dengan di database blocks table

### SQL statement count = 0
→ Check format file, pastikan tidak ada cell kosong

### Totals tidak match
→ Check apakah semua blocks sudah di-include di Excel

---

## 📞 JIKA BUTUH BANTUAN

Kalau Boss bingung atau ada error:
1. Screenshot error message
2. Kirim sample 5 baris data Excel
3. Saya akan bantu debug

---

**READY BOSS! Silakan upload file TAHAP 1 (AME) dulu!** 🚀

Folder sudah ready di: `source/estate_fix/`
