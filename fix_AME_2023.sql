-- FIX AME 2023 PRODUCTION DATA
-- Generated from: source/data_produksi_AME_2023.xlsx
-- Total statements: 227
-- UPDATE: 194 | INSERT: 33

-- TARGET TOTALS:
-- Realisasi: 43,233.53 Ton
-- Potensi: 52,157.67 Ton

-- BACKUP FIRST (RECOMMENDED):
-- CREATE TABLE production_annual_backup AS SELECT * FROM production_annual;

INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (1, 2023, 181.76, 175.17482517482514); -- A001A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (2, 2023, 587.74, 658.0419580419581); -- C006A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (3, 2023, 464.79, 539.5104895104895); -- A002A
UPDATE production_annual SET real_ton = 577.01, potensi_ton = 524.2237762237763 WHERE id = 1; -- C007A
UPDATE production_annual SET real_ton = 558.54, potensi_ton = 655.5454545454545 WHERE id = 2; -- A003A
UPDATE production_annual SET real_ton = 666.64, potensi_ton = 572.7272727272726 WHERE id = 3; -- C008A
UPDATE production_annual SET real_ton = 23.24, potensi_ton = 31.21678321678322 WHERE id = 4; -- A003B
UPDATE production_annual SET real_ton = 351.92, potensi_ton = 491.9580419580419 WHERE id = 5; -- B003A
UPDATE production_annual SET real_ton = 367.22, potensi_ton = 415.5594405594406 WHERE id = 6; -- A004A
UPDATE production_annual SET real_ton = 622.06, potensi_ton = 635.6643356643356 WHERE id = 7; -- B004A
UPDATE production_annual SET real_ton = 83.22, potensi_ton = 157.9160839160839 WHERE id = 8; -- A004B
UPDATE production_annual SET real_ton = 404.09, potensi_ton = 517.6573426573426 WHERE id = 9; -- B005A
UPDATE production_annual SET real_ton = 1.1, potensi_ton = 1.3076923076923075 WHERE id = 10; -- A004C
UPDATE production_annual SET real_ton = 424.96, potensi_ton = 332.1188811188811 WHERE id = 11; -- C005A
UPDATE production_annual SET real_ton = 1.34, potensi_ton = 3.076923076923077 WHERE id = 12; -- A004D
UPDATE production_annual SET real_ton = 616.93, potensi_ton = 600.6993006993006 WHERE id = 13; -- C009A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 14; -- A004E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 15; -- A005A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 16; -- A005B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 17; -- A005C
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 18; -- A006A
UPDATE production_annual SET real_ton = 151.34, potensi_ton = 197.9020979020979 WHERE id = 19; -- B001A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 20; -- A007A
UPDATE production_annual SET real_ton = 109.77, potensi_ton = 149.993006993007 WHERE id = 21; -- B002A
UPDATE production_annual SET real_ton = 11.86, potensi_ton = 7.622377622377623 WHERE id = 22; -- A010A
UPDATE production_annual SET real_ton = 286.17, potensi_ton = 501.46853146853147 WHERE id = 23; -- B006A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 24; -- A010B
UPDATE production_annual SET real_ton = 254.9, potensi_ton = 330.1328671328671 WHERE id = 25; -- B007A
UPDATE production_annual SET real_ton = 17.75, potensi_ton = 49.90909090909091 WHERE id = 26; -- A011A
UPDATE production_annual SET real_ton = 598.46, potensi_ton = 623.6013986013985 WHERE id = 27; -- C010A
UPDATE production_annual SET real_ton = 1.4, potensi_ton = 29.26573426573426 WHERE id = 28; -- A011B
UPDATE production_annual SET real_ton = 559.39, potensi_ton = 570.2797202797203 WHERE id = 29; -- C011A
UPDATE production_annual SET real_ton = 89.98, potensi_ton = 114.67132867132868 WHERE id = 30; -- C004A
UPDATE production_annual SET real_ton = 24.77, potensi_ton = 54.972027972027966 WHERE id = 31; -- B001B
UPDATE production_annual SET real_ton = 28.73, potensi_ton = 30.412587412587413 WHERE id = 32; -- C004B
UPDATE production_annual SET real_ton = 1.33, potensi_ton = 3.7202797202797195 WHERE id = 33; -- B001C
UPDATE production_annual SET real_ton = 66.64, potensi_ton = 138.16083916083915 WHERE id = 34; -- C005B
UPDATE production_annual SET real_ton = 4.74, potensi_ton = 3.3566433566433562 WHERE id = 35; -- B001D
UPDATE production_annual SET real_ton = 12.29, potensi_ton = 74.25874125874125 WHERE id = 36; -- C007B
UPDATE production_annual SET real_ton = 2.47, potensi_ton = 4.594405594405594 WHERE id = 37; -- B001E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 38; -- B001F
UPDATE production_annual SET real_ton = 12.45, potensi_ton = 38.76223776223776 WHERE id = 39; -- B002B
UPDATE production_annual SET real_ton = 21.27, potensi_ton = 26.811188811188813 WHERE id = 40; -- B009A
UPDATE production_annual SET real_ton = 11.02, potensi_ton = 42.79720279720279 WHERE id = 41; -- B002C
UPDATE production_annual SET real_ton = 240.92, potensi_ton = 328.78321678321674 WHERE id = 42; -- B010A
UPDATE production_annual SET real_ton = 5.18, potensi_ton = 1.1888111888111887 WHERE id = 43; -- B002D
UPDATE production_annual SET real_ton = 124.42, potensi_ton = 187.55244755244755 WHERE id = 44; -- B011A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 45; -- B002E
UPDATE production_annual SET real_ton = 3.97, potensi_ton = 10.874125874125873 WHERE id = 46; -- C004C
UPDATE production_annual SET real_ton = 3.51, potensi_ton = 18.426573426573427 WHERE id = 47; -- B003B
UPDATE production_annual SET real_ton = 1.38, potensi_ton = 4.027972027972028 WHERE id = 48; -- B003C
UPDATE production_annual SET real_ton = 187.27, potensi_ton = 235.65034965034963 WHERE id = 49; -- B008A
UPDATE production_annual SET real_ton = 5.39, potensi_ton = 3.2195464110357728 WHERE id = 50; -- B003D
UPDATE production_annual SET real_ton = 132.68, potensi_ton = 179.94405594405598 WHERE id = 51; -- B009B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 52; -- B003E
UPDATE production_annual SET real_ton = 1.8, potensi_ton = 1.5104895104895104 WHERE id = 53; -- B006B
UPDATE production_annual SET real_ton = 7.23, potensi_ton = 19.685314685314683 WHERE id = 54; -- B006C
UPDATE production_annual SET real_ton = 104.23, potensi_ton = 12.797202797202797 WHERE id = 55; -- B008B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 56; -- B006D
UPDATE production_annual SET real_ton = 27.99, potensi_ton = 30.419580419580416 WHERE id = 57; -- B009C
UPDATE production_annual SET real_ton = 22.76, potensi_ton = 39.02097902097903 WHERE id = 58; -- B010B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 59; -- B007B
UPDATE production_annual SET real_ton = 9.54, potensi_ton = 108.00699300699301 WHERE id = 60; -- B011B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 61; -- B007C
UPDATE production_annual SET real_ton = 2.27, potensi_ton = 6.853146853146853 WHERE id = 62; -- C005C
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 63; -- B007D
UPDATE production_annual SET real_ton = 4.2, potensi_ton = 12.083916083916083 WHERE id = 64; -- B008C
UPDATE production_annual SET real_ton = 4.93, potensi_ton = 14.160839160839163 WHERE id = 65; -- B008D
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 66; -- B008E
UPDATE production_annual SET real_ton = 3.36, potensi_ton = 7.874125874125875 WHERE id = 67; -- B009D
UPDATE production_annual SET real_ton = 4.13, potensi_ton = 6.643356643356643 WHERE id = 68; -- B011C
UPDATE production_annual SET real_ton = 1.01, potensi_ton = 0.8321678321678322 WHERE id = 69; -- C004D
UPDATE production_annual SET real_ton = 1.15, potensi_ton = 1.7622377622377623 WHERE id = 70; -- C005D
UPDATE production_annual SET real_ton = 3.41, potensi_ton = 6.958041958041958 WHERE id = 71; -- B009E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 72; -- B009F
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 73; -- B009G
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 74; -- C003A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 75; -- C004E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 76; -- C004F
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 77; -- C005E
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (81, 2023, 402.52, 609.0909090909091); -- D001A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (82, 2023, 364.75, 550.6993006993007); -- D002A
UPDATE production_annual SET real_ton = 482.23, potensi_ton = 482.26573426573424 WHERE id = 80; -- F006A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (84, 2023, 413.9, 547.3776223776224); -- D003A
UPDATE production_annual SET real_ton = 436.43, potensi_ton = 398.2587412587412 WHERE id = 82; -- F007A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (86, 2023, 362.98, 496.6783216783217); -- D004A
UPDATE production_annual SET real_ton = 580.76, potensi_ton = 604.3286713286712 WHERE id = 84; -- F008A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (88, 2023, 436.92, 412.93706293706293); -- D005A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (89, 2023, 377.23, 418.00699300699296); -- D006A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (90, 2023, 385.88, 454.1958041958042); -- D007A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (91, 2023, 460.99, 443.8811188811188); -- D008A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (92, 2023, 499.43, 456.99300699300704); -- D009A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (93, 2023, 447.68, 450.1748251748252); -- D010A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (94, 2023, 404.69, 377.6223776223776); -- D011A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (95, 2023, 497.56, 456.46853146853147); -- D012A
UPDATE production_annual SET real_ton = 379.15, potensi_ton = 526.9230769230769 WHERE id = 93; -- E001A
UPDATE production_annual SET real_ton = 329.73, potensi_ton = 499.82517482517477 WHERE id = 94; -- E002A
UPDATE production_annual SET real_ton = 302.29, potensi_ton = 486.71328671328666 WHERE id = 95; -- E003A
UPDATE production_annual SET real_ton = 305.99, potensi_ton = 444.9300699300699 WHERE id = 96; -- E004A
UPDATE production_annual SET real_ton = 412.19, potensi_ton = 455.4195804195805 WHERE id = 97; -- E005A
UPDATE production_annual SET real_ton = 443.27, potensi_ton = 467.8321678321679 WHERE id = 98; -- E006A
UPDATE production_annual SET real_ton = 470.05, potensi_ton = 433.91608391608395 WHERE id = 99; -- E007A
UPDATE production_annual SET real_ton = 482.63, potensi_ton = 478.32167832167835 WHERE id = 100; -- E008A
UPDATE production_annual SET real_ton = 371.11, potensi_ton = 364.8601398601399 WHERE id = 101; -- E009A
UPDATE production_annual SET real_ton = 455.91, potensi_ton = 436.3636363636363 WHERE id = 102; -- E010A
UPDATE production_annual SET real_ton = 431.7, potensi_ton = 431.993006993007 WHERE id = 103; -- E011A
UPDATE production_annual SET real_ton = 466.26, potensi_ton = 452.6223776223775 WHERE id = 104; -- E012A
UPDATE production_annual SET real_ton = 347.55, potensi_ton = 437.5874125874126 WHERE id = 105; -- F001A
UPDATE production_annual SET real_ton = 242.53, potensi_ton = 374.3006993006993 WHERE id = 106; -- F002A
UPDATE production_annual SET real_ton = 225.79, potensi_ton = 291.95804195804203 WHERE id = 107; -- F003A
UPDATE production_annual SET real_ton = 243.4, potensi_ton = 296.67832167832165 WHERE id = 108; -- F004A
UPDATE production_annual SET real_ton = 353.29, potensi_ton = 426.3986013986014 WHERE id = 109; -- F005A
UPDATE production_annual SET real_ton = 353.29, potensi_ton = 677.2867132867133 WHERE id = 109; -- F005A
UPDATE production_annual SET real_ton = 456.02, potensi_ton = 455.06993006992997 WHERE id = 111; -- F009A
UPDATE production_annual SET real_ton = 438.67, potensi_ton = 484.965034965035 WHERE id = 112; -- F010A
UPDATE production_annual SET real_ton = 392.14, potensi_ton = 423.77622377622384 WHERE id = 113; -- F011A
UPDATE production_annual SET real_ton = 473.91, potensi_ton = 530.4195804195804 WHERE id = 114; -- F012A
UPDATE production_annual SET real_ton = 298.2, potensi_ton = 583.4965034965035 WHERE id = 115; -- C020A
UPDATE production_annual SET real_ton = 522.54, potensi_ton = 597.7272727272727 WHERE id = 116; -- C021A
UPDATE production_annual SET real_ton = 424.25, potensi_ton = 440.90909090909093 WHERE id = 117; -- E016A
UPDATE production_annual SET real_ton = 320.0, potensi_ton = 640.9090909090909 WHERE id = 118; -- C022A
UPDATE production_annual SET real_ton = 323.09, potensi_ton = 580.2167832167834 WHERE id = 119; -- C023A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (122, 2023, 419.13, 528.2937062937064); -- D013A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 121; -- C024A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (124, 2023, 429.16, 493.79720279720283); -- D014A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 123; -- C024B
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (126, 2023, 388.55, 480.92307692307685); -- D015A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (127, 2023, 477.95, 526.916083916084); -- D016A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (128, 2023, 354.28, 470.10489510489504); -- D017A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (129, 2023, 396.65, 530.2447552447552); -- D018A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (130, 2023, 353.38, 493.88111888111894); -- D019A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (131, 2023, 346.24, 455.59440559440554); -- D020A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (132, 2023, 447.36, 619.0); -- D021A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (133, 2023, 542.2, 714.160839160839); -- D022A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (134, 2023, 510.59, 663.2797202797203); -- D023A
UPDATE production_annual SET real_ton = 416.97, potensi_ton = 513.2517482517483 WHERE id = 133; -- E013A
UPDATE production_annual SET real_ton = 438.83, potensi_ton = 494.30769230769226 WHERE id = 134; -- E014A
UPDATE production_annual SET real_ton = 361.84, potensi_ton = 507.60139860139856 WHERE id = 135; -- E015A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (138, 2023, 97.78, 235.7902097902098); -- D024A
UPDATE production_annual SET real_ton = 341.0, potensi_ton = 487.06293706293707 WHERE id = 137; -- E017A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (140, 2023, 2.72, 9.020979020979022); -- D024B
UPDATE production_annual SET real_ton = 384.18, potensi_ton = 472.2797202797203 WHERE id = 139; -- E018A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (142, 2023, 3.05, 13.776223776223778); -- D024C
UPDATE production_annual SET real_ton = 430.18, potensi_ton = 538.986013986014 WHERE id = 141; -- E019A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (144, 2023, 2.57, 13.692307692307693); -- D024D
UPDATE production_annual SET real_ton = 384.82, potensi_ton = 512.1958041958042 WHERE id = 143; -- E020A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (146, 2023, 2.09, 5.454545454545453); -- D024E
UPDATE production_annual SET real_ton = 431.8, potensi_ton = 668.979020979021 WHERE id = 145; -- E021A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (148, 2023, 0.0, 0.0); -- D024F
UPDATE production_annual SET real_ton = 523.41, potensi_ton = 713.7272727272727 WHERE id = 147; -- E022A
INSERT INTO production_annual (block_id, year, real_ton, potensi_ton) VALUES (150, 2023, 0.0, 0.0); -- D024G
UPDATE production_annual SET real_ton = 516.38, potensi_ton = 613.3496503496505 WHERE id = 149; -- E023A
UPDATE production_annual SET real_ton = 99.79, potensi_ton = 130.59440559440557 WHERE id = 150; -- E024A
UPDATE production_annual SET real_ton = 2.22, potensi_ton = 5.524475524475525 WHERE id = 151; -- E024B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 152; -- E024C
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 153; -- E024D
UPDATE production_annual SET real_ton = 27.41, potensi_ton = 29.580419580419576 WHERE id = 154; -- A012A
UPDATE production_annual SET real_ton = 521.5, potensi_ton = 610.6083916083917 WHERE id = 155; -- B019A
UPDATE production_annual SET real_ton = 32.11, potensi_ton = 26.36363636363636 WHERE id = 156; -- A012B
UPDATE production_annual SET real_ton = 490.34, potensi_ton = 615.5594405594405 WHERE id = 157; -- B020A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 158; -- A012C
UPDATE production_annual SET real_ton = 543.3, potensi_ton = 536.7972027972028 WHERE id = 159; -- C012A
UPDATE production_annual SET real_ton = 462.86, potensi_ton = 543.8811188811189 WHERE id = 161; -- C019A
UPDATE production_annual SET real_ton = 2.29, potensi_ton = 1.3846153846153846 WHERE id = 162; -- A013A
UPDATE production_annual SET real_ton = 155.62, potensi_ton = 209.2657342657343 WHERE id = 163; -- A020A
UPDATE production_annual SET real_ton = 56.12, potensi_ton = 80.90909090909092 WHERE id = 164; -- A013B
UPDATE production_annual SET real_ton = 577.75, potensi_ton = 744.4965034965035 WHERE id = 165; -- B018A
UPDATE production_annual SET real_ton = 0.61, potensi_ton = 0.24475524475524477 WHERE id = 166; -- A013C
UPDATE production_annual SET real_ton = 568.88, potensi_ton = 653.1468531468531 WHERE id = 167; -- C014A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 168; -- A013D
UPDATE production_annual SET real_ton = 427.85, potensi_ton = 565.1258741258742 WHERE id = 169; -- C018A
UPDATE production_annual SET real_ton = 50.77, potensi_ton = 64.03496503496504 WHERE id = 171; -- A018A
UPDATE production_annual SET real_ton = 73.26, potensi_ton = 119.24475524475524 WHERE id = 172; -- A014A
UPDATE production_annual SET real_ton = 163.06, potensi_ton = 164.86013986013987 WHERE id = 173; -- A019A
UPDATE production_annual SET real_ton = 30.64, potensi_ton = 40.76923076923077 WHERE id = 174; -- A014B
UPDATE production_annual SET real_ton = 123.74, potensi_ton = 161.6083916083916 WHERE id = 175; -- A021A
UPDATE production_annual SET real_ton = 2.72, potensi_ton = 3.6363636363636367 WHERE id = 176; -- A014C
UPDATE production_annual SET real_ton = 52.55, potensi_ton = 90.38461538461539 WHERE id = 177; -- B014A
UPDATE production_annual SET real_ton = 6.77, potensi_ton = 10.664335664335665 WHERE id = 179; -- B015A
UPDATE production_annual SET real_ton = 9.65, potensi_ton = 24.3006993006993 WHERE id = 180; -- B016A
UPDATE production_annual SET real_ton = 8.51, potensi_ton = 7.202797202797202 WHERE id = 181; -- A018B
UPDATE production_annual SET real_ton = 21.81, potensi_ton = 42.65734265734265 WHERE id = 182; -- B017A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 183; -- A018C
UPDATE production_annual SET real_ton = 471.37, potensi_ton = 601.1538461538461 WHERE id = 184; -- B021A
UPDATE production_annual SET real_ton = 168.1, potensi_ton = 199.05594405594408 WHERE id = 185; -- B022A
UPDATE production_annual SET real_ton = 28.56, potensi_ton = 38.37762237762238 WHERE id = 186; -- A019B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 187; -- B022B
UPDATE production_annual SET real_ton = 16.48, potensi_ton = 19.2937062937063 WHERE id = 188; -- A019C
UPDATE production_annual SET real_ton = 560.41, potensi_ton = 630.7692307692307 WHERE id = 189; -- C013A
UPDATE production_annual SET real_ton = 508.81, potensi_ton = 562.9370629370627 WHERE id = 190; -- C015A
UPDATE production_annual SET real_ton = 57.21, potensi_ton = 89.97202797202799 WHERE id = 191; -- A020B
UPDATE production_annual SET real_ton = 487.1, potensi_ton = 656.1188811188811 WHERE id = 192; -- C016A
UPDATE production_annual SET real_ton = 9.68, potensi_ton = 13.216783216783215 WHERE id = 193; -- A020C
UPDATE production_annual SET real_ton = 467.59, potensi_ton = 612.5874125874125 WHERE id = 194; -- C017A
UPDATE production_annual SET real_ton = 40.52, potensi_ton = 54.01398601398601 WHERE id = 195; -- C018B
UPDATE production_annual SET real_ton = 39.41, potensi_ton = 53.23776223776223 WHERE id = 196; -- A021B
UPDATE production_annual SET real_ton = 371.03, potensi_ton = 329.93706293706293 WHERE id = 197; -- B012A
UPDATE production_annual SET real_ton = 21.05, potensi_ton = 26.223776223776227 WHERE id = 198; -- B012B
UPDATE production_annual SET real_ton = 2.0, potensi_ton = 3.8391608391608396 WHERE id = 199; -- B012C
UPDATE production_annual SET real_ton = 349.5, potensi_ton = 335.62937062937056 WHERE id = 200; -- B013A
UPDATE production_annual SET real_ton = 21.28, potensi_ton = 20.55944055944056 WHERE id = 202; -- B013B
UPDATE production_annual SET real_ton = 17.46, potensi_ton = 20.0979020979021 WHERE id = 204; -- B015B
UPDATE production_annual SET real_ton = 38.83, potensi_ton = 49.930069930069926 WHERE id = 205; -- B014B
UPDATE production_annual SET real_ton = 8.37, potensi_ton = 13.804195804195805 WHERE id = 206; -- B016B
UPDATE production_annual SET real_ton = 67.92, potensi_ton = 100.1958041958042 WHERE id = 207; -- B014C
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 208; -- B020B
UPDATE production_annual SET real_ton = 2.67, potensi_ton = 2.0979020979020975 WHERE id = 209; -- B014D
UPDATE production_annual SET real_ton = 10.09, potensi_ton = 18.34965034965035 WHERE id = 210; -- B021B
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 211; -- B014E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 212; -- B015C
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 213; -- B015D
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 214; -- B015E
UPDATE production_annual SET real_ton = 2.21, potensi_ton = 4.405594405594406 WHERE id = 215; -- B016C
UPDATE production_annual SET real_ton = 26.38, potensi_ton = 15.174825174825173 WHERE id = 216; -- B017B
UPDATE production_annual SET real_ton = 0.65, potensi_ton = 0.6923076923076924 WHERE id = 217; -- B016D
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 218; -- B016E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 219; -- B016F
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 220; -- B016G
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 221; -- B016H
UPDATE production_annual SET real_ton = 2.69, potensi_ton = 3.7132867132867133 WHERE id = 222; -- B017C
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 223; -- B017D
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 224; -- B017E
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 225; -- B017F
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 226; -- B017G
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 227; -- B024A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 228; -- B023A
UPDATE production_annual SET real_ton = 0.0, potensi_ton = 0.0 WHERE id = 229; -- B024B

-- VERIFICATION QUERY:
-- Check AME 2023 totals after running:

SELECT 
    b.block_code,
    p.year,
    p.real_ton,
    p.potensi_ton
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND (b.block_code LIKE 'A%' OR b.block_code LIKE 'B%' OR 
       b.block_code LIKE 'C%' OR b.block_code LIKE 'E%' OR b.block_code LIKE 'F%')
ORDER BY b.block_code;

-- Summary:
SELECT 
    SUM(p.real_ton) as total_realisasi,
    SUM(p.potensi_ton) as total_potensi
FROM production_annual p
JOIN blocks b ON p.block_id = b.id
WHERE p.year = 2023 
  AND (b.block_code LIKE 'A%' OR b.block_code LIKE 'B%' OR 
       b.block_code LIKE 'C%' OR b.block_code LIKE 'E%' OR b.block_code LIKE 'F%');
