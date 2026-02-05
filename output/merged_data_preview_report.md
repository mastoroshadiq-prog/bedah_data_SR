
# PREVIEW MERGED DATA - SUMMARY REPORT

Generated: 2026-02-03 11:23:19

---

## 📊 MERGE STATISTICS

### Input Files:
- **Data Gabungan**: 643 rows × 181 columns
- **Realisasi vs Potensi**: 619 rows × 120 columns

### Merge Result:
- **Total rows**: 645 rows
- **Total columns**: 301 columns
- **Matched records**: 616 (95.5%)
- **Unmatched records**: 29 (4.5%)

### Join Details:
- **Join type**: LEFT JOIN
- **Join key**: gabungan.k001 = realisasi.blok
- **Match strategy**: Case-insensitive, trimmed

---

## 📋 DATA QUALITY

### Missing Values (Top 10 columns):

- **column_59**: 34 missing (5.3%)
- **p001**: 34 missing (5.3%)
- **p002**: 34 missing (5.3%)
- **53006**: 29 missing (4.5%)
- **560_89**: 29 missing (4.5%)
- **14_115146001877042**: 29 missing (4.5%)
- **46085**: 29 missing (4.5%)
- **650_4965034965035**: 29 missing (4.5%)
- **3_5335137338319154**: 29 missing (4.5%)
- **data_source_realisasi**: 29 missing (4.5%)

### Data Types:

- **float64**: 220 columns
- **object**: 56 columns
- **int64**: 25 columns

---

## 🎯 KEY FINDINGS

### Overlap Analysis:
- **Gabungan unique blocks**: 641
- **Realisasi unique blocks**: 618
- **Common blocks**: 612
- **Match rate**: 99.0%

### Matched Records:

**Estate Distribution:**

- DBE001: 77 records
- AME001: 76 records
- AME004: 70 records
- DBE002: 52 records
- OLE002: 44 records
- OLE003: 39 records
- DBE004: 39 records
- OLE004: 38 records
- AME003: 38 records
- AME002: 37 records
- OLE001: 34 records
- DBE006: 33 records
- DBE005: 25 records
- DBE003: 14 records

---

## 📁 EXPORTED FILES

1. **merged_full_data.csv**
   - Complete merged dataset
   - 645 rows × 301 columns
   - Ready for upload to Supabase

2. **merged_preview.xlsx**
   - Excel format for easy viewing
   - First 645 rows
   - All columns included

3. **merged_preview_100rows.csv**
   - Small sample for quick review
   - 100 rows × 11 key columns

4. **merged_matched_50rows.csv** (if matches found)
   - Matched records only
   - 50 rows × 301 columns

---

## 💡 RECOMMENDATIONS

### Based on the merge analysis:


✅ **HIGH MATCH RATE (95.5%)**

**Recommendation**: Proceed with merged data upload

**Action Items:**
1. Review merged_preview.xlsx to validate data quality
2. Check if all expected columns are present
3. Upload merged_full_data.csv to Supabase
4. Create indexes on k001 and blok columns


### File Size Considerations:

- **Current merged file**: ~3.3 MB in memory
- **Columns**: 301 (very wide table)

**If too wide**, consider:
- Uploading separately with foreign key relationship
- Creating views in Supabase for common join patterns
- Selecting only necessary columns from realisasi

---

## 📞 NEXT STEPS

Choose one of the following options:

### Option A: Upload Merged Data ✅
```bash
# Upload to Supabase
python upload_to_supabase.py
# (Modify script to use merged_full_data.csv)
```

### Option B: Upload Separately 📊
```bash
# Upload data_gabungan
python upload_to_supabase.py --file data_cleaned_latest.csv --table data_gabungan

# Upload realisasi
python upload_to_supabase.py --file realisasi_cleaned.csv --table realisasi_vs_potensi
```

### Option C: Review & Decide 🔍
1. Open `merged_preview.xlsx` in Excel
2. Review data quality and completeness
3. Decide based on your analysis needs

---

**Status**: ✅ Preview Ready - Awaiting Decision
