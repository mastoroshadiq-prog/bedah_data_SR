-- CLEAR DATA for tables 3-8 only
-- Keep estates and blocks (already uploaded successfully)
-- Run in Supabase SQL Editor

-- Clear all tables in reverse order (respects foreign keys)
TRUNCATE TABLE production_monthly CASCADE;
TRUNCATE TABLE production_annual CASCADE;
TRUNCATE TABLE block_planting_yearly CASCADE;
TRUNCATE TABLE block_planting_history CASCADE;
TRUNCATE TABLE block_pest_disease CASCADE;
TRUNCATE TABLE block_land_infrastructure CASCADE;

-- Verify all cleared
SELECT 
    'block_land_infrastructure' as table_name, COUNT(*) FROM block_land_infrastructure
UNION ALL SELECT 'block_pest_disease', COUNT(*) FROM block_pest_disease
UNION ALL SELECT 'block_planting_history', COUNT(*) FROM block_planting_history
UNION ALL SELECT 'block_planting_yearly', COUNT(*) FROM block_planting_yearly
UNION ALL SELECT 'production_annual', COUNT(*) FROM production_annual
UNION ALL SELECT 'production_monthly', COUNT(*) FROM production_monthly;

-- Expected: All should show 0

-- Check estates and blocks are still there
SELECT 'estates' as table_name, COUNT(*) FROM estates
UNION ALL SELECT 'blocks', COUNT(*) FROM blocks;

-- Expected: estates=3, blocks=641
