-- ============================================================================
-- NORMALIZED PALM OIL PRODUCTION DATABASE SCHEMA
-- Generated: 2026-02-04 10:31:11
-- Total Tables: 8
-- Total Records: 25,863
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: estates (Master Estate Data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS estates (
    id BIGINT PRIMARY KEY,
    estate_code VARCHAR(10) NOT NULL UNIQUE,
    estate_name VARCHAR(100),
    division VARCHAR(50),
    category VARCHAR(20) CHECK (category IN ('Inti', 'Plasma')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_estates_code ON estates(estate_code);
CREATE INDEX idx_estates_category ON estates(category);

COMMENT ON TABLE estates IS 'Master estate/kebun data with 13 estates';

-- ============================================================================
-- TABLE 2: blocks (Master Block Data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS blocks (
    id BIGINT PRIMARY KEY,
    block_code VARCHAR(10) NOT NULL UNIQUE,
    estate_id BIGINT REFERENCES estates(id),
    estate_code VARCHAR(10),
    estate_name VARCHAR(100),
    division VARCHAR(50),
    category VARCHAR(20) CHECK (category IN ('Inti', 'Plasma')),
    has_production_data BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blocks_code ON blocks(block_code);
CREATE INDEX idx_blocks_estate ON blocks(estate_id);
CREATE INDEX idx_blocks_category ON blocks(category);
CREATE INDEX idx_blocks_production ON blocks(has_production_data);

COMMENT ON TABLE blocks IS 'Master block data with 641 blocks total';

-- ============================================================================
-- TABLE 3: block_land_infrastructure (Land & Infrastructure Data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS block_land_infrastructure (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    
    -- Land area
    total_luas_sd_2025 NUMERIC(10, 2),
    luas_tanam_sd_2024 NUMERIC(10, 2),
    
    -- SPH (Standar Pokok per Hektar)
    sd_thn_2019_pkk NUMERIC(10, 2),
    sph NUMERIC(10, 2),
    
    -- Infrastructure
    empls VARCHAR(20),
    bbt VARCHAR(20),
    pks VARCHAR(20),
    
    -- Planting summary
    realisasi_tanam_sd_november_2025_komposisi_pokok NUMERIC(10, 2),
    total_pkk NUMERIC(10, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(block_id)
);

CREATE INDEX idx_infrastructure_block ON block_land_infrastructure(block_id);
CREATE INDEX idx_infrastructure_sph ON block_land_infrastructure(sph);

COMMENT ON TABLE block_land_infrastructure IS 'Land area, SPH, and infrastructure data per block';

-- ============================================================================
-- TABLE 4: block_pest_disease (Pest & Disease Data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS block_pest_disease (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    
    -- Ganoderma data by stadium
    serangan_ganoderma_pkk_stadium_1_2 NUMERIC(10, 2),
    stadium_3_4 NUMERIC(10, 2),
    total_serangan NUMERIC(10, 2),
    pct_serangan NUMERIC(5, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(block_id)
);

CREATE INDEX idx_pest_block ON block_pest_disease(block_id);
CREATE INDEX idx_pest_total ON block_pest_disease(total_serangan);
CREATE INDEX idx_pest_pct ON block_pest_disease(pct_serangan);

COMMENT ON TABLE block_pest_disease IS 'Ganoderma pest data by stadium levels';

-- ============================================================================
-- TABLE 5: block_planting_history (Historical Planting 2009-2019)
-- ============================================================================
CREATE TABLE IF NOT EXISTS block_planting_history (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL CHECK (year BETWEEN 2009 AND 2019),
    komposisi_pokok NUMERIC(10, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(block_id, year)
);

CREATE INDEX idx_planting_history_block ON block_planting_history(block_id);
CREATE INDEX idx_planting_history_year ON block_planting_history(year);
CREATE INDEX idx_planting_history_block_year ON block_planting_history(block_id, year);

COMMENT ON TABLE block_planting_history IS 'Historical planting data 2009-2019 (11 years)';

-- ============================================================================
-- TABLE 6: block_planting_yearly (Yearly Planting 2020-2025)
-- ============================================================================
CREATE TABLE IF NOT EXISTS block_planting_yearly (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL CHECK (year BETWEEN 2020 AND 2025),
    
    -- Planting data
    tanam NUMERIC(10, 2),
    sisip NUMERIC(10, 2),
    sisip_kentosan NUMERIC(10, 2),
    tbm NUMERIC(10, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(block_id, year)
);

CREATE INDEX idx_planting_yearly_block ON block_planting_yearly(block_id);
CREATE INDEX idx_planting_yearly_year ON block_planting_yearly(year);
CREATE INDEX idx_planting_yearly_block_year ON block_planting_yearly(block_id, year);

COMMENT ON TABLE block_planting_yearly IS 'Yearly planting data 2020-2025 with sisip, kentosan, TBM';

-- ============================================================================
-- TABLE 7: production_annual (Annual Production 2023-2025)
-- ============================================================================
CREATE TABLE IF NOT EXISTS production_annual (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL CHECK (year BETWEEN 2023 AND 2025),
    
    -- Realisasi (Actual)
    real_bjr_kg NUMERIC(10, 2),
    real_jum_jjg NUMERIC(10, 2),
    real_ton NUMERIC(10, 2),
    
    -- Potensi (Target)
    potensi_bjr_kg NUMERIC(10, 2),
    potensi_jum_jjg NUMERIC(10, 2),
    potensi_ton NUMERIC(10, 2),
    
    -- Gap (Actual - Target)
    gap_bjr_kg NUMERIC(10, 2),
    gap_jum_jjg NUMERIC(10, 2),
    gap_ton NUMERIC(10, 2),
    
    -- Gap Percentage
    gap_pct_bjr NUMERIC(10, 2),
    gap_pct_jjg NUMERIC(10, 2),
    gap_pct_ton NUMERIC(10, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(block_id, year)
);

CREATE INDEX idx_production_annual_block ON production_annual(block_id);
CREATE INDEX idx_production_annual_year ON production_annual(year);
CREATE INDEX idx_production_annual_block_year ON production_annual(block_id, year);
CREATE INDEX idx_production_annual_gap_ton ON production_annual(gap_ton);
CREATE INDEX idx_production_annual_gap_pct ON production_annual(gap_pct_ton);

COMMENT ON TABLE production_annual IS 'Annual production data 2023-2025 (year-over-year comparison)';

-- ============================================================================
-- TABLE 8: production_monthly (Monthly Production 2023-2024)
-- ============================================================================
CREATE TABLE IF NOT EXISTS production_monthly (
    id BIGINT PRIMARY KEY,
    block_id BIGINT NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
    block_code VARCHAR(10),
    year INTEGER NOT NULL,
    month VARCHAR(10) NOT NULL,
    
    -- Realisasi (Actual)
    real_bjr_kg NUMERIC(10, 2),
    real_jum_jjg NUMERIC(10, 2),
    real_ton NUMERIC(10, 2),
    
    -- Potensi (Target)
    potensi_bjr_kg NUMERIC(10, 2),
    potensi_jum_jjg NUMERIC(10, 2),
    potensi_ton NUMERIC(10, 2),
    
    -- Gap (Actual - Target)
    gap_bjr_kg NUMERIC(10, 2),
    gap_jum_jjg NUMERIC(10, 2),
    gap_ton NUMERIC(10, 2),
    
    -- Gap Percentage
    gap_pct_bjr NUMERIC(10, 2),
    gap_pct_jjg NUMERIC(10, 2),
    gap_pct_ton NUMERIC(10, 2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(block_id, year, month)
);

CREATE INDEX idx_production_monthly_block ON production_monthly(block_id);
CREATE INDEX idx_production_monthly_year ON production_monthly(year);
CREATE INDEX idx_production_monthly_month ON production_monthly(month);
CREATE INDEX idx_production_monthly_block_year_month ON production_monthly(block_id, year, month);
CREATE INDEX idx_production_monthly_gap_ton ON production_monthly(gap_ton);
CREATE INDEX idx_production_monthly_gap_pct ON production_monthly(gap_pct_ton);

COMMENT ON TABLE production_monthly IS 'Monthly production data 2023-2024 (monthly trend analysis)';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE estates ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE block_land_infrastructure ENABLE ROW LEVEL SECURITY;
ALTER TABLE block_pest_disease ENABLE ROW LEVEL SECURITY;
ALTER TABLE block_planting_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE block_planting_yearly ENABLE ROW LEVEL SECURITY;
ALTER TABLE production_annual ENABLE ROW LEVEL SECURITY;
ALTER TABLE production_monthly ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users (read-only for now)
CREATE POLICY "Allow read access for all authenticated users" ON estates
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON blocks
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON block_land_infrastructure
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON block_pest_disease
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON block_planting_history
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON block_planting_yearly
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON production_annual
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for all authenticated users" ON production_monthly
    FOR SELECT USING (auth.role() = 'authenticated');

-- ============================================================================
-- USEFUL VIEWS
-- ============================================================================

-- View: Complete block information with all references
CREATE OR REPLACE VIEW v_blocks_complete AS
SELECT 
    b.id,
    b.block_code,
    b.estate_code,
    b.estate_name,
    b.division,
    b.category,
    b.has_production_data,
    i.sph,
    i.total_luas_sd_2025 as total_area,
    p.total_serangan as ganoderma_total,
    p.pct_serangan as ganoderma_pct
FROM blocks b
LEFT JOIN block_land_infrastructure i ON b.id = i.block_id
LEFT JOIN block_pest_disease p ON b.id = p.block_id;

-- View: Latest annual production with gap analysis
CREATE OR REPLACE VIEW v_production_latest_annual AS
SELECT 
    b.block_code,
    b.estate_name,
    b.division,
    p.year,
    p.real_ton,
    p.potensi_ton,
    p.gap_ton,
    p.gap_pct_ton,
    CASE 
        WHEN p.gap_pct_ton < -20 THEN 'CRITICAL'
        WHEN p.gap_pct_ton < -10 THEN 'HIGH'
        WHEN p.gap_pct_ton < 0 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = (SELECT MAX(year) FROM production_annual);

-- ============================================================================
-- SUMMARY STATISTICS
-- ============================================================================

COMMENT ON DATABASE postgres IS 'Normalized Palm Oil Production Database - 25,863 total records';

