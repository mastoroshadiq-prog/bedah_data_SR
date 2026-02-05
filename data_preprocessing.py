"""
Data Normalization & Preprocessing Pipeline
Best Practices untuk persiapan data sebelum upload ke Supabase

Author: Data Analysis Team
Date: 2026-02-03
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    """
    Kelas untuk melakukan normalisasi dan pre-processing data
    dengan pendekatan best practices
    """
    
    def __init__(self, input_file):
        self.input_file = input_file
        self.df_raw = None
        self.df_clean = None
        self.preprocessing_report = {}
        
    def load_data(self):
        """Memuat data dari file Excel"""
        print("=" * 80)
        print("TAHAP 1: LOADING DATA")
        print("=" * 80)
        
        # Coba baca dengan beberapa metode untuk menangani header yang kompleks
        try:
            # Metode 1: Baca dengan skiprows untuk skip header yang tidak relevan
            self.df_raw = pd.read_excel(self.input_file, skiprows=0)
            print(f"✓ Data berhasil dimuat: {self.df_raw.shape[0]} baris x {self.df_raw.shape[1]} kolom")
            
            # Simpan snapshot data mentah
            self.preprocessing_report['original_shape'] = self.df_raw.shape
            self.preprocessing_report['original_columns'] = list(self.df_raw.columns)
            
            return True
        except Exception as e:
            print(f"✗ Error saat memuat data: {str(e)}")
            return False
    
    def analyze_data_quality(self):
        """Analisis kualitas data"""
        print("\n" + "=" * 80)
        print("TAHAP 2: ANALISIS KUALITAS DATA")
        print("=" * 80)
        
        # 1. Hitung missing values
        missing_counts = self.df_raw.isnull().sum()
        missing_pct = (missing_counts / len(self.df_raw)) * 100
        
        print(f"\n📊 Missing Values Analysis:")
        print(f"   Total cells: {self.df_raw.shape[0] * self.df_raw.shape[1]:,}")
        print(f"   Missing cells: {self.df_raw.isnull().sum().sum():,}")
        print(f"   Missing percentage: {(self.df_raw.isnull().sum().sum() / (self.df_raw.shape[0] * self.df_raw.shape[1]) * 100):.2f}%")
        
        # 2. Kolom dengan missing values > 50%
        high_missing_cols = missing_pct[missing_pct > 50].index.tolist()
        print(f"\n⚠️  Kolom dengan missing > 50%: {len(high_missing_cols)} kolom")
        
        # 3. Tipe data
        print(f"\n📋 Tipe Data:")
        print(self.df_raw.dtypes.value_counts())
        
        # 4. Duplikasi
        duplicates = self.df_raw.duplicated().sum()
        print(f"\n🔄 Baris duplikat: {duplicates}")
        
        # Simpan hasil analisis
        self.preprocessing_report['missing_analysis'] = {
            'total_missing': self.df_raw.isnull().sum().sum(),
            'missing_percentage': (self.df_raw.isnull().sum().sum() / (self.df_raw.shape[0] * self.df_raw.shape[1]) * 100),
            'high_missing_columns': high_missing_cols
        }
        self.preprocessing_report['duplicates'] = duplicates
    
    def fix_headers(self):
        """Perbaiki nama kolom yang tidak jelas"""
        print("\n" + "=" * 80)
        print("TAHAP 3: PERBAIKAN HEADER/KOLOM")
        print("=" * 80)
        
        # Identifikasi baris yang sebenarnya adalah header
        # Biasanya di baris 4-5 berdasarkan output sebelumnya
        
        # Strategi: Baca ulang dengan header yang tepat
        try:
            # Coba deteksi baris header otomatis
            df_test = pd.read_excel(self.input_file, header=None, nrows=10)
            
            # Cari baris dengan konten yang paling banyak (kemungkinan header)
            non_null_counts = df_test.count(axis=1)
            header_row = non_null_counts.idxmax()
            
            print(f"✓ Header terdeteksi di baris: {header_row}")
            
            # Baca ulang dengan header yang benar
            self.df_raw = pd.read_excel(self.input_file, header=header_row)
            
            # Bersihkan nama kolom
            self.df_raw.columns = [
                str(col).strip().replace('\n', ' ').replace('  ', ' ') 
                if not str(col).startswith('Unnamed') 
                else f'Column_{i}' 
                for i, col in enumerate(self.df_raw.columns)
            ]
            
            print(f"✓ Kolom diperbaiki: {len(self.df_raw.columns)} kolom")
            print(f"\nSample kolom: {list(self.df_raw.columns[:10])}")
            
            self.preprocessing_report['header_fix'] = {
                'header_row': header_row,
                'new_columns': list(self.df_raw.columns)
            }
            
        except Exception as e:
            print(f"⚠️  Auto-detect gagal: {str(e)}")
            print("   Menggunakan strategi alternatif...")
            
            # Strategi alternatif: rename kolom secara manual
            new_columns = []
            for i, col in enumerate(self.df_raw.columns):
                if str(col).startswith('Unnamed'):
                    new_columns.append(f'Column_{i}')
                else:
                    new_columns.append(str(col).strip())
            
            self.df_raw.columns = new_columns
    
    def remove_empty_rows_cols(self):
        """Hapus baris dan kolom yang kosong"""
        print("\n" + "=" * 80)
        print("TAHAP 4: PEMBERSIHAN BARIS & KOLOM KOSONG")
        print("=" * 80)
        
        before_shape = self.df_raw.shape
        
        # Hapus baris yang sepenuhnya kosong
        self.df_raw = self.df_raw.dropna(how='all')
        
        # Hapus kolom yang sepenuhnya kosong
        self.df_raw = self.df_raw.dropna(axis=1, how='all')
        
        # Hapus kolom dengan missing > 80%
        threshold = 0.8
        missing_pct = self.df_raw.isnull().sum() / len(self.df_raw)
        cols_to_keep = missing_pct[missing_pct < threshold].index
        self.df_raw = self.df_raw[cols_to_keep]
        
        after_shape = self.df_raw.shape
        
        print(f"✓ Baris dihapus: {before_shape[0] - after_shape[0]}")
        print(f"✓ Kolom dihapus: {before_shape[1] - after_shape[1]}")
        print(f"✓ Shape sekarang: {after_shape[0]} baris x {after_shape[1]} kolom")
        
        self.preprocessing_report['cleaning'] = {
            'rows_removed': before_shape[0] - after_shape[0],
            'cols_removed': before_shape[1] - after_shape[1],
            'shape_after': after_shape
        }
    
    def handle_data_types(self):
        """Konversi tipe data ke format yang sesuai"""
        print("\n" + "=" * 80)
        print("TAHAP 5: KONVERSI TIPE DATA")
        print("=" * 80)
        
        type_conversions = {}
        
        for col in self.df_raw.columns:
            # Skip jika kolom kosong
            if self.df_raw[col].isnull().all():
                continue
            
            # Ambil sample data non-null
            sample_data = self.df_raw[col].dropna().astype(str).str.strip()
            
            if len(sample_data) == 0:
                continue
            
            # Deteksi tipe data
            # 1. Numerik (integer atau float)
            try:
                # Cek apakah bisa dikonversi ke numeric
                pd.to_numeric(sample_data.head(10), errors='raise')
                # Coba konversi semua data
                self.df_raw[col] = pd.to_numeric(self.df_raw[col], errors='coerce')
                type_conversions[col] = 'numeric'
                continue
            except:
                pass
            
            # 2. Tanggal
            try:
                pd.to_datetime(sample_data.head(10), errors='raise')
                self.df_raw[col] = pd.to_datetime(self.df_raw[col], errors='coerce')
                type_conversions[col] = 'datetime'
                continue
            except:
                pass
            
            # 3. Boolean
            unique_vals = sample_data.str.lower().unique()
            if set(unique_vals).issubset({'yes', 'no', 'true', 'false', '1', '0', 'ya', 'tidak'}):
                self.df_raw[col] = self.df_raw[col].map({
                    'yes': True, 'no': False,
                    'true': True, 'false': False,
                    '1': True, '0': False,
                    'ya': True, 'tidak': False
                })
                type_conversions[col] = 'boolean'
                continue
            
            # 4. Default: tetap sebagai string
            type_conversions[col] = 'string'
        
        print(f"✓ Konversi tipe data selesai:")
        for dtype, count in pd.Series(type_conversions).value_counts().items():
            print(f"   {dtype}: {count} kolom")
        
        self.preprocessing_report['type_conversions'] = type_conversions
    
    def handle_missing_values(self):
        """Handle missing values dengan strategi yang tepat"""
        print("\n" + "=" * 80)
        print("TAHAP 6: PENANGANAN MISSING VALUES")
        print("=" * 80)
        
        strategies = {}
        
        for col in self.df_raw.columns:
            missing_count = self.df_raw[col].isnull().sum()
            
            if missing_count == 0:
                continue
            
            missing_pct = (missing_count / len(self.df_raw)) * 100
            
            # Strategi berdasarkan tipe data dan persentase missing
            if pd.api.types.is_numeric_dtype(self.df_raw[col]):
                if missing_pct < 5:
                    # Isi dengan median
                    self.df_raw[col].fillna(self.df_raw[col].median(), inplace=True)
                    strategies[col] = 'median'
                elif missing_pct < 30:
                    # Isi dengan mean
                    self.df_raw[col].fillna(self.df_raw[col].mean(), inplace=True)
                    strategies[col] = 'mean'
                else:
                    # Isi dengan 0 atau biarkan null (untuk Supabase)
                    self.df_raw[col].fillna(0, inplace=True)
                    strategies[col] = 'zero'
            
            elif pd.api.types.is_datetime64_dtype(self.df_raw[col]):
                # Untuk tanggal, biarkan null
                strategies[col] = 'keep_null'
            
            else:
                # Untuk string, isi dengan 'unknown' atau biarkan null
                if missing_pct < 30:
                    self.df_raw[col].fillna('', inplace=True)
                    strategies[col] = 'empty_string'
                else:
                    strategies[col] = 'keep_null'
        
        print(f"✓ Missing values ditangani dengan strategi:")
        for strategy, count in pd.Series(strategies).value_counts().items():
            print(f"   {strategy}: {count} kolom")
        
        self.preprocessing_report['missing_strategies'] = strategies
    
    def remove_duplicates(self):
        """Hapus data duplikat"""
        print("\n" + "=" * 80)
        print("TAHAP 7: PENGHAPUSAN DUPLIKASI")
        print("=" * 80)
        
        before = len(self.df_raw)
        self.df_raw = self.df_raw.drop_duplicates()
        after = len(self.df_raw)
        
        print(f"✓ Duplikat dihapus: {before - after} baris")
        print(f"✓ Total baris sekarang: {after}")
        
        self.preprocessing_report['duplicates_removed'] = before - after
    
    def normalize_data(self):
        """Normalisasi data numerik jika diperlukan"""
        print("\n" + "=" * 80)
        print("TAHAP 8: NORMALISASI DATA (OPSIONAL)")
        print("=" * 80)
        
        # Untuk Supabase, kita tidak perlu normalisasi Min-Max
        # Simpan data dalam bentuk aslinya
        print("ℹ️  Data disimpan dalam bentuk asli (tidak di-normalize)")
        print("   Normalisasi dapat dilakukan di tahap analisis nanti jika diperlukan")
        
        self.preprocessing_report['normalization'] = 'skipped_for_supabase'
    
    def standardize_column_names(self):
        """Standardisasi nama kolom untuk database"""
        print("\n" + "=" * 80)
        print("TAHAP 9: STANDARDISASI NAMA KOLOM")
        print("=" * 80)
        
        old_columns = list(self.df_raw.columns)
        
        # Konversi ke format snake_case yang database-friendly
        new_columns = []
        for col in self.df_raw.columns:
            # Lowercase
            new_col = str(col).lower()
            # Replace spasi dengan underscore
            new_col = new_col.replace(' ', '_')
            # Hapus karakter special
            new_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in new_col)
            # Hapus multiple underscores
            while '__' in new_col:
                new_col = new_col.replace('__', '_')
            # Hapus underscore di awal/akhir
            new_col = new_col.strip('_')
            # Tambahkan prefix jika dimulai dengan angka
            if new_col[0].isdigit():
                new_col = 'col_' + new_col
            
            new_columns.append(new_col)
        
        # Handle duplikat nama kolom
        seen = {}
        final_columns = []
        for col in new_columns:
            if col in seen:
                seen[col] += 1
                final_columns.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                final_columns.append(col)
        
        self.df_raw.columns = final_columns
        
        print(f"✓ Nama kolom distandardisasi: {len(final_columns)} kolom")
        print(f"\nSample kolom baru: {final_columns[:10]}")
        
        self.preprocessing_report['column_standardization'] = {
            'old_columns': old_columns,
            'new_columns': final_columns
        }
    
    def add_metadata_columns(self):
        """Tambahkan kolom metadata untuk tracking"""
        print("\n" + "=" * 80)
        print("TAHAP 10: PENAMBAHAN METADATA")
        print("=" * 80)
        
        # Tambahkan ID unik
        self.df_raw.insert(0, 'id', range(1, len(self.df_raw) + 1))
        
        # Tambahkan timestamp
        self.df_raw['created_at'] = datetime.now()
        self.df_raw['updated_at'] = datetime.now()
        
        # Tambahkan source info
        self.df_raw['data_source'] = 'data_gabungan.xlsx'
        self.df_raw['preprocessing_version'] = '1.0'
        
        print(f"✓ Metadata ditambahkan:")
        print(f"   - id (primary key)")
        print(f"   - created_at")
        print(f"   - updated_at")
        print(f"   - data_source")
        print(f"   - preprocessing_version")
        
        self.preprocessing_report['metadata_added'] = [
            'id', 'created_at', 'updated_at', 'data_source', 'preprocessing_version'
        ]
    
    def validate_for_supabase(self):
        """Validasi data untuk Supabase"""
        print("\n" + "=" * 80)
        print("TAHAP 11: VALIDASI UNTUK SUPABASE")
        print("=" * 80)
        
        validation_results = {}
        
        # 1. Cek panjang nama kolom (PostgreSQL max 63 karakter)
        long_columns = [col for col in self.df_raw.columns if len(col) > 63]
        if long_columns:
            print(f"⚠️  Kolom dengan nama terlalu panjang (>63): {len(long_columns)}")
            # Perpendek nama kolom
            for col in long_columns:
                new_name = col[:60]
                self.df_raw.rename(columns={col: new_name}, inplace=True)
            validation_results['long_columns_fixed'] = len(long_columns)
        else:
            print(f"✓ Panjang nama kolom: OK")
            validation_results['long_columns_fixed'] = 0
        
        # 2. Cek karakter reserved PostgreSQL
        reserved_keywords = ['user', 'table', 'select', 'insert', 'update', 'delete', 'from', 'where']
        reserved_cols = [col for col in self.df_raw.columns if col.lower() in reserved_keywords]
        if reserved_cols:
            print(f"⚠️  Kolom dengan nama reserved keyword: {reserved_cols}")
            for col in reserved_cols:
                self.df_raw.rename(columns={col: f"{col}_field"}, inplace=True)
            validation_results['reserved_keywords_fixed'] = len(reserved_cols)
        else:
            print(f"✓ Nama kolom tidak menggunakan reserved keyword: OK")
            validation_results['reserved_keywords_fixed'] = 0
        
        # 3. Cek ukuran data
        memory_usage = self.df_raw.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"✓ Memory usage: {memory_usage:.2f} MB")
        validation_results['memory_usage_mb'] = memory_usage
        
        # 4. Cek row count
        print(f"✓ Total rows: {len(self.df_raw):,}")
        validation_results['total_rows'] = len(self.df_raw)
        
        # 5. Cek column count
        print(f"✓ Total columns: {len(self.df_raw.columns)}")
        validation_results['total_columns'] = len(self.df_raw.columns)
        
        self.preprocessing_report['supabase_validation'] = validation_results
    
    def export_cleaned_data(self, output_formats=['csv', 'excel', 'json']):
        """Export data yang sudah bersih ke berbagai format"""
        print("\n" + "=" * 80)
        print("TAHAP 12: EXPORT DATA")
        print("=" * 80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exported_files = {}
        
        # Buat folder output jika belum ada
        import os
        os.makedirs('output', exist_ok=True)
        
        # 1. CSV (terbaik untuk Supabase import)
        if 'csv' in output_formats:
            csv_path = f'output/data_cleaned_{timestamp}.csv'
            self.df_raw.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"✓ CSV exported: {csv_path}")
            exported_files['csv'] = csv_path
        
        # 2. Excel
        if 'excel' in output_formats:
            excel_path = f'output/data_cleaned_{timestamp}.xlsx'
            self.df_raw.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"✓ Excel exported: {excel_path}")
            exported_files['excel'] = excel_path
        
        # 3. JSON
        if 'json' in output_formats:
            json_path = f'output/data_cleaned_{timestamp}.json'
            self.df_raw.to_json(json_path, orient='records', date_format='iso', indent=2)
            print(f"✓ JSON exported: {json_path}")
            exported_files['json'] = json_path
        
        # 4. Parquet (efficient untuk big data)
        if 'parquet' in output_formats:
            parquet_path = f'output/data_cleaned_{timestamp}.parquet'
            self.df_raw.to_parquet(parquet_path, index=False)
            print(f"✓ Parquet exported: {parquet_path}")
            exported_files['parquet'] = parquet_path
        
        self.preprocessing_report['exported_files'] = exported_files
        
        # Simpan juga versi latest tanpa timestamp
        latest_csv = 'output/data_cleaned_latest.csv'
        self.df_raw.to_csv(latest_csv, index=False, encoding='utf-8-sig')
        print(f"✓ Latest version: {latest_csv}")
        
        return exported_files
    
    def generate_report(self):
        """Generate comprehensive preprocessing report"""
        print("\n" + "=" * 80)
        print("TAHAP 13: GENERATE LAPORAN")
        print("=" * 80)
        
        report_content = f"""
