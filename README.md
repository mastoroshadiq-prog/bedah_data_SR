# 📊 Data Preprocessing & Normalization - Complete Guide

## 🎯 Executive Summary

**Status**: ✅ **COMPLETED**  
**Date**: 2026-02-03  
**Pipeline Version**: 1.0

---

## 📌 Apakah Ini Bagian dari Data Analysis Best Practices?

### ✅ **YA! Ini adalah bagian PENTING dari Data Analysis Pipeline**

Anda sedang berada di **TAHAP 2** dari pipeline Data Analysis yang komprehensif:

```
┌───────────────────────────────────────────────────────────────┐
│                  DATA ANALYSIS PIPELINE                        │
│                     (Best Practices)                           │
└───────────────────────────────────────────────────────────────┘

1️⃣  DATA COLLECTION
    └─ ✅ source/data_gabungan.xlsx (649 rows x 177 cols)

2️⃣  DATA PREPROCESSING & NORMALIZATION ⭐ ANDA DI SINI
    ├─ ✅ Data Cleaning
    ├─ ✅ Missing Value Handling
    ├─ ✅ Data Type Conversion
    ├─ ✅ Normalization
    ├─ ✅ Standardization
    └─ ✅ Quality Validation

3️⃣  DATA STORAGE
    └─ 🔜 Supabase Cloud Database (PostgreSQL)

4️⃣  DATA ANALYSIS
    └─ 🔜 Exploratory Data Analysis (EDA)
    └─ 🔜 Statistical Analysis
    └─ 🔜 Machine Learning (if needed)

5️⃣  VISUALIZATION & INSIGHTS
    └─ 🔜 Dashboards
    └─ 🔜 Reports
    └─ 🔜 Actionable Insights
```

---

## 📊 Preprocessing Results Summary

### Original Data
- **Shape**: 649 rows × 177 columns
- **Size**: ~1.26 MB
- **Missing Data**: 12,280 cells (10.69%)
- **Duplicates**: 0 rows

### After Preprocessing
- **Shape**: 643 rows × 180 columns *(6 rows removed, 5 metadata columns added)*
- **Size**: ~1.26 MB
- **Missing Data**: HANDLED (filled with appropriate strategies)
- **Duplicates**: 0 rows
- **Data Quality**: ✅ **PRODUCTION READY**

### Key Improvements

| Aspect | Before | After | Status |
|--------|--------|-------|--------|
| **Column Names** | Mixed, unclear | Standardized (snake_case) | ✅ |
| **Data Types** | All `object` | 164 numeric, 11 string | ✅ |
| **Missing Values** | 10.69% | Handled strategically | ✅ |
| **Empty Columns** | 2 columns | Removed | ✅ |
| **Database Ready** | ❌ | ✅ PostgreSQL compatible | ✅ |
| **Metadata** | None | 5 tracking columns added | ✅ |

---

## 🔄 Preprocessing Pipeline Details

### Phase 1: Data Loading & Analysis
```
✓ Loaded 649 rows × 177 columns
✓ Detected 10.69% missing data
✓ Identified 7 columns with >50% missing
✓ No duplicate rows found
```

### Phase 2: Data Cleaning
```
✓ Removed 2 empty columns
✓ Removed 6 empty rows
✓ Fixed column headers
✓ Final shape: 643 × 175 (before metadata)
```

### Phase 3: Data Type Conversion
```
✓ Converted 164 columns to numeric
✓ Kept 11 columns as string
✓ Auto-detected and converted types
```

### Phase 4: Missing Value Handling
**Strategy Distribution:**
- **Mean imputation**: 97 columns (for numeric with <30% missing)
- **Zero filling**: 18 columns (for numeric with >30% missing)
- **Median imputation**: 17 columns (for numeric with <5% missing)
- **Empty string**: 5 columns (for categorical with <30% missing)

### Phase 5: Standardization
```
✓ Column names → snake_case
✓ PostgreSQL compatible
✓ No reserved keywords
✓ Max length < 63 chars
```

### Phase 6: Metadata Enrichment
Added tracking columns:
- `id` - Unique identifier (1 to 643)
- `created_at` - Timestamp saat preprocessing
- `updated_at` - Timestamp terakhir diupdate
- `data_source` - Source file name
- `preprocessing_version` - Pipeline version (1.0)

---

## 📁 Output Files Generated

### 1. CSV File ⭐ **RECOMMENDED for Supabase**
```
📄 output/data_cleaned_20260203_104248.csv
📄 output/data_cleaned_latest.csv (always latest version)
```
- **Format**: UTF-8 with BOM
- **Size**: ~1.1 MB
- **Rows**: 643
- **Columns**: 180
- **Use**: Direct upload to Supabase

