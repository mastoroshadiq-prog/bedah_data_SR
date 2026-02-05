"""
Generate SQL INSERT statements from CSV
For direct execution in Supabase SQL Editor
"""
import pandas as pd

# Read CSV
df = pd.read_csv('output/normalized_tables/phase2_metadata/block_pest_disease.csv')

# Keep 'id' column - table requires it (NOT NULL constraint)

print(f"Generating SQL for {len(df)} records...")

# Start SQL file
sql_lines = []
sql_lines.append("-- =====================================================")
sql_lines.append("-- RE-UPLOAD BLOCK_PEST_DISEASE DATA")
sql_lines.append("-- Source: block_pest_disease.csv (normalized)")
sql_lines.append(f"-- Total records: {len(df)}")
sql_lines.append("-- =====================================================")
sql_lines.append("")

# 1. Delete existing data
sql_lines.append("-- 1. Delete all existing records")
sql_lines.append("DELETE FROM block_pest_disease;")
sql_lines.append("")

# 2. Generate INSERT statements in batches
sql_lines.append("-- 2. Insert fresh data")
batch_size = 100
total_batches = (len(df) + batch_size - 1) // batch_size

for batch_num in range(total_batches):
    start_idx = batch_num * batch_size
    end_idx = min(start_idx + batch_size, len(df))
    batch_df = df.iloc[start_idx:end_idx]
    
    sql_lines.append(f"-- Batch {batch_num + 1}/{total_batches} (rows {start_idx + 1}-{end_idx})")
    sql_lines.append("INSERT INTO block_pest_disease (id, block_id, block_code, serangan_ganoderma_pkk_stadium_1_2, stadium_3_4, pct_serangan, recorded_date)")
    sql_lines.append("VALUES")
    
    values = []
    for idx, row in batch_df.iterrows():
        # Escape single quotes in strings
        block_code = str(row['block_code']).replace("'", "''")
        recorded_date = str(row['recorded_date']).replace("'", "''")
        
        # Handle NULL values
        serangan = 'NULL' if pd.isna(row['serangan_ganoderma_pkk_stadium_1_2']) else str(float(row['serangan_ganoderma_pkk_stadium_1_2']))
        stadium_34 = 'NULL' if pd.isna(row['stadium_3_4']) else str(float(row['stadium_3_4']))
        
        value = f"({int(row['id'])}, {row['block_id']}, '{block_code}', {serangan}, {stadium_34}, {row['pct_serangan']}, '{recorded_date}')"
        values.append(value)
    
    sql_lines.append(",\n".join(values) + ";")
    sql_lines.append("")

# 3. Verification query
sql_lines.append("-- 3. Verification - Check G001A")
sql_lines.append("SELECT b.block_code, bpd.pct_serangan, bpd.pct_serangan * 100 as pct_display")
sql_lines.append("FROM block_pest_disease bpd")
sql_lines.append("JOIN blocks b ON b.id = bpd.block_id")
sql_lines.append("WHERE b.block_code = 'G001A';")
sql_lines.append("")

sql_lines.append("-- 4. Overall statistics")
sql_lines.append("SELECT ")
sql_lines.append("  COUNT(*) as total_records,")
sql_lines.append("  COUNT(CASE WHEN pct_serangan = 0 THEN 1 END) as zero_count,")
sql_lines.append("  COUNT(CASE WHEN pct_serangan > 0 THEN 1 END) as nonzero_count,")
sql_lines.append("  AVG(pct_serangan) as avg_pct,")
sql_lines.append("  MAX(pct_serangan) as max_pct")
sql_lines.append("FROM block_pest_disease;")

# Write to file
output_file = 'reupload_ganoderma_data.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f"✅ SQL file generated: {output_file}")
print(f"   Total lines: {len(sql_lines)}")
print(f"   Batches: {total_batches}")
print(f"\nNext steps:")
print(f"1. Open Supabase Dashboard → SQL Editor")
print(f"2. Copy & paste contents of {output_file}")
print(f"3. Click RUN")
print(f"4. Check verification results")
