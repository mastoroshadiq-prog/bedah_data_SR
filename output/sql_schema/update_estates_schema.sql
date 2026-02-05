-- UPDATE estates table schema to match corrected CSV
-- Run this in Supabase SQL Editor

-- Drop and recreate with correct columns
DROP TABLE IF EXISTS estates CASCADE;

CREATE TABLE estates (
    id BIGINT PRIMARY KEY,
    estate_code VARCHAR(10) NOT NULL UNIQUE,
    estate_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_estates_code ON estates(estate_code);

-- Verify structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'estates'
ORDER BY ordinal_position;

-- Expected columns:
-- id, estate_code, estate_name, created_at
