# 🚀 PHASE 5: AUTOMATED SUPABASE UPLOAD GUIDE

**Complete automation - No manual table creation needed!**

---

## 📋 **PREREQUISITES**

### **1. Install Required Package**

```bash
pip install supabase
```

### **2. Create Supabase Project** (if not exists)

1. Go to [https://supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in project details
4. Wait for project to be ready (~2 minutes)

### **3. Get Your Credentials**

**SUPABASE_URL:**
- Go to: Project Settings > API
- Copy: Project URL
- Example: `https://abcdefghijklmnop.supabase.co`

**SUPABASE_SERVICE_KEY:**
- Go to: Project Settings > API
- Find: `service_role` key (click "Reveal" to see)
- ⚠️ **Important:** Use service_role (NOT anon key) for admin access
- Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

---

## ⚙️ **SETUP STEPS**

### **Step 1: Configure Environment Variables**

Create `.env` file in project root:

```bash
# Copy from template
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

### **Step 2: Create Database Schema**

**Option A: Via Supabase Dashboard (Recommended)**

1. Go to Supabase Dashboard
2. Click **SQL Editor** (left sidebar)
3. Click **"New Query"**
4. Open file: `output/sql_schema/create_tables_final.sql`
5. Copy ALL contents and paste into SQL Editor
6. Click **"Run"** or press `Ctrl+Enter`
7. Wait for success message (~5 seconds)

**Option B: Via SQL File Upload** (if available)

1. Go to SQL Editor
2. Click "Upload SQL"
3. Select `create_tables_final.sql`
4. Click "Run"

**What this creates:**
- ✅ 8 tables with constraints
- ✅ Foreign key relationships
- ✅ 20+ indexes
- ✅ Row Level Security policies
- ✅ 2 useful views

---

## 🚀 **RUN AUTOMATED UPLOAD**

### **Execute Upload Script**

```bash
python phase5_upload_supabase.py
```

### **What the script does:**

1. **Connects to Supabase** ✅
   - Validates credentials
   - Confirms connection

2. **Verifies Schema Created** ✅
   - Prompts you to confirm tables are ready
   - (Script will remind you if not done)

3. **Uploads All CSV Data** ✅
   - Processes 8 tables in correct order:
     1. estates (13 records)
     2. blocks (641 records)
     3. block_land_infrastructure (645 records)
     4. block_pest_disease (645 records)
     5. block_planting_history (7,095 records)
     6. block_planting_yearly (3,870 records)
     7. production_annual (1,920 records)
     8. production_monthly (11,034 records)
   
   - **Batch processing** (1,000 records per batch)
   - **Progress tracking** (real-time updates)
   - **Error handling** (option to continue or abort)

4. **Validates Data Integrity** ✅
   - Verifies record counts
   - Checks foreign key relationships
   - Tests database views

5. **Generates Report** ✅
   - Complete upload summary
   - Detailed statistics
   - Test queries
   - Next steps

---

## 📊 **EXPECTED OUTPUT**

```
================================================================================
PHASE 5: AUTOMATED SUPABASE UPLOAD
================================================================================
Started at: 2026-02-04 10:40:00

================================================================================
STEP 1: Connecting to Supabase
================================================================================
✅ Connected to Supabase
   URL: https://your-project.supabase.co

================================================================================
STEP 2: Creating database schema
================================================================================
✅ Loaded SQL schema from output/sql_schema/create_tables_final.sql

⚠️  IMPORTANT: SQL Schema Setup Required
================================================================================
Before running data upload, you need to create the schema:

1. Go to Supabase Dashboard > SQL Editor
2. Open file: output/sql_schema/create_tables_final.sql
3. Copy and paste the SQL into the editor
4. Click 'Run'

This only needs to be done ONCE to create all tables.
================================================================================

Have you run the SQL schema? (yes/no): yes

✅ Proceeding with data upload...

================================================================================
STEP 3: Uploading CSV data to Supabase
================================================================================

[1/8] Uploading estates...
    Description: Master estate data
    File: output/normalized_tables/phase1_core/estates.csv
    Records to upload: 13
    Uploading in 1 batch(es)...
      Batch 1/1: 13/13 records
    ✅ Successfully uploaded 13 records
    ✅ Verified: 13 records in database

[2/8] Uploading blocks...
    Description: Master block data
    File: output/normalized_tables/phase1_core/blocks_standardized.csv
    Records to upload: 641
    Uploading in 1 batch(es)...
      Batch 1/1: 641/641 records
    ✅ Successfully uploaded 641 records
    ✅ Verified: 641 records in database

... (continues for all 8 tables)

================================================================================
STEP 4: Verifying data integrity
================================================================================

Verifying foreign key relationships...
✅ blocks table: 641 unique IDs
✅ block_land_infrastructure.block_id → blocks.id: 641 refs, 0 orphaned
✅ block_pest_disease.block_id → blocks.id: 641 refs, 0 orphaned
✅ block_planting_history.block_id → blocks.id: 641 refs, 0 orphaned
✅ block_planting_yearly.block_id → blocks.id: 641 refs, 0 orphaned
✅ production_annual.block_id → blocks.id: 638 refs, 0 orphaned
✅ production_monthly.block_id → blocks.id: 612 refs, 0 orphaned

================================================================================
STEP 5: Testing database views
================================================================================

Testing v_blocks_complete...
✅ v_blocks_complete: 5 sample records retrieved

Testing v_production_latest_annual...
✅ v_production_latest_annual: 5 sample records retrieved

================================================================================
STEP 6: Generating upload report
================================================================================

✅ Generated upload report: output/sql_schema/supabase_upload_report.md

================================================================================
✅ PHASE 5 COMPLETE - DATABASE LIVE!
================================================================================
Completed at: 2026-02-04 10:45:35

📊 Upload Summary:
  Tables uploaded: 8/8
  Total records: 25,863
  Supabase URL: https://your-project.supabase.co

🎉 Your database is now LIVE and ready for use!

Files created:
  - supabase_upload_report.md - Detailed upload report

✅ PROJECT COMPLETE!
```

---

## 🔍 **VERIFY UPLOAD SUCCESS**

### **Via Supabase Dashboard:**

1. Go to **Table Editor**
2. Check each table appears in left sidebar
3. Click tables to view data
4. Verify row counts match expected

### **Via SQL Editor:**

```sql
-- Quick count check
SELECT 
    'estates' as table_name, COUNT(*) as count FROM estates
UNION ALL
SELECT 'blocks', COUNT(*) FROM blocks
UNION ALL
SELECT 'block_land_infrastructure', COUNT(*) FROM block_land_infrastructure
UNION ALL
SELECT 'block_pest_disease', COUNT(*) FROM block_pest_disease
UNION ALL
SELECT 'block_planting_history', COUNT(*) FROM block_planting_history
UNION ALL
SELECT 'block_planting_yearly', COUNT(*) FROM block_planting_yearly
UNION ALL
SELECT 'production_annual', COUNT(*) FROM production_annual
UNION ALL
SELECT 'production_monthly', COUNT(*) FROM production_monthly;

-- Expected results:
-- estates: 13
-- blocks: 641
-- block_land_infrastructure: 645
-- block_pest_disease: 645
-- block_planting_history: 7,095
-- block_planting_yearly: 3,870
-- production_annual: 1,920
-- production_monthly: 11,034
-- TOTAL: 25,863
```

---

## ⚠️ **TROUBLESHOOTING**

### **Error: "Supabase credentials not found"**

**Solution:**
- Check `.env` file exists
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are set
- Ensure no extra spaces or quotes

### **Error: "Table does not exist"**

**Solution:**
- SQL schema not created yet
- Run `create_tables_final.sql` in Supabase SQL Editor first
- Make sure to run the ENTIRE file

### **Error: "Connection refused" or "Invalid API key"**

**Solution:**
- Check `SUPABASE_SERVICE_KEY` is the **service_role** key (not anon)
- Verify `SUPABASE_URL` is correct
- Check internet connection

### **Error: "Foreign key constraint violation"**

**Solution:**
- Upload order matters!
- Script handles this automatically
- If manual upload: estates → blocks → rest

### **Upload Interrupted**

**Solution:**
- Script tracks which tables succeeded
- Delete uploaded tables: `TRUNCATE table_name CASCADE;`
- Re-run script

### **Partial Upload (Some tables uploaded, some failed)**

**Solution:**
- Check error messages
- Fix the issue
- Either:
  - Delete all data and re-run: `TRUNCATE estates CASCADE;`
  - Or skip successful tables in script

---

## 🎯 **NEXT STEPS AFTER UPLOAD**

### **1. Test Database Access**

```python
from supabase import create_client

# Use ANON key for regular access (not service_role)
supabase = create_client(
    'https://your-project.supabase.co',
    'your_anon_key_here'
)

# Test query
result = supabase.table('estates').select('*').execute()
print(f"Estates: {len(result.data)}")
```

### **2. Build Dashboard**

Your database is ready for:
- **Web dashboard** (React, Vue, Svelte, etc.)
- **Desktop app** (Electron, Tauri, etc.)
- **Mobile app** (React Native, Flutter, etc.)

### **3. Set Up Authentication (Optional)**

If you need user login:
1. Supabase Dashboard > Authentication
2. Enable providers (Email, Google, etc.)
3. Update RLS policies for user-specific access

### **4. Create Additional Views/Functions**

Add custom views or functions in SQL Editor for:
- Aggregated statistics
- Custom calculations
- Reporting queries

---

## 📝 **FILES GENERATED**

After successful upload:

```
output/sql_schema/
├── create_tables_final.sql - Schema (already used)
├── integration_report.md - Phase 4 report
└── supabase_upload_report.md - Phase 5 report ⭐ NEW
```

---

## ⏱️ **ESTIMATED TIME**

- **Setup (.env):** 2 minutes
- **Create schema (SQL Editor):** 1 minute
- **Run upload script:** 5-10 minutes (25,863 records)
- **Verify:** 2 minutes

**Total: 10-15 minutes** ⚡

---

## ✅ **SUCCESS CHECKLIST**

- [ ] `.env` file created with correct credentials
- [ ] SQL schema run successfully in Supabase
- [ ] Upload script completed without errors
- [ ] All 8 tables show in Table Editor
- [ ] Record counts match expected (25,863 total)
- [ ] Foreign key checks passed
- [ ] Views working (v_blocks_complete, v_production_latest_annual)
- [ ] Test query successful

---

## 🎉 **PROJECT COMPLETE!**

**From Excel to Production Database in ~2.5 hours:**

1. ✅ Phase 1.5: Block Standardization (641 blocks)
2. ✅ Phase 2: Metadata Extraction (12,255 records)
3. ✅ Phase 3: Production Extraction (12,954 records)
4. ✅ Phase 4: SQL Schema Generation
5. ✅ Phase 5: Automated Upload to Supabase

**Your normalized database is now LIVE and ready for dashboard integration!** 🚀

---

## 📚 **USEFUL RESOURCES**

- **Supabase Docs:** https://supabase.com/docs
- **Python Client:** https://supabase.com/docs/reference/python/introduction
- **SQL Guide:** https://supabase.com/docs/guides/database
- **Row Level Security:** https://supabase.com/docs/guides/auth/row-level-security

---

**Questions?** Check `supabase_upload_report.md` for detailed results and test queries!
