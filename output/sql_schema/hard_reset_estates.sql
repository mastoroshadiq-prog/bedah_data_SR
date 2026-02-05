-- HARD RESET - Complete table recreation
-- Run this in Supabase SQL Editor if TRUNCATE doesn't work

-- Step 1: Drop the estates table completely (CASCADE drops all dependent data)
DROP TABLE IF EXISTS estates CASCADE;

-- Step 2: Recreate estates table with correct schema
CREATE TABLE estates (
    id BIGINT PRIMARY KEY,
    estate_code VARCHAR(10) NOT NULL UNIQUE,
    division_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Step 3: Create index
CREATE INDEX idx_estates_code ON estates(estate_code);

-- Step 4: Enable RLS (optional, you disabled it but can enable later)
-- ALTER TABLE estates ENABLE ROW LEVEL SECURITY;

-- Step 5: Verify table is empty and structure is correct
SELECT * FROM estates;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'estates'
ORDER BY ordinal_position;

-- Expected columns:
-- id (bigint)
-- estate_code (character varying)
-- division_code (character varying)
-- created_at (timestamp)