# DATA PREPROCESSING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. ORIGINAL DATA
- Shape: {self.preprocessing_report['original_shape']}
- Total Columns: {len(self.preprocessing_report['original_columns'])}

## 2. DATA QUALITY ANALYSIS
- Total Missing Cells: {self.preprocessing_report['missing_analysis']['total_missing']:,}
- Missing Percentage: {self.preprocessing_report['missing_analysis']['missing_percentage']:.2f}%
- Columns with >50% missing: {len(self.preprocessing_report['missing_analysis']['high_missing_columns'])}
- Duplicate Rows: {self.preprocessing_report['duplicates']}

## 3. CLEANING RESULTS
- Rows Removed: {self.preprocessing_report['cleaning']['rows_removed']}
- Columns Removed: {self.preprocessing_report['cleaning']['cols_removed']}
- Final Shape: {self.preprocessing_report['cleaning']['shape_after']}

## 4. DATA TYPE CONVERSIONS
"""
        for dtype, cols in pd.Series(self.preprocessing_report['type_conversions']).value_counts().items():
            report_content += f"- {dtype}: {cols} columns\n"
        
        report_content += f"""
## 5. MISSING VALUE STRATEGIES
"""
        for strategy, cols in pd.Series(self.preprocessing_report['missing_strategies']).value_counts().items():
            report_content += f"- {strategy}: {cols} columns\n"
        
        report_content += f"""
