"""
Streamlit Dashboard for Normalized Data
Interactive visualization with performance monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Page config
st.set_page_config(
    page_title="Palm Oil Data Dashboard",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .performance-good {
        color: #10B981;
        font-weight: bold;
    }
    .performance-warning {
        color: #F59E0B;
        font-weight: bold;
    }
    .performance-bad {
        color: #EF4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("⚠️ Supabase credentials not found! Please check .env file")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor query performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        # Store performance data in session state
        if 'performance_log' not in st.session_state:
            st.session_state.performance_log = []
        
        st.session_state.performance_log.append({
            'function': func.__name__,
            'time_ms': elapsed
        })
        
        return result, elapsed
    return wrapper

# Data loading functions with caching and performance monitoring
@st.cache_data(ttl=600)
@monitor_performance
def load_estates():
    """Load estates data"""
    response = supabase.table('estates').select('*').execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=600)
@monitor_performance
def load_blocks(estate_filter=None):
    """Load blocks data with optional estate filter"""
    query = supabase.table('blocks').select('*')
    
    if estate_filter and estate_filter != 'All':
        query = query.eq('estate_code', estate_filter)
    
    response = query.execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=600)
@monitor_performance
def load_production_data(block_codes=None):
    """Load production data"""
    query = supabase.table('production_data').select('block_code, id')
    
    if block_codes:
        query = query.in_('block_code', block_codes[:100])  # Limit to prevent huge queries
    
    response = query.execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=600)
@monitor_performance
def load_estate_summary():
    """Load pre-computed estate summary from materialized view"""
    try:
        response = supabase.table('mv_estate_summary').select('*').execute()
        return pd.DataFrame(response.data)
    except:
        # Fallback to direct query if materialized view not available
        return compute_estate_summary()

def compute_estate_summary():
    """Compute estate summary (fallback)"""
    blocks_df, _ = load_blocks()
    
    summary = blocks_df.groupby('estate_code').agg({
        'block_code': 'count',
        'area_ha': ['sum', 'mean']
    }).reset_index()
    
    summary.columns = ['estate_code', 'total_blocks', 'total_area_ha', 'avg_area_ha']
    return summary

# ============================================================================
# DASHBOARD LAYOUT
# ============================================================================

# Header
st.markdown('<div class="main-header">🌴 Palm Oil Estate Dashboard</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    # Estate filter
    st.subheader("Filters")
    estates_df, perf1 = load_estates()
    estate_options = ['All'] + sorted(estates_df['estate_code'].unique().tolist())
    selected_estate = st.selectbox("Select Estate", estate_options)
    
    # Year filter
    blocks_df, perf2 = load_blocks(selected_estate if selected_estate != 'All' else None)
    if not blocks_df.empty and 'year_planted' in blocks_df.columns:
        year_range  = st.slider(
            "Year Planted Range",
            int(blocks_df['year_planted'].min()) if blocks_df['year_planted'].notna().any() else 2000,
            int(blocks_df['year_planted'].max()) if blocks_df['year_planted'].notna().any() else 2025,
            (2000, 2025)
        )
    else:
        year_range = (2000, 2025)
    
    st.divider()
    
    # Performance monitor
    st.subheader("⚡ Performance Monitor")
    if 'performance_log' in st.session_state and st.session_state.performance_log:
        recent_perf = st.session_state.performance_log[-5:]
        for perf in recent_perf:
            time_ms = perf['time_ms']
            if time_ms < 50:
                status_class = "performance-good"
                status_icon = "✅"
            elif time_ms < 100:
                status_class = "performance-warning"
                status_icon = "⚠️"
            else:
                status_class = "performance-bad"
                status_icon = "❌"
            
            st.markdown(
                f"{status_icon} **{perf['function']}**: "
                f'<span class="{status_class}">{time_ms:.1f}ms</span>',
                unsafe_allow_html=True
            )
    
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.session_state.performance_log = []
        st.rerun()

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "🔍 Details", "⚡ Performance"])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    st.header("Estate Overview")
    
    # Load summary data
    summary_df, perf_summary = load_estate_summary()
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_estates = len(summary_df)
        st.metric("Total Estates", total_estates)
    
    with col2:
        total_blocks = summary_df['total_blocks'].sum() if 'total_blocks' in summary_df.columns else len(blocks_df)
        st.metric("Total Blocks", f"{int(total_blocks):,}")
    
    with col3:
        total_area = summary_df['total_area_ha'].sum() if 'total_area_ha' in summary_df.columns else blocks_df['area_ha'].sum()
        st.metric("Total Area", f"{total_area:,.1f} ha")
    
    with col4:
        avg_area = summary_df['avg_area_ha'].mean() if 'avg_area_ha' in summary_df.columns else blocks_df['area_ha'].mean()
        st.metric("Avg Block Size", f"{avg_area:.1f} ha")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Blocks by Estate")
        if 'total_blocks' in summary_df.columns:
            fig1 = px.bar(
                summary_df,
                x='estate_code',
                y='total_blocks',
                title="Number of Blocks per Estate",
                color='total_blocks',
                color_continuous_scale='Greens'
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Area Distribution")
        if 'total_area_ha' in summary_df.columns:
            fig2 = px.pie(
                summary_df,
                values='total_area_ha',
                names='estate_code',
                title="Area Distribution by Estate"
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

# ============================================================================
# TAB 2: ANALYTICS
# ============================================================================

with tab2:
    st.header("Block Analytics")
    
    # Filter blocks by year range
    if not blocks_df.empty and 'year_planted' in blocks_df.columns:
        filtered_blocks = blocks_df[
            (blocks_df['year_planted'] >= year_range[0]) &
            (blocks_df['year_planted'] <= year_range[1])
        ]
    else:
        filtered_blocks = blocks_df
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Planting Timeline")
        if not filtered_blocks.empty and 'year_planted' in filtered_blocks.columns:
            year_counts = filtered_blocks['year_planted'].value_counts().sort_index()
            fig3 = px.line(
                x=year_counts.index,
                y=year_counts.values,
                title="Blocks Planted by Year",
                labels={'x': 'Year', 'y': 'Number of Blocks'}
            )
            fig3.update_traces(mode='lines+markers')
            st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.subheader("Area Size Distribution")
        if not filtered_blocks.empty and 'area_ha' in filtered_blocks.columns:
            fig4 = px.histogram(
                filtered_blocks,
                x='area_ha',
                title="Distribution of Block Sizes",
                labels={'area_ha': 'Area (hectares)'},
                nbins=20
            )
            st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# TAB 3: DETAILS
# ============================================================================

with tab3:
    st.header("Block Details")
    
    # Display filtered data
    if not filtered_blocks.empty:
        st.subheader(f"Showing {len(filtered_blocks)} blocks")
        
        # Select columns to display
        display_cols = ['block_code', 'estate_code', 'area_ha', 'year_planted', 'number']
        available_cols = [col for col in display_cols if col in filtered_blocks.columns]
        
        st.dataframe(
            filtered_blocks[available_cols].sort_values('block_code'),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_blocks.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"blocks_{selected_estate}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No blocks found with current filters")

# ============================================================================
# TAB 4: PERFORMANCE BENCHMARK
# ============================================================================

with tab4:
    st.header("⚡ Performance Benchmark")
    
    st.markdown("""
    This tab shows real-time query performance metrics for the normalized database schema.
    All times are in milliseconds (ms).
    """)
    
    if st.button("🚀 Run Full Benchmark"):
        with st.spinner("Running benchmark tests..."):
            benchmark_results = []
            
            # Test 1: Load estates
            start = time.time()
            estates_df, _ = load_estates()
            benchmark_results.append({
                'Query': 'Load Estates',
                'Time (ms)': (time.time() - start) * 1000,
                'Rows': len(estates_df)
            })
            
            # Test 2: Load all blocks
            start = time.time()
            all_blocks, _ = load_blocks()
            benchmark_results.append({
                'Query': 'Load All Blocks',
                'Time (ms)': (time.time() - start) * 1000,
                'Rows': len(all_blocks)
            })
            
            # Test 3: Filter by estate
            start = time.time()
            estate_blocks, _ = load_blocks('AME001')
            benchmark_results.append({
                'Query': 'Filter by Estate (AME001)',
                'Time (ms)': (time.time() - start) * 1000,
                'Rows': len(estate_blocks)
            })
            
            # Test 4: Load estate summary
            start = time.time()
            summary, _ = load_estate_summary()
            benchmark_results.append({
                'Query': 'Load Estate Summary',
                'Time (ms)': (time.time() - start) * 1000,
                'Rows': len(summary)
            })
            
            # Display results
            benchmark_df = pd.DataFrame(benchmark_results)
            
            st.subheader("Benchmark Results")
            st.dataframe(benchmark_df, use_container_width=True)
            
            # Performance chart
            fig5 = px.bar(
                benchmark_df,
                x='Query',
                y='Time (ms)',
                title="Query Performance Comparison",
                color='Time (ms)',
                color_continuous_scale=['green', 'yellow', 'red']
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Performance summary
            avg_time = benchmark_df['Time (ms)'].mean()
            max_time = benchmark_df['Time (ms)'].max()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Query Time", f"{avg_time:.1f} ms")
            with col2:
                st.metric("Slowest Query", f"{max_time:.1f} ms")
            with col3:
                if avg_time < 100:
                    st.success("✅ Excellent Performance!")
                elif avg_time < 200:
                    st.warning("⚠️ Good Performance")
                else:
                    st.error("❌ Needs Optimization")
    
    # Historical performance log
    if 'performance_log' in st.session_state and st.session_state.performance_log:
        st.subheader("Query History")
        perf_df = pd.DataFrame(st.session_state.performance_log)
        
        # Group by function
        perf_summary = perf_df.groupby('function')['time_ms'].agg(['mean', 'min', 'max', 'count']).reset_index()
        perf_summary.columns = ['Function', 'Avg (ms)', 'Min (ms)', 'Max (ms)', 'Calls']
        
        st.dataframe(perf_summary, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Normalized Database Dashboard | Built with Streamlit & Supabase</p>
    <p>⚡ Powered by Optimized Schema with Indexes & Materialized Views</p>
</div>
""", unsafe_allow_html=True)
