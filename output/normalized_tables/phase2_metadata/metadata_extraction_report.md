# PHASE 2: METADATA EXTRACTION REPORT

**Generated:** 2026-02-04 09:46:05

## Summary

### Source Data
- Source file: data_gabungan.xlsx (via normalized_production_data_COMPLETE.csv)
- Master blocks: 641 blocks

### Tables Created

#### 1. block_land_infrastructure.csv
- Rows: 645
- Columns: 12
- Contains: SPH, land area, infrastructure data
- Coverage: 645 / 641 blocks (100.6%)

#### 2. block_pest_disease.csv
- Rows: 645
- Columns: 7
- Contains: Ganoderma stadium data, serangan
- Coverage: Complete

#### 3. block_planting_history.csv
- Rows: 7095
- Years: 2009-2019 (11 years)
- Contains: Komposisi pokok per year
- Average per block: 11.1 years

#### 4. block_planting_yearly.csv
- Rows: 3870
- Years: 2020-2025 (6 years)
- Contains: Tanam, Sisip, Kentosan, TBM per year
- Average per block: 6.0 years

## Data Coverage

### Infrastructure Data
- SPH (Standar Pokok per Hektar): ✅
- Land area data: ✅
- Infrastructure (empls, bbt, pks): ✅

### Pest & Disease Data
- Ganoderma data: ✅

### Planting Data
- Historical (2009-2019): ✅
- Recent years (2020-2025): ✅
- Kentosan data: ❌

## Next Steps

1. ✅ Phase 2 complete - Metadata extracted
2. 📋 Phase 3 - Extract production data from Realisasi PT SR.xlsx (613 blocks)
3. 📋 Phase 4 - Integration and SQL schema generation

## Files Created

```
output/normalized_tables/phase2_metadata/
├── block_land_infrastructure.csv (645 rows)
├── block_pest_disease.csv (645 rows)
├── block_planting_history.csv (7095 rows)
├── block_planting_yearly.csv (3870 rows)
└── metadata_extraction_report.md (this file)
```

## Key Statistics

- Total metadata records: 12255
- Blocks covered: 641
- Years covered: 2009-2025 (up to 17 years)
- Ready for production data integration: 613 blocks

## Data Quality

- Infrastructure completeness: Excellent
- Pest/disease data: Available
- Historical planting: Complete
- Recent planting: Complete

**Status:** ✅ Phase 2 Complete
**Ready for:** Phase 3 - Production Data Extraction
