# ADDING DIVISION DATA TO SUPABASE
## Complete Implementation Guide

---

## 📊 DIVISION STRUCTURE EXTRACTED

**Total: 641 unique blocks mapped to divisions**

### AME Estate (231 blocks):
- **AME001** (AME I): 80 blocks
- **AME002** (AME II): 36 blocks  
- **AME003** (AME III): 39 blocks
- **AME004** (AME IV): 76 blocks

### OLE Estate (161 blocks):
- **OLE001** (OLE I): 35 blocks
- **OLE002** (OLE II): 45 blocks
- **OLE003** (OLE III): 38 blocks
- **OLE004** (OLE IV): 43 blocks

### DBE Estate (249 blocks):
- **DBE001** (DBE I): 79 blocks
- **DBE002** (DBE II): 32 blocks
- **DBE003** (DBE III): 50 blocks
- **DBE004** (DBE IV): 50 blocks
- **DBE005** (DBE V): 38 blocks

---

## 🔧 IMPLEMENTATION STEPS

### **STEP 1: Add Division Column via Supabase Dashboard**

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project
   
2. **Open SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"
   
3. **Run SQL Script**
   - Copy content from: `output/sql_schema/add_division_column.sql`
   - Paste into SQL Editor
   - Click "Run"
   
**SQL Script:**
```sql
-- Add division to blocks table
ALTER TABLE blocks 
ADD COLUMN IF NOT EXISTS division VARCHAR(10);

-- Add division to estates table
ALTER TABLE estates 
ADD COLUMN IF NOT EXISTS division VARCHAR(10);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_blocks_division ON blocks(division);
CREATE INDEX IF NOT EXISTS idx_estates_division ON estates(division);
```

---

### **STEP 2: Update Blocks with Division Data**

1. **Run Update Script**
   ```bash
   python update_division_supabase.py
   ```

2. **Script will:**
   - Load division mapping from `output/block_division_mapping.csv`
   - Match blocks by `block_code`
   - Update each block with its division
   - Process in batches of 100
   - Show progress every 50 blocks

3. **Expected Output:**
   ```
   Loaded 643 block->division mappings
   Found 641 blocks in database
   641 blocks have division mapping
   Updated 50/641 blocks...
   Updated 100/641 blocks...
   ...
   ✅ Update complete!
   Successfully updated: 641 blocks
   Errors: 0
   ```

---

### **STEP 3: Verify Update**

**Check via SQL:**
```sql
-- Count blocks per division
SELECT division, COUNT(*) as block_count
FROM blocks
WHERE division IS NOT NULL
GROUP BY division
ORDER BY division;

-- Sample blocks with division
SELECT block_code, estate_code, division
FROM blocks
WHERE division IS NOT NULL
LIMIT 20;
```

**Expected Result:**
```
division | block_count
---------|------------
AME001   | 80
AME002   | 36
AME003   | 39
AME004   | 76
OLE001   | 35
OLE002   | 45
OLE003   | 38
OLE004   | 43
DBE001   | 79
DBE002   | 32
DBE003   | 50
DBE004   | 50
DBE005   | 38
```

---

## 📁 FILES CREATED

1. **Division Mapping CSV:**
   - `output/block_division_mapping.csv` (643 rows)
   - Columns: block_code, estate, division, division_lama

2. **SQL Script:**
   - `output/sql_schema/add_division_column.sql`
   - Adds division column + indexes

3. **Python Update Script:**
   - `update_division_supabase.py`
   - Updates all blocks with division

4. **Verification Scripts:**
   - `check_division_clean.py` - Verify division counts
   - `verify_division_count.py` - Detailed check

---

## ⚠️ IMPORTANT NOTES

### **Division Code Format:**
- **Format:** `{ESTATE}{DIVISION_NUMBER}`
- **Examples:**
  - AME001 = AME Division I
  - AME002 = AME Division II
  - OLE001 = OLE Division I
  - DBE001 = DBE Division I

### **Data Source:**
- Extracted from: `source/data_gabungan.xlsx`
- Columns used: DIVISI BARU (C004)
- Cross-checked with: DIVISI LAMA (C003)

### **Missing Divisions:**
- 2 blocks have no division (empty/null in source)
- These will have NULL division in database

---

## 🚀 NEXT STEPS (For Dashboard)

After Supabase update complete:

1. **✅ Estate Level** (Current) - AME, OLE, DBE
2. **🔄 Division Level** (Next) - AME001-004, OLE001-004, DBE001-005
3. **📊 Block Level** (Final) - Individual blocks

**Dashboard Structure:**
```
All Estates
├── AME
│   ├── AME I (AME001) - 80 blocks
│   ├── AME II (AME002) - 36 blocks
│   ├── AME III (AME003) - 39 blocks
│   └── AME IV (AME004) - 76 blocks
├── OLE
│   ├── OLE I (OLE001) - 35 blocks
│   ├── OLE II (OLE002) - 45 blocks
│   ├── OLE III (OLE003) - 38 blocks
│   └── OLE IV (OLE004) - 43 blocks
└── DBE
    ├── DBE I (DBE001) - 79 blocks
    ├── DBE II (DBE002) - 32 blocks
    ├── DBE III (DBE003) - 50 blocks
    ├── DBE IV (DBE004) - 50 blocks
    └── DBE V (DBE005) - 38 blocks
```

---

## ✅ CHECKLIST

- [ ] Run SQL script in Supabase Dashboard
- [ ] Verify division column exists in blocks table
- [ ] Run `python update_division_supabase.py`
- [ ] Verify 641 blocks updated successfully
- [ ] Check division counts via SQL
- [ ] Ready for dashboard division breakdown

---

**Created:** 2026-02-04  
**Status:** Ready for Execution  
**Next:** Run Step 1 in Supabase Dashboard
