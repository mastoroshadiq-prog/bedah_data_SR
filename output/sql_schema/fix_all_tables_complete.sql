-- COMPLETE SQL FIX - ALL TABLES AT ONCE
-- Run this entire file in Supabase SQL Editor
-- This will recreate ALL tables to match CSV files exactly

-- ============================================================================
-- TABLE 1: estates (Already uploaded - no changes needed)
-- ============================================================================
-- Current structure is correct: id, estate_code, estate_name, created_at

-- ============================================================================
-- TABLE 2: blocks (Already uploaded - no changes needed) 
-- ============================================================================
-- Current structure is correct: id, block_code, has_production_data, category, created_at

-- ============================================================================
-- TABLE 3: block_land_infrastructure
-- ============================================================================
DROP TABLE IF EXISTS block_land_infrastructure CASCADE;

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

-- ============================================================================
-- TABLE 4: block_pest_disease
-- ============================================================================
DROP TABLE IF EXISTS block_pest_disease CASCADE;

CREATE TABLE block_pest_disease (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    serangan_ganoderma_pkk_stadium_1_2 NUMERIC(10, 2),
    stadium_3_4 NUMERIC(10, 2),
    pct_serangan NUMERIC(5, 2),  -- CSV has "%serangan" - using pct_serangan  
    recorded_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(block_id)
);

CREATE INDEX idx_pest_block ON block_pest_disease(block_id);

-- ============================================================================
-- TABLE 5: block_planting_history
-- ============================================================================
DROP TABLE IF EXISTS block_planting_history CASCADE;

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

-- ============================================================================
-- TABLE 6: block_planting_yearly
-- ============================================================================
DROP TABLE IF EXISTS block_planting_yearly CASCADE;

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

-- ============================================================================
-- TABLE 7: production_annual
-- ============================================================================
DROP TABLE IF EXISTS production_annual CASCADE;

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

-- ============================================================================
-- TABLE 8: production_monthly
-- ============================================================================
DROP TABLE IF EXISTS production_monthly CASCADE;

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

-- ============================================================================
-- VERIFICATION - Check all table structures
-- ============================================================================
SELECT 
    table_name,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name IN (
        'estates',
        'blocks', 
        'block_land_infrastructure',
        'block_pest_disease',
        'block_planting_history',
        'block_planting_yearly',
        'production_annual',
        'production_monthly'
    )
GROUP BY table_name
ORDER BY table_name;

-- Expected column counts (including created_at):
-- estates: 4
-- blocks: 5
-- block_land_infrastructure: 14
-- block_pest_disease: 8
-- block_planting_history: 7
-- block_planting_yearly: 7
-- production_annual: 18
-- production_monthly: 19

-- ============================================================================
-- DONE! All tables recreated to match CSV files exactly
-- ============================================================================
-- Now you can run: python phase5_upload_supabase.py
-- All uploads from [3/8] to [8/8] should work!
