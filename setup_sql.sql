-- ============================================================================
-- SUPABASE SETUP: Indexes, Views, and RLS Policies
-- Generated: 2026-02-03
-- Purpose: Optimize normalized schema for performance
-- ============================================================================

-- ============================================================================
-- STEP 1: CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Estates table indexes
CREATE INDEX IF NOT EXISTS idx_estates_code ON estates(estate_code);
COMMENT ON INDEX idx_estates_code IS 'Index for estate lookups';

-- Blocks table indexes
CREATE INDEX IF NOT EXISTS idx_blocks_code ON blocks(block_code);
CREATE INDEX IF NOT EXISTS idx_blocks_estate ON blocks(estate_code);
CREATE INDEX IF NOT EXISTS idx_blocks_year ON blocks(year_planted);
CREATE INDEX IF NOT EXISTS idx_blocks_estate_year ON blocks(estate_code, year_planted);
COMMENT ON INDEX idx_blocks_code IS 'Index for block code lookups';
COMMENT ON INDEX idx_blocks_estate IS 'Index for filtering by estate';
COMMENT ON INDEX idx_blocks_year IS 'Index for filtering by year planted';
COMMENT ON INDEX idx_blocks_estate_year IS 'Composite index for estate + year queries';

-- Production data indexes
CREATE INDEX IF NOT EXISTS idx_production_block ON production_data(block_code);
COMMENT ON INDEX idx_production_block IS 'Index for joining production data';

-- Realisasi potensi indexes
CREATE INDEX IF NOT EXISTS idx_realisasi_block ON realisasi_potensi(block_code);
COMMENT ON INDEX idx_realisasi_block IS 'Index for joining realisasi data';

-- ============================================================================
-- STEP 2: CREATE MATERIALIZED VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View 1: Complete data view (for convenience)
CREATE OR REPLACE VIEW v_complete_data AS
SELECT 
    b.id as block_id,
    b.block_code,
    b.estate_code,
    e.estate_code as estate_name,
    b.area_ha,
    b.year_planted,
    b.number,
    pd.id as production_id,
    rp.id as realisasi_id
FROM blocks b
LEFT JOIN estates e ON b.estate_code = e.estate_code
LEFT JOIN production_data pd ON b.block_code = pd.block_code
LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code;

COMMENT ON VIEW v_complete_data IS 'Complete view joining all tables for easy access';

-- View 2: Estate summary (materialized for performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_estate_summary AS
SELECT 
    b.estate_code,
    COUNT(*) as total_blocks,
    SUM(b.area_ha) as total_area_ha,
    AVG(b.area_ha) as avg_area_ha,
    MIN(b.year_planted) as earliest_year,
    MAX(b.year_planted) as latest_year,
    COUNT(CASE WHEN b.year_planted > 2015 THEN 1 END) as blocks_after_2015
FROM blocks b
WHERE b.estate_code IS NOT NULL
GROUP BY b.estate_code
ORDER BY total_blocks DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_estate_summary_estate ON mv_estate_summary(estate_code);
COMMENT ON MATERIALIZED VIEW mv_estate_summary IS 'Pre-computed estate statistics for dashboard';

-- View 3: Block details with production summary
CREATE OR REPLACE VIEW v_block_details AS
SELECT 
    b.block_code,
    b.estate_code,
    b.area_ha,
    b.year_planted,
    b.number,
    pd.id as has_production_data,
    rp.id as has_realisasi_data
FROM blocks b
LEFT JOIN production_data pd ON b.block_code = pd.block_code
LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code;

COMMENT ON VIEW v_block_details IS 'Block overview with data availability flags';

-- ============================================================================
-- STEP 3: CREATE REFRESH FUNCTION FOR MATERIALIZED VIEWS
-- ============================================================================

CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_estate_summary;
    RAISE NOTICE 'Materialized views refreshed successfully';
END;
$$;

COMMENT ON FUNCTION refresh_materialized_views IS 'Refresh all materialized views (call periodically)';

-- ============================================================================
-- STEP 4: ROW LEVEL SECURITY (Optional - enable if needed)
-- ============================================================================

-- Enable RLS on tables (uncomment if needed)
-- ALTER TABLE estates ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE blocks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE production_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE realisasi_potensi ENABLE ROW LEVEL SECURITY;

-- Create policies for read access (uncomment if RLS enabled)
-- CREATE POLICY "Enable read access for all users" ON estates FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON blocks FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON production_data FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON realisasi_potensi FOR SELECT USING (true);

-- ============================================================================
-- STEP 5: HELPFUL FUNCTIONS FOR ANALYSIS
-- ============================================================================

-- Function: Get blocks by estate
CREATE OR REPLACE FUNCTION get_blocks_by_estate(estate_filter TEXT)
RETURNS TABLE (
    block_code VARCHAR,
    area_ha DECIMAL,
    year_planted INTEGER,
    has_production BOOLEAN,
    has_realisasi BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.block_code,
        b.area_ha,
        b.year_planted,
        (pd.id IS NOT NULL) as has_production,
        (rp.id IS NOT NULL) as has_realisasi
    FROM blocks b
    LEFT JOIN production_data pd ON b.block_code = pd.block_code
    LEFT JOIN realisasi_potensi rp ON b.block_code = rp.block_code
    WHERE b.estate_code = estate_filter
    ORDER BY b.block_code;
END;
$$;

COMMENT ON FUNCTION get_blocks_by_estate IS 'Get all blocks for a specific estate with data availability';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('estates', 'blocks', 'production_data', 'realisasi_potensi')
ORDER BY tablename, indexname;

-- Verify views
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname = 'public'
AND viewname LIKE 'v_%'
ORDER BY viewname;

-- Verify materialized views
SELECT 
    schemaname,
    matviewname
FROM pg_matviews
WHERE schemaname = 'public'
ORDER BY matviewname;

-- Test estate summary view
SELECT * FROM mv_estate_summary LIMIT 5;

-- ============================================================================
-- SETUP COMPLETE!
-- ============================================================================

-- To refresh materialized views manually:
-- SELECT refresh_materialized_views();

-- To set up automatic refresh (every hour):
-- SELECT cron.schedule(
--     'refresh-mv-estate-summary',
--     '0 * * * *',  -- Every hour
--     $$ SELECT refresh_materialized_views(); $$
-- );
