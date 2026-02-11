# KEY PERFORMANCE INDICATORS - CALCULATION ANALYSIS

## Overview
This document explains the data sources and formulas for all KPIs shown in the dashboard.

---

## 1. TOTAL AREA: **29,474 Ha**

### Data Source:
- **Table:** `block_land_infrastructure`
- **Column:** `total_luas_sd_2025_ha`

### Calculation:
```python
total_area = df_filtered['total_luas_sd_2025_ha'].sum()
```

### Code Location:
`dashboard_tier1_executive.py` - Line 247

### Notes:
- Sums the total land area (in hectares) for all blocks
- Uses infrastructure table which contains the most up-to-date land area data
- Filtered by selected year and estate

---

## 2. PRODUCTION ACTUAL: **418,134 Ton** (↑ 74.0% of target)

### Data Source:
- **Table:** `production_annual`
- **Column:** `real_ton` (actual production)
- **Column:** `potensi_ton` (target/potential production)

### Calculations:
```python
total_production_actual = df_filtered['real_ton'].sum()
total_production_target = df_filtered['potensi_ton'].sum()
achievement_pct = (total_production_actual / total_production_target * 100)
```

### Code Location:
`dashboard_tier1_executive.py` - Lines 248-251

### Breakdown by Year:
- **2023:** 140,396 Ton
- **2024:** 135,503 Ton
- **2025:** 142,234 Ton
- **TOTAL:** 418,134 Ton

### Notes:
- Real production across all years (2023-2025)
- Achievement percentage: **74.0%** means we're achieving 74% of our target
- This is aggregated from all blocks across all selected years

---

## 3. PRODUCTION GAP: **-146,644 Ton** (↓ -26.0%)

### Data Source:
- **Table:** `production_annual`
- **Columns:** `real_ton` and `potensi_ton`

### Calculations:
```python
total_gap = total_production_actual - total_production_target
gap_percentage = (total_gap / total_production_target * 100)
```

### Code Location:
`dashboard_tier1_executive.py` - Line 250

### Formula Breakdown:
```
Total Gap = Actual Production - Target Production
          = 418,134 - 564,778
          = -146,644 Ton

Gap Percentage = (-146,644 / 564,778) * 100
               = -26.0%
```

### Gap by Year:
- **2023:** -45,762 Ton
- **2024:** -53,324 Ton
- **2025:** -47,558 Ton
- **TOTAL:** -146,644 Ton

### Notes:
- **Negative value** means underperformance (production is below target)
- **-26.0%** means we're **26% below target** (or achieving only 74% of target)
- This represents the total opportunity loss in terms of production volume

---

## 4. RISK EXPOSURE: **1335 Blocks** (↑ 69.7% of portfolio)

### Data Source:
- **Table:** `production_annual`
- **Derived Column:** `gap_pct_ton` (calculated)

### Calculations:
```python
# Calculate gap percentage per block
gap_pct_ton = ((real_ton - potensi_ton) / potensi_ton) * 100

# Count risk blocks
critical_blocks = COUNT where gap_pct_ton < -20%
high_risk_blocks = COUNT where -20% <= gap_pct_ton < -10%
total_risk_blocks = critical_blocks + high_risk_blocks

# Risk percentage
risk_percentage = (total_risk_blocks / total_blocks) * 100
```

### Code Location:
`dashboard_tier1_executive.py` - Lines 253-256

### Risk Categories:
- **Critical Blocks** (Gap < -20%): Severely underperforming
- **High Risk Blocks** (-20% ≤ Gap < -10%): Underperforming
- **Total Risk Blocks:** Critical + High Risk = 1335
- **Total Blocks in Portfolio:** ~1913 blocks
- **Risk Exposure:** 1335 / 1913 = **69.7%**

### Notes:
- Almost **70% of blocks** are underperforming by more than 10%
- This is a **critical metric** indicating widespread production issues
- Used to identify blocks requiring immediate attention

---

## DATA FLOW DIAGRAM

```
┌─────────────────────┐
│ production_annual   │ ← Main data source (yearly production records)
│ - year              │
│ - block_id          │
│ - real_ton          │ → Actual production
│ - potensi_ton       │ → Target production
└──────────┬──────────┘
           │
           │ MERGE (on block_id)
           ↓
┌─────────────────────────────┐
│ block_land_infrastructure   │ ← Land area data
│ - block_id                  │
│ - total_luas_sd_2025_ha     │ → Total area
└─────────────────────────────┘

FILTERED BY:
- selected_year (or "All Years")
- selected_estate (or "All")

CALCULATED METRICS:
→ Total Area (SUM)
→ Production Actual (SUM real_ton)
→ Production Target (SUM potensi_ton)
→ Production Gap (Actual - Target)
→ Achievement % (Actual / Target * 100)
→ Gap % ([Actual - Target] / Target * 100)
→ Risk Blocks (COUNT where gap_pct_ton < -10%)
```

---

## VERIFICATION RESULTS

✅ **All calculations verified against database:**

| Metric | Dashboard Value | Calculated Value | Match |
|--------|----------------|------------------|-------|
| Total Area | 29,474 Ha | 29,474 Ha | ✓ |
| Production Actual | 418,134 Ton | 418,134 Ton | ✓ |
| Achievement % | 74.0% | 74.0% | ✓ |
| Production Gap | -146,644 Ton | -146,644 Ton | ✓ |
| Gap % | -26.0% | -26.0% | ✓ |
| Risk Blocks | 1335 | 1335 | ✓ |
| Risk % | 69.7% | 69.7% | ✓ |

---

## INTERPRETATION GUIDE

### 74.0% Achievement (or -26.0% Gap)
These two metrics show the same information from different perspectives:
- **74.0% achievement** = We're getting 74% of what we targeted
- **-26.0% gap** = We're 26% short of our target

Both are correct and complementary.

### Why 69.7% Risk Exposure is Critical
This means almost 7 out of 10 blocks are underperforming significantly (>10% below target).
This high percentage indicates:
- Systemic production issues across the portfolio
- High correlation between Ganoderma infection and production loss
- Urgent need for intervention in the majority of blocks

---

## FILES USED FOR VERIFICATION
- `verify_kpi_calculations.py` - Full detailed verification
- `verify_kpi_simple.py` - Simplified verification
- This analysis confirms all KPI calculations are accurate and traceable

---

**Generated:** 2026-02-06  
**Verification Status:** ✅ All metrics verified accurate
