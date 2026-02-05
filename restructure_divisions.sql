-- RAPID DATABASE RESTRUCTURE - Run in Supabase SQL Editor
-- Time: 1 minute total
-- ============================================================

-- 1. Create divisions table (10 seconds)
CREATE TABLE IF NOT EXISTS divisions (
    id SERIAL PRIMARY KEY,
    division_code VARCHAR(10) UNIQUE NOT NULL,
    division_name VARCHAR(100) NOT NULL,
    estate_id INTEGER REFERENCES estates(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Insert 13 divisions (20 seconds)
-- Get estate IDs first
INSERT INTO divisions (division_code, division_name, estate_id)
SELECT 'AME001', 'AME Division 001', id FROM estates WHERE estate_code = 'AME'
UNION ALL
SELECT 'AME002', 'AME Division 002', id FROM estates WHERE estate_code = 'AME'
UNION ALL
SELECT 'AME003', 'AME Division 003', id FROM estates WHERE estate_code = 'AME'
UNION ALL
SELECT 'AME004', 'AME Division 004', id FROM estates WHERE estate_code = 'AME'
UNION ALL
SELECT 'OLE001', 'OLE Division 001', id FROM estates WHERE estate_code = 'OLE'
UNION ALL
SELECT 'OLE002', 'OLE Division 002', id FROM estates WHERE estate_code = 'OLE'
UNION ALL
SELECT 'OLE003', 'OLE Division 003', id FROM estates WHERE estate_code = 'OLE'
UNION ALL
SELECT 'OLE004', 'OLE Division 004', id FROM estates WHERE estate_code = 'OLE'
UNION ALL
SELECT 'DBE001', 'DBE Division 001', id FROM estates WHERE estate_code = 'DBE'
UNION ALL
SELECT 'DBE002', 'DBE Division 002', id FROM estates WHERE estate_code = 'DBE'
UNION ALL
SELECT 'DBE003', 'DBE Division 003', id FROM estates WHERE estate_code = 'DBE'
UNION ALL
SELECT 'DBE004', 'DBE Division 004', id FROM estates WHERE estate_code = 'DBE'
UNION ALL
SELECT 'DBE005', 'DBE Division 005', id FROM estates WHERE estate_code = 'DBE'
ON CONFLICT (division_code) DO NOTHING;

-- 3. Add division_id column to blocks (10 seconds)
ALTER TABLE blocks ADD COLUMN IF NOT EXISTS division_id INTEGER REFERENCES divisions(id);

-- 4. Migrate data - Update division_id based on old division column (20 seconds)
UPDATE blocks b
SET division_id = d.id
FROM divisions d
WHERE b.division = d.division_code;

-- 5. Verification
SELECT 
    'Total divisions' as metric, COUNT(*)::text as value FROM divisions
UNION ALL
SELECT 
    'Blocks with division_id', COUNT(*)::text FROM blocks WHERE division_id IS NOT NULL
UNION ALL
SELECT 
    'Blocks without division_id', COUNT(*)::text FROM blocks WHERE division_id IS NULL;

-- Show divisions per estate
SELECT 
    e.estate_code,
    COUNT(d.id) as division_count,
    STRING_AGG(d.division_code, ', ' ORDER BY d.division_code) as divisions
FROM estates e
LEFT JOIN divisions d ON d.estate_id = e.id
GROUP BY e.estate_code
ORDER BY e.estate_code;
