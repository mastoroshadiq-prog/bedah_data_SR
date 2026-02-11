-- INSERT MISSING AME 2023 BLOCKS
-- Blocks: A001A, A002A, C006A
-- Total: 3 records
-- Actual: 1234.29 Ton
-- Target: 1372.73 Ton

-- Option 1: Let database auto-generate id (RECOMMENDED)
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) 
VALUES (1, 2023, 181.76, 175.17); -- A001A

INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) 
VALUES (3, 2023, 464.79, 539.51); -- A002A

INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) 
VALUES (2, 2023, 587.74, 658.04); -- C006A

-- VERIFY after running:
-- Check that these 3 blocks now appear in AME 2023 data

SELECT b.block_code, p.year, p.real_ton, p.potensi_ton
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND b.block_code IN ('A001A', 'A002A', 'C006A')
ORDER BY b.block_code;
