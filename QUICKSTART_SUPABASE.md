# ⚡ QUICK START: Upload ke Supabase

## 🚀 **3 LANGKAH MUDAH**

### **1. Install Package** (1x saja)
```bash
pip install supabase
```

### **2. Setup Credentials**
Edit `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
```

**Cara dapat credentials:**
- Buka Supabase Dashboard
- Project Settings > API
- Copy: Project URL & service_role key

### **3. Run 2 Commands**

**A. Create Schema (Supabase SQL Editor):**
1. Copy isi file: `output/sql_schema/create_tables_final.sql`
2. Paste ke SQL Editor
3. Click "Run"

**B. Upload Data (Terminal):**
```bash
python phase5_upload_supabase.py
```

**Done!** ✅ Database live dalam 10-15 menit!

---

## 📊 **Yang Akan Di-upload:**

```
✅ 8 tables
✅ 25,863 records
✅ Foreign keys
✅ Indexes
✅ Views
```

**Otomatis!** Tidak perlu buat table manual! 🎉

---

## ✅ **Verify Success:**

Supabase Dashboard > Table Editor:
- estates: 13 ✅
- blocks: 641 ✅
- block_land_infrastructure: 645 ✅
- block_pest_disease: 645 ✅
- block_planting_history: 7,095 ✅
- block_planting_yearly: 3,870 ✅
- production_annual: 1,920 ✅
- production_monthly: 11,034 ✅

**Total: 25,863 records** 🎯

---

## 🆘 **Troubleshooting:**

**Error: Credentials not found**
→ Check `.env` file ada dan isi benar

**Error: Table not found**
→ Run SQL schema dulu di SQL Editor

**Error: Connection failed**
→ Pakai service_role key (bukan anon key)

---

**Full guide:** `PHASE5_UPLOAD_GUIDE.md` 📖
