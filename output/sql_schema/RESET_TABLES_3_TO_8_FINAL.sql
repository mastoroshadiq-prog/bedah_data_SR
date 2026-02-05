-- ============================================================================
-- FINAL SOLUTION - DROP & RECREATE Tables 3-8
-- This will COMPLETELY reset tables 3-8, removing ALL data and constraints
-- Run this ENTIRE file in Supabase SQL Editor
-- ============================================================================

-- STEP 1: DROP all tables 3-8 completely (removes all data and schema)
DROP TABLE IF EXISTS production_monthly CASCADE;
DROP TABLE IF EXISTS production_annual CASCADE;
DROP TABLE IF EXISTS block_planting_yearly CASCADE;
DROP TABLE IF EXISTS block_planting_history CASCADE;
DROP TABLE IF EXISTS block_pest_disease CASCADE;
DROP TABLE IF EXISTS block_land_infrastructure CASCADE;

-- STEP 2: RECREATE all tables with fresh schema

-- TABLE 3: block_land_infrastructure
CREATE TABLE block_land_infrastructure (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    luas_tanam_sd_2024_ha NUMERIC(10, 2),
    total_luas_sd_2025_ha NUMERIC(10, 2),
    empls VARCHAR(20),
    bbt VARCHAR(20),
    pks VARCHAR(20),
    jalan_parit_ha NUMERIC(10, 2),
    areal_cadangan_ha NUMERIC(10, 2),
    total_luas_keseluruhan_ha NUMERIC(10, 2),
    standar_pokok_per_hektar NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id)
);
CREATE INDEX idx_infrastructure_block ON block_land_infrastructure(block_id);

-- TABLE 4: block_pest_disease
CREATE TABLE block_pest_disease (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    serangan_ganoderma_pkk_stadium_1_2 NUMERIC(10, 2),
    stadium_3_4 NUMERIC(10, 2),
    pct_serangan NUMERIC(5, 2),
    recorded_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id)
);
CREATE INDEX idx_pest_block ON block_pest_disease(block_id);

-- TABLE 5: block_planting_history
CREATE TABLE block_planting_history (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    komposisi_pokok NUMERIC(10, 2),
    year INTEGER NOT NULL CHECK (year BETWEEN 2009 AND 2019),
    sph NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id, year)
);
CREATE INDEX idx_planting_history_block ON block_planting_history(block_id);
CREATE INDEX idx_planting_history_year ON block_planting_history(year);

-- TABLE 6: block_planting_yearly
CREATE TABLE block_planting_yearly (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL CHECK (year BETWEEN 2020 AND 2025),
    tanam NUMERIC(10, 2),
    sph NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id, year)
);
CREATE INDEX idx_planting_yearly_block ON block_planting_yearly(block_id);
CREATE INDEX idx_planting_yearly_year ON block_planting_yearly(year);

-- TABLE 7: production_annual
CREATE TABLE production_annual (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL CHECK (year BETWEEN 2023 AND 2025),
    real_bjr_kg NUMERIC(10, 2),
    real_jum_jjg NUMERIC(10, 2),
    real_ton NUMERIC(10, 2),
    potensi_bjr_kg NUMERIC(10, 2),
    potensi_jum_jjg NUMERIC(10, 2),
    potensi_ton NUMERIC(10, 2),
    gap_bjr_kg NUMERIC(10, 2),
    gap_jum_jjg NUMERIC(10, 2),
    gap_ton NUMERIC(10, 2),
    gap_pct_bjr NUMERIC(10, 2),
    gap_pct_jjg NUMERIC(10, 2),
    gap_pct_ton NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id, year)
);
CREATE INDEX idx_production_annual_block ON production_annual(block_id);
CREATE INDEX idx_production_annual_year ON production_annual(year);
CREATE INDEX idx_production_annual_gap_ton ON production_annual(gap_ton);
CREATE INDEX idx_production_annual_gap_pct ON production_annual(gap_pct_ton);

-- TABLE 8: production_monthly
CREATE TABLE production_monthly (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL,
    month VARCHAR(10) NOT NULL,
    real_bjr_kg NUMERIC(10, 2),
    real_jum_jjg NUMERIC(10, 2),
    real_ton NUMERIC(10, 2),
    potensi_bjr_kg NUMERIC(10, 2),
    potensi_jum_jjg NUMERIC(10, 2),
    potensi_ton NUMERIC(10, 2),
    gap_bjr_kg NUMERIC(10, 2),
    gap_jum_jjg NUMERIC(10, 2),
    gap_ton NUMERIC(10, 2),
    gap_pct_bjr NUMERIC(10, 2),
    gap_pct_jjg NUMERIC(10, 2),
    gap_pct_ton NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id, year, month)
);
CREATE INDEX idx_production_monthly_block ON production_monthly(block_id);
CREATE INDEX idx_production_monthly_year ON production_monthly(year);
CREATE INDEX idx_production_monthly_month ON production_monthly(month);
CREATE INDEX idx_production_monthly_gap_ton ON production_monthly(gap_ton);
CREATE INDEX idx_production_monthly_gap_pct ON production_monthly(gap_pct_ton);

-- STEP 3: Verify tables are empty and ready
SELECT 
    'block_land_infrastructure' as table_name, COUNT(*) as count 
FROM block_land_infrastructure
UNION ALL SELECT 'block_pest_disease', COUNT(*) FROM block_pest_disease
UNION ALL SELECT 'block_planting_history', COUNT(*) FROM block_planting_history
UNION ALL SELECT 'block_planting_yearly', COUNT(*) FROM block_planting_yearly
UNION ALL SELECT 'production_annual', COUNT(*) FROM production_annual
UNION ALL SELECT 'production_monthly', COUNT(*) FROM production_monthly;

-- Expected: All should show 0

-- ============================================================================
-- DONE! Tables 3-8 completely reset and ready for upload
-- Now run: python phase5_upload_supabase.py
-- ============================================================================
