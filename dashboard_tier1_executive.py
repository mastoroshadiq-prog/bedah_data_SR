"""
TIER 1: EXECUTIVE DASHBOARD - SHAREHOLDER INSIGHTS
====================================================
Interactive Python Dashboard using Streamlit
11,000 Ha Palm Oil Plantation Analytics

Run: streamlit run dashboard_tier1_executive.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from dotenv import load_dotenv
import os
import numpy as np

# Page config
st.set_page_config(
    page_title="PT SR - Executive Dashboard",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment
load_dotenv()

# Initialize Supabase connection
@st.cache_resource
def init_supabase():
    return create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

supabase = init_supabase()

# Load data with caching
@st.cache_data(ttl=60)  # Cache for 1 minute only
def load_production_data():
    """Load production annual data - ALL RECORDS using pagination"""
    # Supabase limit() is capped at 1000! Need to use range() for more
    # Load in chunks and combine
    all_data = []
    page_size = 1000
    page = 0
    
    while True:
        start = page * page_size
        end = start + page_size - 1
        response = supabase.table('production_annual').select('*').range(start, end).execute()
        
        if not response.data:
            break
            
        all_data.extend(response.data)
        
        if len(response.data) < page_size:
            break
            
        page += 1
    
    return pd.DataFrame(all_data)

@st.cache_data(ttl=60)
def load_blocks_data():
    """Load blocks master data"""
    response = supabase.table('blocks').select('*').execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=60)
def load_estates_data():
    """Load estates data"""
    response = supabase.table('estates').select('*').execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=60)
def load_infrastructure_data():
    """Load infrastructure data"""
    response = supabase.table('block_land_infrastructure').select('*').execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=60)
def load_ganoderma_data():
    """Load ganoderma/pest disease data"""
    all_data = []
    page_size = 1000
    page = 0
    
    while True:
        start = page * page_size
        end = start + page_size - 1
        response = supabase.table('block_pest_disease').select('*').range(start, end).execute()
        
        if not response.data:
            break
            
        all_data.extend(response.data)
        
        if len(response.data) < page_size:
            break
            
        page += 1
    
    return pd.DataFrame(all_data)

# Load all data
df_prod = load_production_data()
df_blocks = load_blocks_data()
df_estates = load_estates_data()
df_infra = load_infrastructure_data()
df_gano = load_ganoderma_data()  # Load ganoderma data

# DEBUG: Show what years we actually loaded
st.sidebar.markdown("---")
st.sidebar.markdown("**🔍 Data Loaded:**")
years_loaded = sorted(df_prod['year'].unique())
st.sidebar.write(f"Years: {years_loaded}")
st.sidebar.write(f"Total records: {len(df_prod)}")

# Add clear cache button
if st.sidebar.button("🔄 Clear Cache & Reload"):
    st.cache_data.clear()
    st.rerun()

# Merge for complete view - rename columns to avoid conflicts
df = df_prod.merge(
    df_blocks[['id', 'block_code', 'category']].rename(columns={'id': 'blocks_id'}), 
    left_on='block_id', 
    right_on='blocks_id', 
    how='left',
    suffixes=('_prod', '_block')
)

df = df.merge(df_infra[['block_id', 'total_luas_sd_2025_ha']], 
              on='block_id', how='left')

# Use block_code from production_annual (block_code_prod) or blocks table (block_code_block)
# Prioritize block_code_block as it's from master table
df['block_code_final'] = df['block_code_block'].fillna(df.get('block_code_prod', df['block_code_block']))

# Extract estate code from block_code (first letter)
df['estate_code'] = df['block_code_final'].str[0]
estate_map = {'A': 'AME', 'O': 'OLE', 'D': 'DBE', 'B': 'AME', 'E': 'AME', 
              'F': 'AME', 'K': 'OLE', 'L': 'OLE', 'M': 'DBE', 'N': 'DBE'}
df['estate'] = df['estate_code'].map(estate_map)

# Rename for clarity in later use
df['block_code'] = df['block_code_final']

# ============================================================================
# HEADER
# ============================================================================
st.title("🌴 PT SR - Executive Dashboard")
st.markdown("### 11,000 Ha Palm Oil Plantation Performance Analytics")
st.markdown("---")

# ============================================================================
# SIDEBAR - CONFIGURATION & FILTERS
# ============================================================================
st.sidebar.header("⚙️ Configuration")

# TBS Price Slider (in Kg)
st.sidebar.markdown("**💰 TBS Price (Rp/Kg)**")
st.sidebar.caption("Adjust to see impact on opportunity loss calculation")

tbs_price_kg = st.sidebar.slider(
    "Price",
    min_value=1_000,
    max_value=5_000,
    value=2_500,
    step=100,
    format="Rp %d",
    label_visibility="collapsed"
)

# Convert to price per ton for calculation (1 Ton = 1000 Kg)
cpo_price = tbs_price_kg * 1000

st.sidebar.info(f"""
**Current TBS Price:**  
Rp {tbs_price_kg:,}/Kg  
(Rp {cpo_price:,}/Ton)

