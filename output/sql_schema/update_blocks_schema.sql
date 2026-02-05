-- UPDATE blocks table to match simplified CSV
-- Run in Supabase SQL Editor

-- Drop and recreate blocks table with correct minimal schema
DROP TABLE IF EXISTS blocks CASCADE;

CREATE TABLE blocks (
    id BIGINT PRIMARY KEY,
    block_code VARCHAR(10) NOT NULL UNIQUE,
    has_production_data BOOLEAN DEFAULT FALSE,
    category VARCHAR(20) CHECK (category IN ('Inti', 'Plasma')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blocks_code ON blocks(block_code);
CREATE INDEX idx_blocks_category ON blocks(category);
CREATE INDEX idx_blocks_production ON blocks(has_production_data);

-- Verify structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'blocks'
ORDER BY ordinal_position;

-- Expected: id, block_code, has_production_data, category, created_at
