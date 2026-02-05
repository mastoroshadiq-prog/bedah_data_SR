"""
Dashboard Updates After Database Restructure
=============================================
Changes to make:
1. Add load_divisions_data() function
2. Update Ganoderma section to use divisions table
3. Simplify division breakdown (no more messy merges!)
"""

# ADD THIS AFTER load_ganoderma_data() function (around line 107):

@st.cache_data(ttl=60)
def load_divisions_data():
    """Load divisions data with estate relationship"""
    response = supabase.table('divisions').select('*').execute()
    return pd.DataFrame(response.data)

# ADD THIS to data loading section (around line 114):
df_divisions = load_divisions_data()

# UPDATE Ganoderma section (around line 573-665) with THIS SIMPLER CODE:

# Show division breakdown if estate selected
if st.session_state.selected_gano_estate:
    sel_estate = st.session_state.selected_gano_estate
    
    # Use expander
    with st.expander(f"📊 **Division Breakdown - {sel_estate} Estate**", expanded=True):
        if st.button("❌ Close", key="close_gano"):
            st.session_state.selected_gano_estate = None
            st.rerun()
        
        # Get estate_id
        estate_id = df_estates[df_estates['estate_code'] == sel_estate]['id'].values[0]
        
        # Get divisions for this estate from divisions table (CLEAN!)
        estate_divisions = df_divisions[df_divisions['estate_id'] == estate_id]
        
        if len(estate_divisions) > 0:
            st.write(f"**{len(estate_divisions)} divisions in {sel_estate}**")
            
            # For each division, get ganoderma stats
            div_stats = []
            for _, div_row in estate_divisions.iterrows():
                # Get blocks in this division
                div_blocks = df_blocks[df_blocks['division_id'] == div_row['id']]
                block_ids = div_blocks['id'].tolist()
                
                # Get ganoderma data for these blocks
                div_gano = df_gano[df_gano['block_id'].isin(block_ids)]
                
                if len(div_gano) > 0:
                    avg_rate = div_gano['pct_serangan'].mean() * 100
                    div_stats.append({
                        'division': div_row['division_code'],
                        'attack_rate': avg_rate,
                        'block_count': len(div_gano)
                    })
            
            if div_stats:
                # Display cards
                cols_per_row = 5
                for i in range(0, len(div_stats), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(min(cols_per_row, len(div_stats) - i)):
                        row = div_stats[i + j]
                        with cols[j]:
                            rate = row['attack_rate']
                            
                            # Color coding
                            if rate >= 15:
                                color = "#dc2626"
                                label = "CRITICAL"
                            elif rate >= 10:
                                color = "#ea580c"
                                label = "HIGH"
                            elif rate >= 5:
                                color = "#f59e0b"
                                label = "MEDIUM"
                            else:
                                color = "#10b981"
                                label = "LOW"
                            
                            st.markdown(f"""
<div style="background: linear-gradient(135deg, {color} 0%, rgba(0,0,0,0.5) 100%);
            padding: 12px; border-radius: 8px; text-align: center;">
    <p style="color: white; margin: 0; font-size: 0.9em; font-weight: bold;">{row['division']}</p>
    <p style="color: white; font-size: 1.8em; font-weight: bold; margin: 8px 0;">{rate:.1f}%</p>
    <p style="color: #e5e7eb; margin: 3px 0; font-size: 0.75em;">{label}</p>
    <p style="color: #9ca3af; font-size: 0.7em; margin: 0;">{int(row['block_count'])} blk</p>
</div>
""", unsafe_allow_html=True)
            else:
                st.info(f"No ganoderma data for divisions in {sel_estate}")
        else:
            st.warning(f"No divisions found for {sel_estate}")
