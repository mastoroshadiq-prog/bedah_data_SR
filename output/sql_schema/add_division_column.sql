-- ============================================================================
-- ADD DIVISION COLUMN TO TABLES
-- ============================================================================

-- Add division to blocks table
ALTER TABLE blocks 
ADD COLUMN IF NOT EXISTS division VARCHAR(10);

-- Add division to estates table
ALTER TABLE estates 
ADD COLUMN IF NOT EXISTS division VARCHAR(10);

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_blocks_division ON blocks(division);
CREATE INDEX IF NOT EXISTS idx_estates_division ON estates(division);

-- Add comments
COMMENT ON COLUMN blocks.division IS 'Division code (e.g., AME001, AME002, OLE001, DBE001)';
COMMENT ON COLUMN estates.division IS 'Division code for estate level aggregation';