### 2. Excel File
```
📄 output/data_cleaned_20260203_104248.xlsx
```
- **Format**: XLSX (OpenPyXML)
- **Use**: Manual review & analysis

### 3. JSON File
```
📄 output/data_cleaned_20260203_104248.json
```
- **Format**: JSON array of records
- **Use**: API integration, web apps

### 4. Report File
```
📄 output/preprocessing_report.md
```
- **Comprehensive preprocessing report**
- **Contains all transformation details**

---

## 🚀 Upload to Supabase - Step by Step Guide

### Method 1: Supabase Dashboard (GUI) - EASIEST

#### Step 1: Login to Supabase
1. Go to https://app.supabase.com
2. Login to your project
3. Navigate to **Table Editor**

#### Step 2: Create New Table
1. Click **"New Table"**
2. Table name: `data_gabungan` (or any name you prefer)
3. **SKIP** column creation for now
4. Enable **Row Level Security (RLS)** if needed
5. Click **Save**

#### Step 3: Import CSV
1. Open the table you just created
2. Click **"Import data from CSV"**
3. Select file: `output/data_cleaned_latest.csv`
4. Supabase will auto-detect:
   - Column names
   - Data types
   - Primary key (use `id`)
5. Click **Import**
6. Wait for completion ⏳

#### Step 4: Verify
```sql
-- Run this query in SQL Editor
SELECT COUNT(*) FROM data_gabungan;
-- Should return: 643

SELECT * FROM data_gabungan LIMIT 10;
-- Check first 10 rows
```

---

### Method 2: Python Script (Programmatic)

Create file: `upload_to_supabase.py`

```python
from supabase import create_client, Client
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for bulk insert

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load cleaned data
df = pd.read_csv('output/data_cleaned_latest.csv')

# Convert to list of dictionaries
data_records = df.to_dict('records')

# Batch insert (Supabase max: 1000 rows per request)
batch_size = 500
total_rows = len(data_records)

print(f"Uploading {total_rows} rows to Supabase...")

for i in range(0, total_rows, batch_size):
    batch = data_records[i:i + batch_size]
    
    try:
        response = supabase.table('data_gabungan').insert(batch).execute()
        print(f"✓ Batch {i//batch_size + 1}: {len(batch)} rows uploaded")
    except Exception as e:
        print(f"✗ Error in batch {i//batch_size + 1}: {str(e)}")

print("✅ Upload complete!")
```

**Setup:**
```bash
# Install dependencies
pip install supabase python-dotenv pandas

# Create .env file with your credentials
echo "SUPABASE_URL=https://your-project.supabase.co" > .env
echo "SUPABASE_SERVICE_KEY=your-service-key" >> .env

# Run upload
python upload_to_supabase.py
```

---

### Method 3: SQL Direct Import

If you have PostgreSQL access:

```sql
-- Create table (auto-generated schema)
CREATE TABLE data_gabungan (
    id INTEGER PRIMARY KEY,
    k001 TEXT,
    k002 NUMERIC,
    -- ... (Supabase will auto-detect all columns)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    data_source TEXT,
    preprocessing_version NUMERIC
);

-- Import from CSV
COPY data_gabungan
FROM '/path/to/output/data_cleaned_latest.csv'
DELIMITER ','
CSV HEADER;

-- Verify
SELECT COUNT(*) FROM data_gabungan;
```

---

## 📈 Recommended Next Steps After Upload

### 1. Create Indexes for Performance
```sql
-- Index untuk kolom yang sering di-query
CREATE INDEX idx_data_k001 ON data_gabungan(k001);
CREATE INDEX idx_data_c001 ON data_gabungan(c001);
CREATE INDEX idx_data_created ON data_gabungan(created_at);

-- Composite index untuk filtering kompleks
CREATE INDEX idx_data_composite ON data_gabungan(c001, c002, created_at);
```

### 2. Setup Row Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE data_gabungan ENABLE ROW LEVEL SECURITY;

-- Policy: Allow authenticated users to read
CREATE POLICY "Allow read access to authenticated users"
ON data_gabungan
FOR SELECT
TO authenticated
USING (true);

-- Policy: Allow service role to do everything
CREATE POLICY "Allow full access to service role"
ON data_gabungan
FOR ALL
TO service_role
USING (true);
```

### 3. Create Views for Common Queries
```sql
-- View: Summary statistics
CREATE VIEW data_summary AS
SELECT 
    c001,
    c002,
    COUNT(*) as total_records,
    AVG(c003) as avg_c003,
    MAX(c004) as max_c004,
    MIN(c004) as min_c004
