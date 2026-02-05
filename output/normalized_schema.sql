
-- ============================================================================
-- NORMALIZED DATABASE SCHEMA FOR SUPABASE
-- Generated: 2026-02-03 11:29:11
-- ============================================================================

-- Table 1: ESTATES (Dimension)
CREATE TABLE IF NOT EXISTS estates (
    id SERIAL PRIMARY KEY,
    estate_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_estates_code ON estates(estate_code);

-- Table 2: BLOCKS (Master Data)
CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) UNIQUE NOT NULL,
    estate_code VARCHAR(50) REFERENCES estates(estate_code),
    area_ha DECIMAL(10, 2),
    year_planted INTEGER,
    number INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blocks_code ON blocks(block_code);
CREATE INDEX idx_blocks_estate ON blocks(estate_code);
CREATE INDEX idx_blocks_year ON blocks(year_planted);

-- Table 3: PRODUCTION_DATA (Fact Table from Gabungan)
CREATE TABLE IF NOT EXISTS production_data (
    id INTEGER PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL REFERENCES blocks(block_code),
    -- Add all production metrics columns here (c001-c056, p001-p115, etc.)
    -- Example columns:
    -- c001 DECIMAL(15, 6),
    -- c002 DECIMAL(15, 6),
    -- ... (add all your specific columns)
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    data_source VARCHAR(255)
);

CREATE INDEX idx_production_block ON production_data(block_code);

-- Table 4: REALISASI_POTENSI (Fact Table - Time Series)
CREATE TABLE IF NOT EXISTS realisasi_potensi (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL REFERENCES blocks(block_code),
    -- Add year-specific columns here
    -- Example structure for each year (2014-2025):
    -- year_2014_real DECIMAL(15, 2),
    -- year_2014_potensi DECIMAL(15, 2),
    -- year_2014_variance DECIMAL(15, 2),
    -- ... repeat for each year
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_realisasi_block ON realisasi_potensi(block_code);

-- Create view for easy joining
CREATE OR REPLACE VIEW v_complete_data AS
SELECT 
    b.block_code,
    b.estate_code,
    e.estate_code as estate_name,
    b.area_ha,
    b.year_planted,
    pd.*,
    rp.*
FROM blocks b
LEFT JOIN estates e ON b.estate_code = e.estate_code
LEFT JOIN production_data pd ON b.block_code = pd.block_code
LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code;

-- Row Level Security (RLS) - Optional
ALTER TABLE estates ENABLE ROW LEVEL SECURITY;
ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE production_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE realisasi_potensi ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (adjust per your needs)
CREATE POLICY "Enable read access for all users" ON estates FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON blocks FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON production_data FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON realisasi_potensi FOR SELECT USING (true);
