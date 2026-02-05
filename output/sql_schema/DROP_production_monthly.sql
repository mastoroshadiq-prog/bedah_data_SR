-- DROP production_monthly table (incorrect data)
-- This table contains WRONG data from misinterpretation of annual data as monthly
-- Run this in Supabase SQL Editor

DROP TABLE IF EXISTS production_monthly CASCADE;

-- Verify it's gone
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name = 'production_monthly';

-- Expected: No rows (table dropped)

-- Current valid tables should be:
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_schema = 'public' AND columns.table_name = tables.table_name) as column_count
FROM information_schema.tables 
WHERE table_schema = 'public'
  AND table_name IN ('estates', 'blocks', 'block_land_infrastructure', 
                     'block_pest_disease', 'block_planting_history', 
                     'block_planting_yearly', 'production_annual')
ORDER BY table_name;

-- Expected: 7 tables (production_monthly excluded)
