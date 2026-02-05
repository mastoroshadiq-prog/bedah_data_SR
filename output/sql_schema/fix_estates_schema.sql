-- QUICK FIX: Update estates table schema to match CSV
-- Run this in Supabase SQL Editor BEFORE uploading data

-- Drop columns that don't exist in CSV
ALTER TABLE estates DROP COLUMN IF EXISTS estate_name;
ALTER TABLE estates DROP COLUMN IF EXISTS division;
ALTER TABLE estates DROP COLUMN IF EXISTS category;
ALTER TABLE estates DROP COLUMN IF EXISTS updated_at;

-- Add column that exists in CSV  
ALTER TABLE estates ADD COLUMN IF NOT EXISTS division_code VARCHAR(10);

-- Verify structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'estates'
ORDER BY ordinal_position;
