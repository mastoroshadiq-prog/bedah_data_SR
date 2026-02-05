"""
Data Analysis Examples - Query Supabase Data
Contoh-contoh query untuk analisa data di Supabase
"""

from supabase import create_client, Client
import pandas as pd
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

TABLE_NAME = "data_gabungan"


class DataAnalyzer:
    """Class untuk analisa data dari Supabase"""
    
    def __init__(self):
        self.supabase = supabase
        self.df = None
    
    def load_all_data(self):
        """Load semua data dari Supabase ke DataFrame"""
        print("📥 Loading data from Supabase...")
        
        response = self.supabase.table(TABLE_NAME).select("*").execute()
        self.df = pd.DataFrame(response.data)
        
        print(f"✓ Loaded {len(self.df):,} rows × {len(self.df.columns)} columns")
        return self.df
    
    def basic_statistics(self):
        """Statistik dasar"""
        print("\n" + "=" * 80)
        print("BASIC STATISTICS")
        print("=" * 80)
        
        if self.df is None:
            self.load_all_data()
        
        print("\n1. Dataset Shape:")
        print(f"   Rows: {len(self.df):,}")
        print(f"   Columns: {len(self.df.columns)}")
        
        print("\n2. Data Types:")
        print(self.df.dtypes.value_counts())
        
        print("\n3. Missing Values:")
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("   No missing values! ✓")
        
        print("\n4. Numeric Columns Statistics:")
        print(self.df.describe())
    
    def query_by_category(self, column='c001', limit=10):
        """Query data berdasarkan kategori"""
        print(f"\n📊 Top {limit} by {column}:")
        
        response = (self.supabase.table(TABLE_NAME)
                   .select("*")
                   .order(column)
                   .limit(limit)
                   .execute())
        
        df_result = pd.DataFrame(response.data)
        print(df_result[[column, 'k001', 'c003', 'c004']].head())
        
        return df_result
    
    def aggregate_analysis(self, group_by='c001', agg_column='c003'):
        """Analisa agregasi"""
        print(f"\n📈 Aggregation by {group_by}:")
        
        if self.df is None:
            self.load_all_data()
        
        # Convert to numeric if needed
        if self.df[agg_column].dtype == 'object':
            self.df[agg_column] = pd.to_numeric(self.df[agg_column], errors='coerce')
        
        result = self.df.groupby(group_by)[agg_column].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).round(2)
        
        print(result)
        return result
    
    def time_series_analysis(self, date_column='created_at', metric_column='c003'):
        """Analisa time series"""
        print(f"\n📅 Time Series Analysis:")
        
        if self.df is None:
            self.load_all_data()
        
        # Convert to datetime
        self.df[date_column] = pd.to_datetime(self.df[date_column])
        
        # Group by date
        ts_data = self.df.groupby(self.df[date_column].dt.date)[metric_column].agg([
            'count', 'mean', 'sum'
        ])
        
        print(ts_data.head(10))
        return ts_data
    
    def correlation_matrix(self, columns=None):
        """Matriks korelasi"""
        print("\n🔗 Correlation Matrix:")
        
        if self.df is None:
            self.load_all_data()
        
        # Select numeric columns
        if columns is None:
            numeric_cols = self.df.select_dtypes(include=['number']).columns[:10]
        else:
            numeric_cols = columns
        
        corr_matrix = self.df[numeric_cols].corr()
        print(corr_matrix)
        
        return corr_matrix
    
    def filter_data(self, conditions):
        """Filter data dengan kondisi tertentu"""
        print(f"\n🔍 Filtering data...")
        
        query = self.supabase.table(TABLE_NAME).select("*")
        
        # Apply filters
        for column, operator, value in conditions:
            if operator == 'eq':
                query = query.eq(column, value)
            elif operator == 'gt':
                query = query.gt(column, value)
            elif operator == 'lt':
                query = query.lt(column, value)
            elif operator == 'gte':
                query = query.gte(column, value)
            elif operator == 'lte':
                query = query.lte(column, value)
        
        response = query.execute()
        df_filtered = pd.DataFrame(response.data)
        
        print(f"✓ Found {len(df_filtered):,} matching rows")
        return df_filtered
    
    def export_analysis_results(self, df, filename):
        """Export hasil analisa"""
        output_path = f'output/analysis_{filename}'
        df.to_csv(output_path, index=False)
        print(f"✓ Results exported to: {output_path}")


