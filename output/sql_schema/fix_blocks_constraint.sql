-- FIX blocks table - Remove CHECK constraint to allow "Unknown" category
-- Run in Supabase SQL Editor

-- Drop and recreate WITHOUT check constraint
DROP TABLE IF EXISTS blocks CASCADE;

CREATE TABLE blocks (
    id BIGINT PRIMARY KEY,
    block_code VARCHAR(10) NOT NULL UNIQUE,
    has_production_data BOOLEAN DEFAULT FALSE,
    category VARCHAR(20),  -- No CHECK constraint - allows any value including "Unknown"
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_blocks_code ON blocks(block_code);
CREATE INDEX idx_blocks_category ON blocks(category);
CREATE INDEX idx_blocks_production ON blocks(has_production_data);

-- Verify
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'blocks'
ORDER BY ordinal_position;
