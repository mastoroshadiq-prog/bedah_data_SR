-- CLEAR ALL DATA - Run ini di Supabase SQL Editor
-- Untuk reset database sebelum upload ulang

-- Truncate all tables (CASCADE akan clear semua dependent tables)
TRUNCATE TABLE estates CASCADE;

-- Verify all tables empty
SELECT 'estates' as table_name, COUNT(*) as count FROM estates
UNION ALL SELECT 'blocks', COUNT(*) FROM blocks
UNION ALL SELECT 'block_land_infrastructure', COUNT(*) FROM block_land_infrastructure
UNION ALL SELECT 'block_pest_disease', COUNT(*) FROM block_pest_disease
UNION ALL SELECT 'block_planting_history', COUNT(*) FROM block_planting_history
UNION ALL SELECT 'block_planting_yearly', COUNT(*) FROM block_planting_yearly
UNION ALL SELECT 'production_annual', COUNT(*) FROM production_annual
UNION ALL SELECT 'production_monthly', COUNT(*) FROM production_monthly;

-- All should show 0
