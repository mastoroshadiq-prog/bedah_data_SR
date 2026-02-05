# 🚀 QUICK START GUIDE

## ✅ Apa yang Sudah Selesai?

### 1. Data Preprocessing ✓
```
Original: 649 rows × 177 columns → Cleaned: 643 rows × 180 columns
Missing: 10.69% → Handled: 100% ✓
Types: All object → 164 numeric + 11 string ✓
```

### 2. Files Generated ✓
```
✓ CSV  : output/data_cleaned_latest.csv (untuk Supabase)
✓ Excel: output/data_cleaned_20260203_104248.xlsx
✓ JSON : output/data_cleaned_20260203_104248.json
✓ Report: output/preprocessing_report.md
```

---

## 🔥 Langkah Selanjutnya (5 menit)

### Option A: Upload via Supabase Dashboard (PALING MUDAH)

1. **Login ke Supabase**
   - Buka: https://app.supabase.com
   - Login ke project Anda

2. **Create Table**
   - Klik **Table Editor** → **New Table**
   - Nama: `data_gabungan`
   - Klik **Save**

3. **Import CSV**
   - Buka table yang baru dibuat
   - Klik **Import data from CSV**
   - Upload: `output/data_cleaned_latest.csv`
   - Klik **Import**
   - DONE! ✅

### Option B: Upload via Python Script

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Credentials**
   ```bash
   # Copy template
   copy .env.example .env
   
   # Edit .env dan isi dengan credentials Supabase Anda
   notepad .env
   ```

3. **Run Upload Script**
   ```bash
   python upload_to_supabase.py
   ```

4. **Verify**
   - Script akan otomatis verify data
   - Check di Supabase Table Editor

---

## 📊 Mulai Analisa Data

### Via Supabase SQL Editor

```sql
-- 1. Cek total data
SELECT COUNT(*) FROM data_gabungan;

-- 2. Lihat sample data
SELECT * FROM data_gabungan LIMIT 10;

-- 3. Statistik per kategori
SELECT 
    c001,
    COUNT(*) as total,
    AVG(c003) as rata_rata,
    MAX(c004) as maksimal
FROM data_gabungan
GROUP BY c001;
```

### Via Python

```bash
# Jalankan script analisa
python analyze_data.py
```

---

## 📂 Struktur Project

```
normalisasi_data/
│
├── 📄 README.md                    # Dokumentasi lengkap
├── 📄 QUICKSTART.md               # File ini
├── 📄 requirements.txt            # Dependencies
├── 📄 .env.example                # Template credentials
│
├── 🐍 data_preprocessing.py       # Main preprocessing script
├── 🐍 upload_to_supabase.py       # Upload script
├── 🐍 analyze_data.py             # Analysis examples
│
├── 📁 source/
│   └── data_gabungan.xlsx         # Original data
│
└── 📁 output/
    ├── data_cleaned_latest.csv    # ⭐ Main output
    ├── data_cleaned_*.xlsx
    ├── data_cleaned_*.json
    └── preprocessing_report.md    # Detail report
```

---

## 💡 Tips

1. **Gunakan CSV untuk upload** - paling compatible dengan Supabase
2. **Baca preprocessing_report.md** - untuk detail transformasi
3. **Create indexes setelah upload** - untuk performa query
4. **Setup RLS jika perlu** - untuk security

---

## 🆘 Troubleshooting

**Q: Upload gagal?**
- Pastikan .env sudah diisi dengan benar
- Check Supabase quota (free tier max 500MB)
- Coba upload via dashboard jika script gagal

**Q: Data tidak sesuai?**
- Lihat preprocessing_report.md untuk detail transformasi
- Original data masih ada di source/data_gabungan.xlsx
- Bisa re-run preprocessing jika perlu

**Q: Perlu custom preprocessing?**
- Edit data_preprocessing.py
- Sesuaikan tahapan preprocessing
- Re-run script

---

## ✅ Checklist

- [ ] Data preprocessing selesai ✓ (sudah otomatis)
- [ ] Upload data ke Supabase
- [ ] Create indexes di Supabase
- [ ] Setup RLS (jika perlu)
- [ ] Mulai analisa data

---

**Next Step**: Upload ke Supabase (pilih Option A atau B di atas) 🚀