**Formula:**  
Loss = Gap (Ton) × Price (Rp/Ton)
""")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

# Year filter with "All Years" option
years = sorted(df['year'].unique())
year_options = ['All Years'] + years
selected_year = st.sidebar.selectbox(
    "Select Year",
    year_options,
    index=0  # Default to "All Years"
)

# Estate filter
estates = ['All'] + sorted(df['estate'].dropna().unique().tolist())
selected_estate = st.sidebar.selectbox("Select Estate", estates)

# Filter data based on selection
if selected_year == 'All Years':
    df_filtered = df.copy()
    year_label = f"{min(years_loaded)}-{max(years_loaded)} (All Data)"
else:
    df_filtered = df[df['year'] == selected_year].copy()
    year_label = str(selected_year)

if selected_estate != 'All':
    df_filtered = df_filtered[df_filtered['estate'] == selected_estate]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data Coverage:**")
st.sidebar.metric("Total Blocks", df_filtered['block_id'].nunique())
st.sidebar.metric("Total Records", len(df_filtered))
st.sidebar.metric("Year", year_label)
st.sidebar.metric("Estate", selected_estate)

# Add data availability info
st.sidebar.markdown("---")
years_info = "\n".join([f"- {year}: {len(df[df['year']==year])} records" for year in years_loaded])
st.sidebar.info(f"""
**Available Data:**
{years_info}
""")

# ============================================================================
# HERO METRICS (Top KPIs)
# ============================================================================
period_display = year_label if selected_year == 'All Years' else f"Year {selected_year}"
st.header(f"📊 Portfolio Performance - {period_display}")

# Calculate metrics
total_area = df_filtered['total_luas_sd_2025_ha'].sum()
total_production_actual = df_filtered['real_ton'].sum()
total_production_target = df_filtered['potensi_ton'].sum()
total_gap = total_production_actual - total_production_target
achievement_pct = (total_production_actual / total_production_target * 100) if total_production_target > 0 else 0

# Count risk blocks
critical_blocks = len(df_filtered[df_filtered['gap_pct_ton'] < -20])
high_risk_blocks = len(df_filtered[(df_filtered['gap_pct_ton'] >= -20) & (df_filtered['gap_pct_ton'] < -10)])
total_risk_blocks = critical_blocks + high_risk_blocks

# Calculate opportunity loss using dynamic TBS price
opportunity_loss = abs(total_gap) * cpo_price if total_gap < 0 else 0

# ============================================================================
# BIG HERO METRIC - TOTAL LOSS (When viewing All data)
# ============================================================================
if selected_year == 'All Years' and selected_estate == 'All':
    st.markdown("---")
    
    # Calculate yearly breakdown
    yearly_loss = []
    for year in sorted(years_loaded):
        df_year = df[df['year'] == year]
        if selected_estate != 'All':
            df_year = df_year[df_year['estate'] == selected_estate]
        
        year_gap = df_year['gap_ton'].sum()
        year_loss = abs(year_gap) * cpo_price if year_gap < 0 else 0
        yearly_loss.append({
            'year': year,
            'gap_ton': year_gap,
            'loss_billion': year_loss / 1_000_000_000
        })
    
    
    # COMBINED LAYOUT: Pie Chart (Left) | Total Loss (Right)
    col_pie, col_total = st.columns([1, 1])
    
    with col_pie:
        # PIE CHART - Yearly Breakdown
        fig_pie = go.Figure(data=[go.Pie(
            labels=[str(item['year']) for item in yearly_loss],
            values=[item['loss_billion'] for item in yearly_loss],
            hole=0.5,
            marker=dict(
                colors=['#dc2626', '#ea580c', '#f59e0b'],
                line=dict(color='#1f2937', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=15, color='white', family='Arial Black'),
            hovertemplate="<b>%{label}</b><br>" +
                         "Loss: Rp %{value:.2f} Milyar<br>" +
                         "<extra></extra>"
        )])
        
        fig_pie.update_layout(
            showlegend=False,
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(
                text=f'<b>Total</b><br>Rp {opportunity_loss/1_000_000_000:.1f}M',
                x=0.5, y=0.5,
                font=dict(size=18, color='#e5e7eb'),
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_total:
        # TOTAL LOSS DISPLAY
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); 
                    padding: 40px 30px; border-radius: 12px; text-align: center; 
                    box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4); height: 380px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <p style='color: #fecaca; font-size: 1.2em; margin: 0 0 15px 0; font-weight: 600;'>
                Total Opportunity Loss (2023-2025)
            </p>
            <h1 style='color: white; font-size: 3.5em; margin: 0; font-weight: 700;'>
                Rp {opportunity_loss/1_000_000_000:.2f} Milyar
            </h1>
            <hr style='border-color: rgba(255,255,255,0.3); margin: 25px 0;'>
            <p style='color: white; font-size: 1.1em; margin: 0;'>
                {abs(total_gap):,.0f} Ton × Rp {tbs_price_kg:,}/Kg
            </p>
            <p style='color: #fecaca; font-size: 1.3em; margin-top: 12px; font-weight: 600;'>
                ({(total_gap/total_production_target*100):.1f}% below target)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # YEAR SELECTOR BUTTONS
    st.markdown("**👆 Click year to see estate breakdown:**")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 2])
    
    # Initialize session state for selected year
    if 'selected_detail_year' not in st.session_state:
        st.session_state.selected_detail_year = None
    
    with col_btn1:
        if st.button("📊 2023", use_container_width=True):
            st.session_state.selected_detail_year = 2023
    
    with col_btn2:
        if st.button("📊 2024", use_container_width=True):
            st.session_state.selected_detail_year = 2024
    
    with col_btn3:
        if st.button("📊 2025", use_container_width=True):
            st.session_state.selected_detail_year = 2025
    
    with col_btn4:
        if st.button("❌ Clear Selection", use_container_width=True):
            st.session_state.selected_detail_year = None
    
    # ESTATE BREAKDOWN EXPANDER (NO DIALOG - USING EXPANDER FOR RELIABILITY)
    if st.session_state.selected_detail_year is not None:
        selected_yr = st.session_state.selected_detail_year
        
        with st.expander(f"📍 **Estate Breakdown for Year {selected_yr}**", expanded=True):
            # Calculate estate breakdown for selected year
            df_selected_year = df[df['year'] == selected_yr]
            
            estate_breakdown = []
            estate_colors = {
                'AME': '#dc2626',
                'OLE': '#ea580c', 
                'DBE': '#f59e0b'
            }
            
            for estate_code in ['AME', 'OLE', 'DBE']:
                df_estate = df_selected_year[df_selected_year['estate'] == estate_code]
                
                if len(df_estate) > 0:
                    estate_gap = df_estate['gap_ton'].sum()
                    estate_loss = abs(estate_gap) * cpo_price if estate_gap < 0 else 0
                    estate_blocks = len(df_estate)
                    estate_gap_pct = df_estate['gap_pct_ton'].mean()  # Use gap_pct_ton
                    
                    estate_breakdown.append({
                        'estate': estate_code,
                        'loss': estate_loss / 1_000_000_000,  # Convert to Milyar (billions)
                        'blocks': estate_blocks,
                        'gap_pct': estate_gap_pct,  # Percentage gap
                        'gap_ton': abs(estate_gap),  # Absolute gap in tons
                        'color': estate_colors[estate_code]
                    })
            
            # Sort by loss descending
            estate_breakdown = sorted(estate_breakdown, key=lambda x: x['loss'], reverse=True)
            
            # BAR CHART - Estate Loss Comparison
            st.markdown(f"### Estate Loss Breakdown - Year {selected_yr}")
            
            fig_estate = go.Figure()
            
            for item in estate_breakdown:
                fig_estate.add_trace(go.Bar(
                    y=[item['estate']],
                    x=[item['loss']],
                    orientation='h',
                    name=item['estate'],
                    text=[f"Rp {item['loss']:.1f} M"],
                    textposition='auto',
                    marker=dict(
                        color=item['color'],
                        line=dict(color='rgba(255,255,255,0.5)', width=2)
                    ),
                    hovertemplate='<b>%{y}</b><br>Loss: Rp %{x:.2f}M<extra></extra>'
                ))
            
            fig_estate.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=14),
                xaxis=dict(
                    title="Loss (Rp Milyar = Billion)",
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True
                ),
                yaxis=dict(
                    title="",
                    showgrid=False
                ),
                height=250,
                margin=dict(l=80, r=20, t=20, b=60)
            )
            
            st.plotly_chart(fig_estate, use_container_width=True)
            
            # DETAILED METRICS - 3 cards
            st.markdown("---")
            st.markdown("### 📊 Detailed Metrics")
            
            cols = st.columns(3)
            for idx, item in enumerate(estate_breakdown):
                with cols[idx]:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
                                padding: 20px; border-radius: 10px; border-left: 4px solid {item['color']};
                                box-shadow: 0 4px 10px rgba(0,0,0,0.3);'>
                        <h3 style='color: {item['color']}; margin: 0 0 15px 0; text-align: center; font-size: 1.5em;'>{item['estate']}</h3>
                        <p style='color: white; font-size: 1.8em; font-weight: 700; margin: 0; text-align: center;'>
                            Rp {item['loss']:.1f} M
                        </p>
                        <p style='color: #9ca3af; font-size: 0.85em; text-align: center; margin: 5px 0 15px 0;'>
                            (Milyar Rupiah)
                        </p>
                        <hr style='border-color: rgba(255,255,255,0.2); margin: 15px 0;'>
                        <p style='color: #e5e7eb; font-size: 0.95em; margin: 5px 0;' 
                           title='Number of plantation blocks in this estate'>
                            📦 <b>Total Blocks:</b> {item['blocks']}
                        </p>
                        <p style='color: #e5e7eb; font-size: 0.95em; margin: 5px 0;' 
                           title='Average production gap percentage per block. Negative means underperformance vs target. Formula: ((Actual - Target) / Target) × 100'>
                            📉 <b>Avg Gap %:</b> {item['gap_pct']:.1f}%
                        </p>
                        <p style='color: #fbbf24; font-size: 0.95em; margin: 5px 0;' 
                           title='Total production shortfall in tons (sum of all blocks). This is the actual tonnage difference between target and actual production.'>
                            ⚠️ <b>Production Shortfall:</b> {item['gap_ton']:,.0f} Ton
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # GANODERMA SECTION - Only for 2025
            if selected_yr == 2025:
                st.markdown("---")
                st.markdown("### 🦠 Ganoderma Attack Rate")
                st.markdown("<p style='color: #9ca3af; font-size: 0.9em;'>📊 Based on 2025 field survey data</p>", unsafe_allow_html=True)
                
                # Calculate ganoderma per estate for 2025
                gano_estate_cards = []
                for estate_code in ['AME', 'OLE', 'DBE']:
                    df_estate_blocks = df_selected_year[df_selected_year['estate'] == estate_code]
                    block_ids = df_estate_blocks['block_id'].unique()
                    df_gano_estate = df_gano[df_gano['block_id'].isin(block_ids)]
                    
                    if len(df_gano_estate) > 0:
                        avg_gano = df_gano_estate['pct_serangan'].mean() * 100
                    else:
                        avg_gano = 0
                    
                    gano_estate_cards.append({
                        'estate': estate_code,
                        'rate': avg_gano,
                        'color': estate_colors[estate_code]
                    })
                
                col_g1, col_g2, col_g3 = st.columns(3)
                for idx, gano_item in enumerate(gano_estate_cards):
                    with [col_g1, col_g2, col_g3][idx]:
                        st.metric(
                            gano_item['estate'],
                            f"{gano_item['rate']:.1f}%",
                            delta="Attack Rate",
                            delta_color="off"
                        )
    
    
    # GANODERMA ATTACK RATE SECTION - Per Estate (Foundation for Division/Block Drilldown)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🦠 Ganoderma Attack Rate by Estate")
    st.markdown("<p style='color: #9ca3af; font-size: 0.9em;'>📊 Data from 2025 field survey | Click estate for division breakdown (coming soon)</p>", unsafe_allow_html=True)
    
    # Calculate ganoderma % per estate
    gano_by_estate = {}
    gano_blocks_count = {}
    
    for estate_code in ['AME', 'OLE', 'DBE']:
        # Get blocks for this estate from main dataframe
        df_estate_blocks = df[df['estate'] == estate_code]
        block_ids = df_estate_blocks['block_id'].unique()
        
        # Get ganoderma data for these blocks
        df_gano_estate = df_gano[df_gano['block_id'].isin(block_ids)]
        
        if len(df_gano_estate) > 0:
            avg_gano_pct = df_gano_estate['pct_serangan'].mean() * 100
            gano_by_estate[estate_code] = avg_gano_pct
            gano_blocks_count[estate_code] = len(df_gano_estate)
        else:
            gano_by_estate[estate_code] = 0
            gano_blocks_count[estate_code] = 0
    
    # Display as 3 columns with gradient cards
    col_ame, col_ole, col_dbe = st.columns(3)
    
    estate_info = {
        'AME': {'color': '#dc2626', 'col': col_ame},
        'OLE': {'color': '#ea580c', 'col': col_ole},
        'DBE': {'color': '#f59e0b', 'col': col_dbe}
    }
    
    for estate_code, info in estate_info.items():
        with info['col']:
            attack_rate = gano_by_estate[estate_code]
            blocks_surveyed = gano_blocks_count[estate_code]
            
            # Determine severity level
            if attack_rate >= 15:
                severity = "CRITICAL"
                severity_icon = "🔴"
            elif attack_rate >= 10:
                severity = "HIGH"
                severity_icon = "🟠"
            elif attack_rate >= 5:
                severity = "MEDIUM"
                severity_icon = "🟡"
            else:
                severity = "LOW"
                severity_icon = "🟢"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {info['color']} 0%, rgba(0,0,0,0.3) 100%); 
                        padding: 25px 20px; border-radius: 10px; text-align: center;
                        border: 2px solid {info['color']}; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                        cursor: pointer; transition: transform 0.2s;'
                 onmouseover='this.style.transform="scale(1.02)"' 
                 onmouseout='this.style.transform="scale(1)"'>
                <h3 style='color: white; margin: 0 0 10px 0; font-size: 1.8em;'>{estate_code}</h3>
                <p style='color: {info['color']}; font-size: 3em; font-weight: 700; margin: 10px 0;'>
                    {attack_rate:.1f}%
                </p>
                <p style='color: #e5e7eb; font-size: 1em; margin: 5px 0;'>
                    {severity_icon} {severity} Risk
                </p>
                <hr style='border-color: rgba(255,255,255,0.2); margin: 15px 0;'>
                <p style='color: #d1d5db; font-size: 0.9em; margin: 0;'>
                    📍 {blocks_surveyed} blocks surveyed
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # ESTATE BREAKDOWN - Show when year is selected
    if st.session_state.selected_detail_year is not None:
        selected_yr = st.session_state.selected_detail_year
        
        st.markdown("---")
        st.markdown(f"### 📍 Estate Breakdown for Year {selected_yr}")
        
        # Calculate estate breakdown for selected year
        df_selected_year = df[df['year'] == selected_yr]
        
        estate_breakdown = []
        for estate_code in ['AME', 'OLE', 'DBE']:
            df_estate = df_selected_year[df_selected_year['estate'] == estate_code]
            
            if len(df_estate) > 0:
                estate_gap = df_estate['gap_ton'].sum()
                estate_loss = abs(estate_gap) * cpo_price if estate_gap < 0 else 0
                estate_blocks = len(df_estate)
                
                estate_breakdown.append({
                    'estate': estate_code,
                    'gap_ton': estate_gap,
                    'loss_billion': estate_loss / 1_000_000_000,
                    'blocks': estate_blocks
                })
        
        # Display as horizontal bar chart
        if estate_breakdown:
            fig_estate = go.Figure()
            
            colors = {
                'AME': '#dc2626',  # Red
                'OLE': '#ea580c',  # Orange  
                'DBE': '#f59e0b'   # Amber
            }
            
            for item in estate_breakdown:
                fig_estate.add_trace(go.Bar(
                    y=[item['estate']],
                    x=[item['loss_billion']],
                    orientation='h',
                    name=item['estate'],
                    text=[f"Rp {item['loss_billion']:.2f} Milyar"],
                    textposition='inside',
                    textfont=dict(color='white', size=16, family='Arial Black'),
                    hovertemplate=f"<b>{item['estate']}</b><br>" +
                                 f"Loss: Rp {item['loss_billion']:.2f} Milyar<br>" +
                                 f"Gap: {item['gap_ton']:,.0f} Ton<br>" +
                                 f"Blocks: {item['blocks']}<br>" +
                                 "<extra></extra>",
                    marker=dict(
                        color=colors[item['estate']],
                        line=dict(color='white', width=2)
                    )
                ))
            
            fig_estate.update_layout(
                title=f"Estate Loss Breakdown - Year {selected_yr}",
                showlegend=False,
                height=250,
                margin=dict(l=80, r=20, t=50, b=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title="Loss (Rp Milyar)",
                    gridcolor='rgba(128,128,128,0.2)',
                    color='#e5e7eb'
                ),
                yaxis=dict(
                    title="",
                    color='#e5e7eb',
                    tickfont=dict(size=16, family='Arial Black')
                ),
                title_font=dict(size=18, color='#e5e7eb')
            )
            
            st.plotly_chart(fig_estate, use_container_width=True)
            
            # Summary cards
            col1, col2, col3 = st.columns(3)
            
            # Color palette for estates
            estate_colors = {
                'AME': '#dc2626',  # Red
                'OLE': '#ea580c',  # Orange
                'DBE': '#f59e0b'   # Amber
            }
            
            for idx, item in enumerate(estate_breakdown):
                with [col1, col2, col3][idx]:
                    # Custom styled card
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                                padding: 20px; border-radius: 10px; 
                                border-left: 4px solid {estate_colors[item['estate']]};
                                box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                        <h3 style='color: {estate_colors[item['estate']]}; margin: 0; font-size: 1.5em;'>
                            {item['estate']}
                        </h3>
                        <h2 style='color: white; margin: 10px 0; font-size: 2.2em; font-weight: 700;'>
                            Rp {item['loss_billion']:.2f} M
                        </h2>
                        <div style='margin-top: 15px; padding: 10px; 
                                    background: rgba(251, 146, 60, 0.15); 
                                    border-radius: 6px; border-left: 3px solid #fb923c;'>
                            <p style='color: #fb923c; margin: 0; font-size: 1.1em; font-weight: 600;'>
                                📊 Total Blocks: <span style='color: #fbbf24;'>{item['blocks']}</span>
                            </p>
                            <p style='color: #fb923c; margin: 5px 0 0 0; font-size: 1.1em; font-weight: 600;'>
                                📉 Gap Yield: <span style='color: #fbbf24;'>{item['gap_ton']:,.0f} Ton</span>
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # GANODERMA INDICATOR CARD - ONLY FOR 2025 (data available)
            if selected_yr == 2025:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Calculate ganoderma % per estate
                gano_by_estate = {}
                for estate_code in ['AME', 'OLE', 'DBE']:
                    # Get blocks for this estate
                    df_estate_blocks = df_selected_year[df_selected_year['estate'] == estate_code]
                    block_ids = df_estate_blocks['block_id'].unique()
                    
                    # Get ganoderma data for these blocks
                    df_gano_estate = df_gano[df_gano['block_id'].isin(block_ids)]
                    
                    if len(df_gano_estate) > 0:
                        avg_gano_pct = df_gano_estate['pct_serangan'].mean() * 100
                        gano_by_estate[estate_code] = avg_gano_pct
                    else:
                        gano_by_estate[estate_code] = 0
                
                # Display ganoderma card
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1f2937 0%, #111827 100%); 
                            padding: 25px; border-radius: 12px; border-left: 4px solid #fbbf24;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.3);'>
                    <h4 style='color: #fbbf24; margin-top: 0; display: flex; align-items: center;'>
                        <span style='font-size: 1.3em; margin-right: 10px;'>🦠</span>
                        Ganoderma Attack Rate (2025 Survey)
                    </h4>
                    <div style='display: flex; justify-content: space-around; margin-top: 15px;'>
                        <div style='text-align: center;'>
                            <p style='color: #dc2626; font-size: 2em; font-weight: 700; margin: 0;'>{gano_by_estate['AME']:.1f}%</p>
                            <p style='color: #9ca3af; margin: 5px 0 0 0;'>AME</p>
                        </div>
                        <div style='text-align: center;'>
                            <p style='color: #ea580c; font-size: 2em; font-weight: 700; margin: 0;'>{gano_by_estate['OLE']:.1f}%</p>
                            <p style='color: #9ca3af; margin: 5px 0 0 0;'>OLE</p>
                        </div>
                        <div style='text-align: center;'>
                            <p style='color: #f59e0b; font-size: 2em; font-weight: 700; margin: 0;'>{gano_by_estate['DBE']:.1f}%</p>
                            <p style='color: #9ca3af; margin: 5px 0 0 0;'>DBE</p>
                        </div>
                    </div>
                    <p style='color: #6b7280; font-size: 0.9em; text-align: center; margin: 15px 0 0 0;'>
                        ⚠️ Based on 2025 field survey data | Higher % indicates greater disease pressure
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show message for years without ganoderma data
                st.info(f"ℹ️ Ganoderma survey data not available for year {selected_yr}. Survey conducted in 2025 only.")
    
    st.markdown("---")

# ============================================================================
# SUPPORTING METRICS (4 columns)
# ============================================================================
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Area",
        f"{total_area:,.0f} Ha",
        delta=None
    )

with col2:
    st.metric(
        "Production Actual",
        f"{total_production_actual:,.0f} Ton",
        delta=f"{achievement_pct:.1f}% of target"
    )

with col3:
    st.metric(
        "Production Gap",
        f"{total_gap:,.0f} Ton",
        delta=f"{(total_gap/total_production_target*100):.1f}%",
        delta_color="inverse"
    )

with col4:
    st.metric(
        "Risk Exposure",
        f"{total_risk_blocks} Blocks",
        delta=f"{(total_risk_blocks/len(df_filtered)*100):.1f}% of portfolio",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================================================
# SECTION 1: PRODUCTION GAP WATERFALL
# ============================================================================
st.header("💧 Production Gap Analysis - Waterfall")

# Calculate by estate
gap_by_estate = df_filtered.groupby('estate').agg({
    'real_ton': 'sum',
    'potensi_ton': 'sum'
}).reset_index()
gap_by_estate['gap'] = gap_by_estate['real_ton'] - gap_by_estate['potensi_ton']

# Create waterfall data
waterfall_data = []
waterfall_data.append({
    'label': 'Target',
    'value': total_production_target,
    'type': 'total'
})

for _, row in gap_by_estate.iterrows():
    waterfall_data.append({
        'label': f"{row['estate']} Gap",
        'value': row['gap'],
        'type': 'relative'
    })

waterfall_data.append({
    'label': 'Actual Achievement',
    'value': total_production_actual,
    'type': 'total'
})

# Create waterfall chart
fig_waterfall = go.Figure(go.Waterfall(
    name="Production",
    orientation="v",
    measure=[d['type'] for d in waterfall_data],
    x=[d['label'] for d in waterfall_data],
    y=[d['value'] for d in waterfall_data],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#EF4444"}},
    increasing={"marker": {"color": "#10B981"}},
    totals={"marker": {"color": "#3B82F6"}}
))

fig_waterfall.update_layout(
    title=f"Where Are We Losing Production? ({year_label})",
    showlegend=False,
    height=400
)

st.plotly_chart(fig_waterfall, use_container_width=True)

# ============================================================================
# SECTION 2: ESTATE PERFORMANCE HEATMAP
# ============================================================================
st.header("🔥 Estate Performance Heatmap (2023-2025)")

# Calculate achievement % by estate and year
heatmap_data = df.groupby(['estate', 'year']).agg({
    'real_ton': 'sum',
    'potensi_ton': 'sum'
}).reset_index()
heatmap_data['achievement_pct'] = (heatmap_data['real_ton'] / heatmap_data['potensi_ton'] * 100).round(1)

# Pivot for heatmap
heatmap_pivot = heatmap_data.pivot(index='estate', columns='year', values='achievement_pct')

# Create heatmap
fig_heatmap = px.imshow(
    heatmap_pivot,
    labels=dict(x="Year", y="Estate", color="Achievement %"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale='RdYlGn',
    color_continuous_midpoint=100,
    text_auto='.1f'
)

fig_heatmap.update_layout(
    title="Estate Performance Trends - Are We Improving?",
    height=300
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ============================================================================
# SECTION 3: RISK DISTRIBUTION
# ============================================================================
st.header("⚠️ Risk Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    # Risk categorization
    def categorize_risk(gap_pct):
        if pd.isna(gap_pct):
            return 'Unknown'
        elif gap_pct < -20:
            return '🔴 Critical (< -20%)'
        elif gap_pct < -10:
            return '🟠 High (-10% to -20%)'
        elif gap_pct < 0:
            return '🟡 Medium (0% to -10%)'
        else:
            return '🟢 On Target (≥ 0%)'
    
    df_filtered['risk_category'] = df_filtered['gap_pct_ton'].apply(categorize_risk)
    
    # Count by risk
    risk_counts = df_filtered['risk_category'].value_counts().reset_index()
    risk_counts.columns = ['Risk Category', 'Count']
    
    # Pie chart
    fig_pie = px.pie(
        risk_counts,
        values='Count',
        names='Risk Category',
        title=f'Block Risk Distribution ({year_label})',
        color='Risk Category',
        color_discrete_map={
            '🔴 Critical (< -20%)': '#EF4444',
            '🟠 High (-10% to -20%)': '#F97316',
            '🟡 Medium (0% to -10%)': '#EAB308',
            '🟢 On Target (≥ 0%)': '#10B981'
        }
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Financial impact
    st.subheader("💰 Financial Impact Estimate")
    
    # Assume CPO price (Crude Palm Oil)
    cpo_price = st.number_input(
        "CPO Price (Rp/Ton)",
        value=2_500_000,
        step=100_000,
        format="%d"
    )
    
    # Calculate opportunity loss
    opportunity_loss = abs(total_gap) * cpo_price if total_gap < 0 else 0
    
    st.metric(
        "Opportunity Loss from Gap",
        f"Rp {opportunity_loss/1_000_000_000:.2f} Milyar",
        delta=f"{abs(total_gap):,.0f} Ton unrealized"
    )
    
    st.markdown(f"""
    **Breakdown:**
    - Production Gap: {total_gap:,.0f} Ton
    - CPO Price: Rp {cpo_price:,}/Ton
    - **Lost Revenue:** Rp {opportunity_loss:,.0f}
    
    *This represents unrealized revenue if we achieved 100% of target.*
    """)

st.markdown("---")

# ============================================================================
# SECTION 4: TOP & BOTTOM PERFORMERS
# ============================================================================
st.header("🏆 Top & Bottom Performers")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Top 10 Best Performers")
    top_10 = df_filtered.nlargest(10, 'gap_pct_ton')[
        ['block_code', 'estate', 'real_ton', 'gap_pct_ton']
    ].copy()
    top_10.columns = ['Block', 'Estate', 'Production (Ton)', 'Gap %']
    top_10['Gap %'] = top_10['Gap %'].round(1)
    top_10['Production (Ton)'] = top_10['Production (Ton)'].round(0)
    st.dataframe(top_10, hide_index=True, use_container_width=True)

with col2:
    st.subheader("❌ Bottom 10 Worst Performers")
    bottom_10 = df_filtered.nsmallest(10, 'gap_pct_ton')[
        ['block_code', 'estate', 'real_ton', 'gap_pct_ton']
    ].copy()
    bottom_10.columns = ['Block', 'Estate', 'Production (Ton)', 'Gap %']
    bottom_10['Gap %'] = bottom_10['Gap %'].round(1)
    bottom_10['Production (Ton)'] = bottom_10['Production (Ton)'].round(0)
    
    # Highlight critical
    def highlight_critical(val):
        if isinstance(val, (int, float)) and val < -20:
            return 'background-color: #FEE2E2; color: #991B1B'
        return ''
    
    st.dataframe(
        bottom_10.style.applymap(highlight_critical, subset=['Gap %']),
        hide_index=True,
        use_container_width=True
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(f"""
**Dashboard Info:**
- Data Source: Supabase Production Database
- Last Updated: Real-time
- Total Records Analyzed: {len(df_filtered):,}
- Coverage: {selected_year} | {selected_estate}
""")

st.markdown("*Built with Streamlit + Python | © 2026 PT SR Analytics*")