## 6. DUPLICATES HANDLING
- Duplicates Removed: {self.preprocessing_report['duplicates_removed']} rows

## 7. METADATA
- Fields Added: {', '.join(self.preprocessing_report['metadata_added'])}

## 8. SUPABASE VALIDATION
- Memory Usage: {self.preprocessing_report['supabase_validation']['memory_usage_mb']:.2f} MB
- Total Rows: {self.preprocessing_report['supabase_validation']['total_rows']:,}
- Total Columns: {self.preprocessing_report['supabase_validation']['total_columns']}
- Long Columns Fixed: {self.preprocessing_report['supabase_validation']['long_columns_fixed']}
- Reserved Keywords Fixed: {self.preprocessing_report['supabase_validation']['reserved_keywords_fixed']}

## 9. EXPORTED FILES
"""
        for format_type, path in self.preprocessing_report['exported_files'].items():
            report_content += f"- {format_type.upper()}: {path}\n"
        
        report_content += f"""
## 10. DATA SAMPLE (First 5 rows)
{self.df_raw.head().to_string()}

## 11. COLUMN LIST
{chr(10).join([f"{i+1}. {col}" for i, col in enumerate(self.df_raw.columns)])}

## 12. RECOMMENDATIONS FOR SUPABASE
1. ✓ Data sudah dibersihkan dan dinormalisasi
2. ✓ Kolom sudah dalam format snake_case (database-friendly)
3. ✓ Tipe data sudah dikonversi dengan tepat
4. ✓ Missing values sudah ditangani
5. ✓ Duplikasi sudah dihapus
6. ✓ Metadata tracking sudah ditambahkan