FROM data_gabungan
GROUP BY c001, c002;

-- View: Recent data
CREATE VIEW data_recent AS
SELECT *
FROM data_gabungan
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY created_at DESC;
```

### 4. Exploratory Data Analysis (EDA)

**Example queries:**

```sql
-- 1. Basic statistics
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT c001) as unique_c001,
    AVG(c003) as avg_c003
FROM data_gabungan;

-- 2. Distribution by category
SELECT 
    c001,
    COUNT(*) as count,
    ROUND(AVG(c003), 2) as avg_value
FROM data_gabungan
GROUP BY c001
ORDER BY count DESC;

-- 3. Time series analysis
SELECT 
    DATE(created_at) as date,
    COUNT(*) as daily_count,
    AVG(c003) as daily_avg
FROM data_gabungan
GROUP BY DATE(created_at)
ORDER BY date;

-- 4. Correlation analysis (if applicable)
SELECT 
    CORR(c003, c004) as correlation_c003_c004,
    CORR(c005, c006) as correlation_c005_c006
FROM data_gabungan;
```

---

## 🔍 Data Quality Assurance Checklist

| Check | Status | Details |
|-------|--------|---------|
| ✅ No null in primary key | PASS | `id` column has unique values 1-643 |
| ✅ Appropriate data types | PASS | 164 numeric, 11 string |
| ✅ No duplicates | PASS | 0 duplicate rows |
| ✅ Missing values handled | PASS | All missing values imputed |
| ✅ Column names standardized | PASS | snake_case, DB-friendly |
| ✅ No reserved keywords | PASS | No PostgreSQL conflicts |
| ✅ Metadata tracking | PASS | 5 tracking columns added |
| ✅ File encoding | PASS | UTF-8 with BOM |
| ✅ Size optimization | PASS | 1.26 MB (reasonable) |
| ✅ PostgreSQL compatible | PASS | Validated for Supabase |

---

## 🎓 Why This Approach is Best Practice

### 1. **Reproducibility**
- Pipeline is documented
- Version controlled preprocessing
- Metadata tracks transformations

### 2. **Data Quality**
- Systematic cleaning process
- Strategic missing value handling
- Type safety ensured

### 3. **Scalability**
- Modular pipeline design
- Batch processing ready
- Cloud-native format (CSV)

### 4. **Auditability**
- Comprehensive report generated
- Transformation log available
- Source tracking enabled

### 5. **Performance**
- Database-optimized schema
- Appropriate indexing strategies
- Efficient data types

### 6. **Security**
- RLS ready
- Service key isolation
- Metadata for access control

---

## 🛠️ Troubleshooting

### Issue 1: CSV Import Fails
**Solution:**
- Ensure UTF-8 encoding
- Check column separator (comma vs semicolon)
- Split large files if needed

### Issue 2: Data Type Mismatch
**Solution:**
- Review `preprocessing_report.md`
- Check Supabase auto-detection
- Manually specify types if needed

### Issue 3: Slow Upload
**Solution:**
- Use batch upload (500 rows/batch)
- Consider Supabase service key
- Upload during off-peak hours

---

## 📚 Additional Resources

### Supabase Documentation
- [Import CSV Data](https://supabase.com/docs/guides/database/import-data)
- [Table Editor](https://supabase.com/docs/guides/database/tables)
- [RLS Policies](https://supabase.com/docs/guides/auth/row-level-security)

### Data Analysis Best Practices
- [Data Preprocessing Guide](https://scikit-learn.org/stable/modules/preprocessing.html)
- [Pandas Data Cleaning](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## 📞 Support & Next Steps

### What You Have Now:
✅ Cleaned & normalized data  
✅ Multiple output formats  
✅ Comprehensive documentation  
✅ Supabase-ready CSV file  

### What's Next:
1. **Upload to Supabase** (choose method above)
2. **Create indexes** for performance
3. **Setup RLS** for security
4. **Start analysis** with SQL queries
5. **Build dashboard** (optional)

---

## 🎯 Summary

**Tahapan yang sudah diselesaikan:**
- ✅ Data Collection
- ✅ Data Preprocessing & Normalization

**Tahapan selanjutnya:**
- 🔜 Data Storage (Supabase upload)
- 🔜 Data Analysis
- 🔜 Visualization & Insights

**Data Anda kini:**
- ✅ Bersih & terstruktur
- ✅ Siap untuk analisis
- ✅ Mengikuti best practices
- ✅ Production-ready

---

Generated by: **Data Preprocessing Pipeline v1.0**  
Date: **2026-02-03**  
Status: **✅ READY FOR PRODUCTION**
