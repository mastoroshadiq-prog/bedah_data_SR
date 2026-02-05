-- ============================================================================
-- SIMPLE TABLE CREATION (Without all columns)
-- Tables will accept dynamic columns from CSV upload
-- ============================================================================

-- Table 1: ESTATES
CREATE TABLE IF NOT EXISTS estates (
    id SERIAL PRIMARY KEY,
    estate_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: BLOCKS  
CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) UNIQUE NOT NULL,
    estate_code VARCHAR(50),
    area_ha DECIMAL(10, 2),
    year_planted INTEGER,
    number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: PRODUCTION_DATA (basic structure)
CREATE TABLE IF NOT EXISTS production_data (
    id INTEGER PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: REALISASI_POTENSI (basic structure)
CREATE TABLE IF NOT EXISTS realisasi_potensi (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Verify tables created
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('estates', 'blocks', 'production_data', 'realisasi_potensi')
ORDER BY table_name;
