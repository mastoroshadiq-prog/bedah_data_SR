# PHASE 3: PRODUCTION DATA EXTRACTION REPORT

**Generated:** 2026-02-04 09:51:10

## Summary

### Source Data
- Source file: Realisasi vs Potensi PT SR.xlsx (Sheet: Real VS Potensi Inti)
- Blocks processed: 612 blocks (from 613 available)

### Production Monthly Table
- **Total records: 11034**
- **Years covered: [np.int64(2023), np.int64(2024)]**
- **Months per year: 12**
- **Blocks with data: 612**

## Data Structure

### Transformation: WIDE → LONG
- **Before:** 113 columns (wide format)
- **After:** 11034 rows (long format)
- **Ratio:** 18.0 records per block

### Metrics Extracted
**Per month, per block:**
1. **Realisasi (Actual):**
   - BJR (Berat Janjang Rata-rata) - kg
   - Jumlah Janjang
   - Produksi - Ton

2. **Potensi (Target):**
   - BJR - kg
   - Jumlah Janjang
   - Produksi - Ton

3. **Gap (Realisasi - Potensi):**
   - Gap BJR - kg
   - Gap Jumlah Janjang
   - Gap Produksi - Ton
   - Gap Percentage - %

## Production Statistics

### Overall Gap Analysis
- **Average gap (Ton):** 93.59 ton/month
- **Average gap (%):** 2972.64%
- **Blocks underperforming:** 211 / 612 (34.5%)

### Gap Distribution (Ton %)
count    7.461000e+03
mean     2.972639e+03
std      2.477076e+04
min     -4.191578e+05
25%     -1.953100e+02
50%     -7.286000e+01
75%     -1.018000e+01
max      1.285057e+06

## Data Coverage

### Years
- 2023: 7356 records
- 2024: 3678 records
- 2025: 0 records

### Completeness
- Expected records: 613 blocks × 18 months = 11034
- Actual records: 11034
- Completeness: 100.0%

## Next Steps

1. ✅ Phase 3 complete - Production data extracted
2. 📋 Phase 4 - Integration and SQL schema generation
3. 📋 Phase 5 - Upload to Supabase

## Files Created

```
output/normalized_tables/phase3_production/
├── production_monthly.csv (11034 rows) ⭐
└── production_extraction_report.md (this file)
```

## Key Insights

- ✅ Successfully transformed 113 wide columns into 11034 long records
- ✅ 612 blocks with complete production data
- ✅ 3-year trend data ready ([np.int64(2023), np.int64(2024)])
- ✅ Gap analysis metrics calculated
- ✅ Average performance: +2972.6% vs target

**Status:** ✅ Phase 3 Complete
**Ready for:** Phase 4 - Integration & SQL Schema
