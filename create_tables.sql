-- ============================================================================
-- CREATE TABLES FOR NORMALIZED SCHEMA
-- Quick table creation script before upload
-- ============================================================================

-- Table 1: ESTATES (Estate master data)
CREATE TABLE IF NOT EXISTS estates (
    id SERIAL PRIMARY KEY,
    estate_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE estates IS 'Estate master data (Dimension table)';

-- Table 2: BLOCKS (Block master data)
CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) UNIQUE NOT NULL,
   estate_code VARCHAR(50),
    area_ha DECIMAL(10, 2),
    year_planted INTEGER,
    number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to estates
    CONSTRAINT fk_blocks_estate 
        FOREIGN KEY (estate_code) 
        REFERENCES estates(estate_code)
        ON DELETE SET NULL
);

COMMENT ON TABLE blocks IS 'Block master data with estate relationships';

-- Table 3: PRODUCTION_DATA (Production metrics - Fact table)
CREATE TABLE IF NOT EXISTS production_data (
    id INTEGER PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add all production columns (c001-c156, p001-p156, etc.)
    -- Note: Actual columns will be added by upload script based on CSV structure
    -- For now, we keep it flexible
    
    CONSTRAINT fk_production_block 
        FOREIGN KEY (block_code) 
        REFERENCES blocks(block_code)
        ON DELETE CASCADE
);

COMMENT ON TABLE production_data IS 'Production metrics fact table';

-- Table 4: REALISASI_POTENSI (Realisasi vs Potensi comparison - Fact table)
CREATE TABLE IF NOT EXISTS realisasi_potensi (
    id SERIAL PRIMARY KEY,
    block_code VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Add all realisasi columns
    -- Note: Actual columns will be added by upload script based on CSV structure
    
    CONSTRAINT fk_realisasi_block 
        FOREIGN KEY (block_code) 
        REFERENCES blocks(block_code)
        ON DELETE CASCADE
);

COMMENT ON TABLE realisasi_potensi IS 'Realisasi vs Potensi comparison fact table';

-- ============================================================================
-- VERIFICATION (Valid SQL only)
-- ============================================================================

-- List all created tables
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('estates', 'blocks', 'production_data', 'realisasi_potensi')
ORDER BY table_name;

-- Show table column details
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('estates', 'blocks', 'production_data', 'realisasi_potensi')
ORDER BY table_name, ordinal_position;