# ============================================================================
# EXAMPLE QUERIES
# ============================================================================

def example_basic_query():
    """Contoh query dasar"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: BASIC QUERY")
    print("=" * 80)
    
    # Get all data
    response = supabase.table(TABLE_NAME).select("*").limit(5).execute()
    df = pd.DataFrame(response.data)
    
    print("\nFirst 5 rows:")
    print(df[['id', 'k001', 'c001', 'c003', 'c004']].head())


def example_filtered_query():
    """Contoh query dengan filter"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: FILTERED QUERY")
    print("=" * 80)
    
    # Filter: c001 = 'AME' AND c003 > 20
    response = (supabase.table(TABLE_NAME)
               .select("*")
               .eq('c001', 'AME')
               .gt('c003', 20)
               .limit(10)
               .execute())
    
    df = pd.DataFrame(response.data)
    print(f"\nFound {len(df)} rows where c001='AME' and c003>20")
    print(df[['k001', 'c001', 'c003', 'c004']].head())


def example_aggregation():
    """Contoh aggregasi"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: AGGREGATION")
    print("=" * 80)
    
    # Get all data first
    response = supabase.table(TABLE_NAME).select("*").execute()
    df = pd.DataFrame(response.data)
    
    # Group by c001 and calculate statistics
    result = df.groupby('c001')['c003'].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('sum', 'sum')
    ]).round(2)
    
    print("\nStatistics by c001:")
    print(result)


def example_time_series():
    """Contoh time series"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: TIME SERIES")
    print("=" * 80)
    
    # Get data with date
    response = supabase.table(TABLE_NAME).select("created_at, c003").execute()
    df = pd.DataFrame(response.data)
    
    # Convert to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    
    # Daily aggregation
    daily_stats = df.groupby('date')['c003'].agg(['count', 'mean', 'sum'])
    
    print("\nDaily statistics:")
    print(daily_stats.head(10))


def example_complex_analysis():
    """Contoh analisa kompleks"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: COMPLEX ANALYSIS")
    print("=" * 80)
    
    analyzer = DataAnalyzer()
    
    # Load data
    analyzer.load_all_data()
    
    # 1. Basic statistics
    analyzer.basic_statistics()
    
    # 2. Aggregation by category
    analyzer.aggregate_analysis(group_by='c001', agg_column='c003')
    
    # 3. Filter example
    filtered_df = analyzer.filter_data([
        ('c001', 'eq', 'AME'),
        ('c003', 'gt', 20)
    ])
    
    print(f"\nFiltered data shape: {filtered_df.shape}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "DATA ANALYSIS EXAMPLES" + " " * 30 + "║")
    print("║" + " " * 20 + "Query & Analyze Supabase Data" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run examples
    try:
        example_basic_query()
        example_filtered_query()
        example_aggregation()
        example_time_series()
        # example_complex_analysis()  # Uncomment untuk analisa lengkap
        
        print("\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETED!")
        print("=" * 80)
        print("\nℹ️  Untuk analisa lebih lanjut:")
        print("   1. Uncomment example_complex_analysis()")
        print("   2. Modify queries sesuai kebutuhan Anda")
        print("   3. Gunakan DataAnalyzer class untuk analisa custom")
        print("")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n⚠️  Make sure:")
        print("   1. Data sudah diupload ke Supabase")
        print("   2. .env file sudah dikonfigurasi dengan benar")
        print("   3. Supabase credentials valid")


if __name__ == "__main__":
    main()
