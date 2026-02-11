# DATA DISCREPANCY INVESTIGATION REPORT

## Problem Statement

Boss's manual calculation from Excel files shows different numbers than database query results.

---

## FINDINGS

### 1. Manual Count (from Excel - Boss's calculation):

**2023:**
- Actual: **141,984 Ton**
- Target: **188,208 Ton**

**2024:**
- Actual: **TBD** (Boss to provide)
- Target: **TBD** (Boss to provide)

**2025:**
- Actual: **TBD** (Boss to provide)
- Target: **TBD** (Boss to provide)

---

### 2. Database Query Results:

**2023:**
- Actual: **140,396.31 Ton**
- Target: **186,157.99 Ton**

**2024:**
- Actual: **135,503.34 Ton**
- Target: **188,827.38 Ton**

**2025:**
- Actual: **142,233.87 Ton**
- Target: **189,792.07 Ton**

**TOTAL:**
- Actual: **418,133.52 Ton**
- Target: **564,777.44 Ton**

---

### 3. Discrepancy for 2023:

| Metric | Excel | Database | Difference |
|--------|-------|----------|------------|
| **Actual** | 141,984.00 | 140,396.31 | **-1,587.69 Ton** |
| **Target** | 188,208.00 | 186,157.99 | **-2,050.01 Ton** |

**Difference:** Database is **MISSING ~1,588 Ton** of actual production and **~2,050 Ton** of target.

---

## ROOT CAUSE

### Database Data Quality Issues:

1. **99 NULL values** in `real_ton` or `potensi_ton` columns
2. **150 ZERO values** in `real_ton` or `potensi_ton` columns
3. **107 problematic records in 2023 alone**

### Why This Happened:
- Data upload from Excel to Supabase may have had errors
- Some records were not properly uploaded
- Or values were corrupted during migration

---

## IMMEDIATE OPTIONS

### Option 1: FIX THE DATABASE (Recommended)
**Action:** Re-upload production data from source Excel files

**Steps:**
1. Identify missing/corrupted records
2. Extract correct values from Excel
3. Update or re-insert records in Supabase
4. Verify totals match Boss's manual count

**Pros:** 
- Database becomes accurate source of truth
- All future queries will be correct
- Consistent across all systems

**Cons:** 
- Requires database update script
- Need to identify exact missing records

---

### Option 2: USE EXCEL VALUES (Temporary)
**Action:** Hard-code Boss's manual numbers in dashboard calculations

**Code change example:**
```python
# Instead of:
total_production_actual = df_filtered['real_ton'].sum()

# Use:
MANUAL_VALUES = {
    2023: {'actual': 141984, 'target': 188208},
    2024: {'actual': 135503, 'target': 188827},  # Verify with Boss
    2025: {'actual': 142234, 'target': 189792}   # Verify with Boss
}
# Filter and sum based on these values
```

**Pros:**
- Quick fix
- Matches Boss's verification

**Cons:**
- Not scalable
- Database still incorrect
- Hard to maintain

---

## RECOMMENDATION

**FIX THE DATABASE (Option 1)**

### Next Steps:

1. **Boss provides complete manual totals for 2024 and 2025**
   - So we can verify all years

2. **Create database fix script**
   - Compare Excel row-by-row with database
   - Identify exact missing/corrupted records
   - Generate UPDATE/INSERT SQL statements

3. **Run fix and verify**
   - Execute database updates
   - Re-query and confirm totals match

4. **Update dashboard**
   - Will automatically show correct values once DB is fixed

---

## PENDING INFORMATION NEEDED

**Boss, please provide manual counts for:**

### 2024:
- Actual Production: _____ Ton
- Target Production: _____ Ton

### 2025:
- Actual Production: _____ Ton
- Target Production: _____ Ton

This will help us verify the full scope of the data quality issue.

---

## CURRENT DASHBOARD STATUS

### Total Area: ✅ FIXED
- Now correctly shows ~9,885 Ha (unique blocks)

### Production Metrics: ⚠️ UNDER INVESTIGATION
- Currently shows database values (with ~1,588 Ton missing for 2023)
- Need database fix or use Excel values

### Risk Exposure: ⚠️ PENDING
- Waiting for decision on counting method

---

**Report Date:** 2026-02-06  
**Status:** Data discrepancy identified, awaiting decision on fix approach
