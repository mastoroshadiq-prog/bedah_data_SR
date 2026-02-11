-- INSERT MISSING AME 2023 BLOCKS (FIXED)
-- Blocks: A001A, A002A, C006A
-- Total: 3 records
-- Actual: 1234.29 Ton
-- Target: 1372.73 Ton

-- Insert with all required columns
-- Setting gap fields to be calculated as (real - potensi)

-- A001A
INSERT INTO production_annual (
    block_id, year, real_ton, potensi_ton,
    gap_ton, gap_pct_ton
) VALUES (
    1, 2023, 181.76, 175.17,
    181.76 - 175.17, ((181.76 - 175.17) / 175.17 * 100)
);

-- A002A  
INSERT INTO production_annual (
    block_id, year, real_ton, potensi_ton,
    gap_ton, gap_pct_ton
) VALUES (
    3, 2023, 464.79, 539.51,
    464.79 - 539.51, ((464.79 - 539.51) / 539.51 * 100)
);

-- C006A
INSERT INTO production_annual (
    block_id, year, real_ton, potensi_ton,
    gap_ton, gap_pct_ton
) VALUES (
    2, 2023, 587.74, 658.04,
    587.74 - 658.04, ((587.74 - 658.04) / 658.04 * 100)
);

-- VERIFY after running:
SELECT b.block_code, p.year, p.real_ton, p.potensi_ton, p.gap_ton
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND b.block_code IN ('A001A', 'A002A', 'C006A')
ORDER BY b.block_code;