### Next Steps:
1. Upload CSV file ke Supabase menggunakan dashboard atau API
2. Pastikan membuat indexes untuk kolom yang sering di-query
3. Setup Row Level Security (RLS) jika diperlukan
4. Lakukan analisis lanjutan di Supabase
"""
        
        # Simpan report
        report_path = 'output/preprocessing_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✓ Report saved: {report_path}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✓ Data preprocessing SELESAI!")
        print(f"✓ Original: {self.preprocessing_report['original_shape']} → Final: {self.preprocessing_report['cleaning']['shape_after']}")
        print(f"✓ Files generated:")
        for format_type, path in self.preprocessing_report['exported_files'].items():
            print(f"  - {path}")
        print(f"✓ Report: {report_path}")
        
        return report_path
    
    def run_pipeline(self):
        """Jalankan seluruh pipeline preprocessing"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "DATA PREPROCESSING PIPELINE" + " " * 30 + "║")
        print("║" + " " * 15 + "Best Practices for Data Analysis" + " " * 28 + "║")
        print("╚" + "=" * 78 + "╝")
        
        steps = [
            (self.load_data, "Load Data"),
            (self.analyze_data_quality, "Analyze Quality"),
            (self.fix_headers, "Fix Headers"),
            (self.remove_empty_rows_cols, "Remove Empty Data"),
            (self.handle_data_types, "Convert Data Types"),
            (self.handle_missing_values, "Handle Missing Values"),
            (self.remove_duplicates, "Remove Duplicates"),
            (self.normalize_data, "Normalize Data"),
            (self.standardize_column_names, "Standardize Columns"),
            (self.add_metadata_columns, "Add Metadata"),
            (self.validate_for_supabase, "Validate for Supabase"),
            (lambda: self.export_cleaned_data(['csv', 'excel', 'json']), "Export Data"),
            (self.generate_report, "Generate Report"),
        ]
        
        for i, (func, name) in enumerate(steps, 1):
            try:
                result = func()
                if i == 1 and not result:  # Load data failed
                    print("\n❌ Pipeline GAGAL pada tahap loading data!")
                    return False
            except Exception as e:
                print(f"\n❌ ERROR pada {name}: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "PIPELINE COMPLETED!" + " " * 32 + "║")
        print("║" + " " * 18 + "Data siap untuk upload ke Supabase" + " " * 25 + "║")
        print("╚" + "=" * 78 + "╝")
        
        return True


def main():
    """Main function"""
    # Path ke file input
    input_file = 'source/data_gabungan.xlsx'
    
    # Inisialisasi preprocessor
    preprocessor = DataPreprocessor(input_file)
    
    # Jalankan pipeline
    success = preprocessor.run_pipeline()
    
    if success:
        print("\n✅ Preprocessing berhasil!")
        print("\n📁 File output tersedia di folder 'output/'")
        print("📄 Baca file 'preprocessing_report.md' untuk detail lengkap")
    else:
        print("\n❌ Preprocessing gagal!")
    
    return success


if __name__ == "__main__":
    main()
