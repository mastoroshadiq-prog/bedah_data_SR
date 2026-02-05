# TIER 1 EXECUTIVE DASHBOARD - SETUP GUIDE
## Interactive Python Dashboard with Streamlit

---

## 🚀 INSTALLATION (5 Minutes)

### Step 1: Install Streamlit & Dependencies

```bash
pip install streamlit plotly python-dotenv
```

*(supabase-py dan pandas sudah terinstall)*

---

### Step 2: Run Dashboard

```bash
streamlit run dashboard_tier1_executive.py
```

**Dashboard akan otomatis terbuka di browser:** `http://localhost:8501`

---

## ✨ FEATURES

### 1. **Interactive Filters** (Sidebar)
- 📅 **Year Selector:** 2023, 2024, 2025
- 🏢 **Estate Filter:** All, AME, OLE, DBE
- 🔄 **Real-time Updates:** Data refresh otomatis

### 2. **Hero Metrics** (Top Row)
- 📏 Total Planted Area (Ha)
- 📦 Production Achievement (Ton + %)
- 📉 Performance Gap (Ton + %)
- ⚠️  Risk Exposure (Block count + %)

### 3. **Production Gap Waterfall**
- 💧 Visual target → actual breakdown
- 🏢 Gap per estate (AME, OLE, DBE)
- 💰 Shows where production is lost

### 4. **Estate Performance Heatmap**
- 🔥 3-year trend (2023-2025)
- 🎨 Color-coded: Red (poor) → Green (excellent)
- 📈 Shows improvement trajectory

### 5. **Risk Distribution**
- 🎯 Pie chart: Critical/High/Medium/On-target
- 💵 **Financial Impact Calculator**
  - Input CPO price
  - Auto-calculate opportunity loss
  - Shows unrealized revenue

### 6. **Top & Bottom 10 Performers**
- ✅ Best performers (learn from success)
- ❌ Worst performers (urgent action needed)
- 🔴 Critical blocks highlighted

---

## 🎨 INTERACTIVE FEATURES

### Filters Work Real-Time:
1. **Select Year** → All charts update instantly
2. **Select Estate** → Focus on AME/OLE/DBE only
3. **Change CPO Price** → Financial impact recalculates

### Hover Interactions:
- Hover charts → See exact values
- Hover tables → Highlight rows
- Click legend → Filter data

### Export Capabilities:
- 📸 Screenshot charts (built-in icon)
- 📊 Download data tables
- 🖨️ Print-friendly view

---

## 💻 USAGE EXAMPLES

### Scenario 1: Board Meeting
```
1. Select "2025" → Latest year
2. Select "All" estates → Full portfolio view
3. Present Hero Metrics → Quick snapshot
4. Show Waterfall → Where we lose production
5. Show Risk Distribution → Action priorities
```

### Scenario 2: Estate Deep Dive
```
1. Select "2024"
2. Select "AME" → Focus on underperforming estate
3. Check heatmap → Improvement trend?
4. Review Bottom 10 → Which blocks need help
5. Calculate financial impact → ROI for intervention
```

### Scenario 3: Year-over-Year Comparison
```
1. Select "2023" → Note metrics
2. Select "2024" → Compare
3. Select "2025" → See progression
4. Heatmap shows 3-year trend automatically
```

---

## 📊 CUSTOMIZATION

### Change CPO Price:
- Dashboard has input field
- Default: Rp 2,500,000/Ton
- Adjust based on market price
- Financial impact updates instantly

### Add More Filters (Optional):
Edit `dashboard_tier1_executive.py`:
```python
# Add category filter (Inti/Plasma)
selected_category = st.sidebar.selectbox(
    "Select Category",
    ['All', 'Inti', 'Plasma']
)
```

---

## 🌐 DEPLOYMENT (Share with Stakeholders)

### Option 1: Streamlit Community Cloud (FREE)
```bash
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect GitHub repo
4. Deploy! (1-click)
```

**Result:** Public URL like `your-dashboard.streamlit.app`

### Option 2: Secure Internal Deployment
```bash
1. Deploy to company server
2. Add authentication (Streamlit Auth)
3. Restrict access to shareholders only
```

---

## 🔧 TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Fix:**
```bash
pip install streamlit
```

### Issue: Dashboard slow to load
**Fix:** Already cached! Data loads once, then cached for 10 min

### Issue: Charts not showing
**Fix:** Make sure Plotly installed:
```bash
pip install plotly
```

---

## 📱 MOBILE RESPONSIVE

✅ Dashboard automatically responsive  
✅ Works on tablets & phones  
✅ Charts adapt to screen size

---

## 🎯 NEXT STEPS

After Tier 1 works:
1. ✅ **Tier 2:** Add root cause analysis (age, disease, SPH correlation)
2. ✅ **Tier 3:** Operational dashboard for field managers
3. ✅ **Tier 4:** Geospatial map visualization

---

## 💡 PRO TIPS

1. **Bookmark the URL** → Quick access
2. **Use filters frequently** → Different perspectives
3. **Screenshot for presentations** → Built-in feature
4. **Update CPO price monthly** → Accurate financial impact
5. **Check daily** → Real-time data from Supabase

---

## ✅ SUCCESS CHECKLIST

- [ ] Streamlit installed
- [ ] Dashboard runs successfully
- [ ] All charts visible
- [ ] Filters work
- [ ] Financial calculator works
- [ ] Data loads from Supabase
- [ ] Ready to share with stakeholders!

---

**🎉 Congratulations! You now have a professional, interactive executive dashboard!**

**Run command:**
```bash
streamlit run dashboard_tier1_executive.py
```

**Expected:** Browser opens automatically with beautiful dashboard! 🌴📊
