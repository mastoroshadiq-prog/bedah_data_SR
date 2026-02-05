-- FIX: Update has_production_data flag to match actual production data
-- This fixes coverage mismatch: 613 flagged vs 638 with data

-- Step 1: Find block_ids that have production data
WITH blocks_with_prod AS (
    SELECT DISTINCT block_id 
    FROM production_annual
)
-- Step 2: Update blocks table to set flag correctly
UPDATE blocks
SET has_production_data = CASE 
    WHEN id IN (SELECT block_id FROM blocks_with_prod) THEN TRUE
    ELSE FALSE
END;

-- Step 3: Verify fix
SELECT 
    'Blocks with flag' as category,
    COUNT(*) as count
FROM blocks 
WHERE has_production_data = TRUE

UNION ALL

SELECT 
    'Blocks in production_annual',
    COUNT(DISTINCT block_id)
FROM production_annual;

-- Expected: Both should show 638
