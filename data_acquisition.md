# DATA ACQUISITION SPEC — "Salary Reality Check"
# All datasets required to build public/data/cities.json
# Version: 1.0 | Format: AI Agent Instruction Document
# Read this BEFORE running scripts/build-data.py

---

## HOW TO READ THIS DOCUMENT

This document tells an AI agent exactly where to get every dataset, how to download it,
what columns to extract, and how to join everything into the final cities.json file.

Follow sections in order: 1 → 2 → 3 → 4 → 5 → 6 (join) → 7 (validate).
Do not skip sections. Do not invent data values.
Every field in cities.json must trace to a source in this document.

---

## SECTION 0: OUTPUT TARGET

All data collected in this document feeds into one output file:

```
public/data/cities.json
```

Schema reminder (from agent-build-spec.md Section 3.1):

```json
{
  "id": "41860",
  "name": "San Francisco, CA",
  "short": "SF",
  "state": "CA",
  "region": "West",
  "stateTaxRate": 0.093,
  "medianRent1BR": 26400,
  "colIndex": 178,
  "salaries": {
    "15-1252": 168000,
    "11-1021": 148000
  }
}
```

Fields by source:
- `id`, `name`, `short`, `state`, `region` → BLS metro definitions (Section 1)
- `salaries` → BLS OEWS (Section 1)
- `medianRent1BR` → Zillow ZORI (Section 2)
- `stateTaxRate` → Tax Foundation hardcoded table (Section 3)
- `colIndex` → Numbeo or BEA RPP (Section 4)

The MIT Living Wage data (Section 5) is NOT stored in cities.json.
It is used as a secondary reference only — for the livability threshold line on charts.
Store it in a separate file: `public/data/living-wage.json`

---

## SECTION 1: BLS OEWS — SALARY DATA

### Status: FREE. No account required. Direct download.

### What this provides:
- `salaries` object (median annual wage per occupation per metro)
- `id` (CBSA code)
- `name` (metro area full name)
- `state` (2-letter abbreviation, derived from name)
- `region` (derived from state using lookup table in Section 6)

---

### 1.1 — Download Instructions

**Step 1:** Download the bulk ZIP file.

```
URL: https://www.bls.gov/oes/special.requests/oesm24ma.zip
Method: HTTP GET (no auth required)
Size: ~50MB
```

In Python:
```python
import requests, zipfile, io

url = "https://www.bls.gov/oes/special.requests/oesm24ma.zip"
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall("data/raw/bls/")
```

**Step 2:** After extraction, locate the target file:
```
data/raw/bls/MSA_M2024_dl.xlsx
```
This single file contains ALL metro areas and ALL occupations.

**Step 3:** Download the metro area definitions file (maps CBSA codes → city names).

```
URL: https://www.bls.gov/oes/2024/may/oessrcma.htm
Action: On this page, find and download the link labeled
        "Metropolitan area definitions (XLSX)"
Save as: data/raw/bls/metro_definitions.xlsx
```

---

### 1.2 — Column Reference

In `MSA_M2024_dl.xlsx`:

| Column      | Type   | Description                                              |
|-------------|--------|----------------------------------------------------------|
| `AREA`      | string | CBSA numeric code (e.g. "41860" = San Francisco)         |
| `AREA_TITLE`| string | Metro area name (e.g. "San Francisco-Oakland-Hayward")   |
| `OCC_CODE`  | string | SOC occupation code (e.g. "15-1252")                     |
| `OCC_TITLE` | string | Occupation name (human-readable)                         |
| `A_MEDIAN`  | mixed  | Annual median wage in USD — MAY CONTAIN "#" (suppressed) |
| `A_MEAN`    | mixed  | Annual mean wage — use as fallback if A_MEDIAN = "#"     |

IMPORTANT: `A_MEDIAN` contains the string `"#"` when BLS suppresses data due to small
sample size. When this occurs, use `A_MEAN` instead. If both are suppressed, use the
state-level median for that occupation (see Section 1.4).

---

### 1.3 — Occupation Codes to Extract

Filter `OCC_CODE` to ONLY these 15 codes. Discard all other rows.

```python
TARGET_OCC_CODES = [
    "15-1252",  # Software Developer / Engineer
    "11-1021",  # General & Operations Manager
    "13-2011",  # Accountant / Auditor
    "29-1141",  # Registered Nurse
    "41-2031",  # Retail Sales Worker
    "23-1011",  # Lawyer / Attorney
    "25-2021",  # Elementary School Teacher
    "17-2141",  # Mechanical Engineer
    "27-1024",  # Graphic Designer
    "15-1211",  # Computer Systems Analyst
    "13-1161",  # Market Research Analyst
    "29-1051",  # Pharmacist
    "11-3031",  # Financial Manager
    "43-3031",  # Bookkeeping / Accounting Clerk
    "35-1012",  # Food Service Manager
]
```

---

### 1.4 — Target Cities (50 CBSAs)

Filter `AREA` to ONLY these CBSA codes. Discard all other rows.

```python
TARGET_CBSA_CODES = {
    "12060": {"name": "Atlanta, GA",        "short": "ATL", "state": "GA", "region": "South"},
    "12420": {"name": "Austin, TX",         "short": "AUS", "state": "TX", "region": "South"},
    "12580": {"name": "Baltimore, MD",      "short": "BAL", "state": "MD", "region": "Northeast"},
    "13820": {"name": "Birmingham, AL",     "short": "BHM", "state": "AL", "region": "South"},
    "14460": {"name": "Boston, MA",         "short": "BOS", "state": "MA", "region": "Northeast"},
    "15380": {"name": "Buffalo, NY",        "short": "BUF", "state": "NY", "region": "Northeast"},
    "16740": {"name": "Charlotte, NC",      "short": "CLT", "state": "NC", "region": "South"},
    "16980": {"name": "Chicago, IL",        "short": "CHI", "state": "IL", "region": "Midwest"},
    "17140": {"name": "Cincinnati, OH",     "short": "CIN", "state": "OH", "region": "Midwest"},
    "17460": {"name": "Cleveland, OH",      "short": "CLE", "state": "OH", "region": "Midwest"},
    "18140": {"name": "Columbus, OH",       "short": "CMH", "state": "OH", "region": "Midwest"},
    "19100": {"name": "Dallas, TX",         "short": "DAL", "state": "TX", "region": "South"},
    "19740": {"name": "Denver, CO",         "short": "DEN", "state": "CO", "region": "West"},
    "19820": {"name": "Detroit, MI",        "short": "DET", "state": "MI", "region": "Midwest"},
    "21340": {"name": "El Paso, TX",        "short": "ELP", "state": "TX", "region": "South"},
    "25540": {"name": "Hartford, CT",       "short": "HFD", "state": "CT", "region": "Northeast"},
    "26420": {"name": "Houston, TX",        "short": "HOU", "state": "TX", "region": "South"},
    "26900": {"name": "Indianapolis, IN",   "short": "IND", "state": "IN", "region": "Midwest"},
    "27260": {"name": "Jacksonville, FL",   "short": "JAX", "state": "FL", "region": "South"},
    "28140": {"name": "Kansas City, MO",    "short": "MCI", "state": "MO", "region": "Midwest"},
    "29820": {"name": "Las Vegas, NV",      "short": "LAS", "state": "NV", "region": "West"},
    "31080": {"name": "Los Angeles, CA",    "short": "LAX", "state": "CA", "region": "West"},
    "31140": {"name": "Louisville, KY",     "short": "SDF", "state": "KY", "region": "South"},
    "32820": {"name": "Memphis, TN",        "short": "MEM", "state": "TN", "region": "South"},
    "33100": {"name": "Miami, FL",          "short": "MIA", "state": "FL", "region": "South"},
    "33340": {"name": "Milwaukee, WI",      "short": "MKE", "state": "WI", "region": "Midwest"},
    "33460": {"name": "Minneapolis, MN",    "short": "MSP", "state": "MN", "region": "Midwest"},
    "34980": {"name": "Nashville, TN",      "short": "BNA", "state": "TN", "region": "South"},
    "35380": {"name": "New Orleans, LA",    "short": "MSY", "state": "LA", "region": "South"},
    "35620": {"name": "New York, NY",       "short": "NYC", "state": "NY", "region": "Northeast"},
    "36420": {"name": "Oklahoma City, OK",  "short": "OKC", "state": "OK", "region": "South"},
    "36740": {"name": "Orlando, FL",        "short": "MCO", "state": "FL", "region": "South"},
    "37980": {"name": "Philadelphia, PA",   "short": "PHL", "state": "PA", "region": "Northeast"},
    "38060": {"name": "Phoenix, AZ",        "short": "PHX", "state": "AZ", "region": "West"},
    "38300": {"name": "Pittsburgh, PA",     "short": "PIT", "state": "PA", "region": "Northeast"},
    "38900": {"name": "Portland, OR",       "short": "PDX", "state": "OR", "region": "West"},
    "39300": {"name": "Providence, RI",     "short": "PVD", "state": "RI", "region": "Northeast"},
    "39580": {"name": "Raleigh, NC",        "short": "RDU", "state": "NC", "region": "South"},
    "40060": {"name": "Richmond, VA",       "short": "RIC", "state": "VA", "region": "South"},
    "40140": {"name": "Riverside, CA",      "short": "RIV", "state": "CA", "region": "West"},
    "40900": {"name": "Sacramento, CA",     "short": "SMF", "state": "CA", "region": "West"},
    "41620": {"name": "Salt Lake City, UT", "short": "SLC", "state": "UT", "region": "West"},
    "41700": {"name": "San Antonio, TX",    "short": "SAT", "state": "TX", "region": "South"},
    "41740": {"name": "San Diego, CA",      "short": "SAN", "state": "CA", "region": "West"},
    "41860": {"name": "San Francisco, CA",  "short": "SF",  "state": "CA", "region": "West"},
    "41940": {"name": "San Jose, CA",       "short": "SJC", "state": "CA", "region": "West"},
    "42660": {"name": "Seattle, WA",        "short": "SEA", "state": "WA", "region": "West"},
    "41180": {"name": "St. Louis, MO",      "short": "STL", "state": "MO", "region": "Midwest"},
    "45300": {"name": "Tampa, FL",          "short": "TPA", "state": "FL", "region": "South"},
    "47900": {"name": "Washington, DC",     "short": "DC",  "state": "DC", "region": "Northeast"},
}
```

---

### 1.5 — Extraction Script (complete)

```python
import pandas as pd
import json

# Load BLS salary data
df = pd.read_excel("data/raw/bls/MSA_M2024_dl.xlsx", dtype={"AREA": str, "OCC_CODE": str})

# Filter to target cities and occupations
df = df[df["AREA"].isin(TARGET_CBSA_CODES.keys())]
df = df[df["OCC_CODE"].isin(TARGET_OCC_CODES)]

# Handle suppressed values: "#" means BLS withheld data
df["A_MEDIAN"] = pd.to_numeric(df["A_MEDIAN"], errors="coerce")
df["A_MEAN"]   = pd.to_numeric(df["A_MEAN"],   errors="coerce")
df["wage"]     = df["A_MEDIAN"].fillna(df["A_MEAN"])

# Pivot: one row per city, columns = occ codes
pivot = df.pivot_table(index="AREA", columns="OCC_CODE", values="wage", aggfunc="first")

# Build base city objects
cities = {}
for cbsa, meta in TARGET_CBSA_CODES.items():
    cities[cbsa] = {
        "id":      cbsa,
        "name":    meta["name"],
        "short":   meta["short"],
        "state":   meta["state"],
        "region":  meta["region"],
        "salaries": {}
    }
    if cbsa in pivot.index:
        for occ in TARGET_OCC_CODES:
            val = pivot.loc[cbsa, occ] if occ in pivot.columns else None
            if pd.notna(val):
                cities[cbsa]["salaries"][occ] = int(round(val / 100) * 100)  # round to $100

print(f"Loaded salary data for {len(cities)} cities")
```

---

## SECTION 2: ZILLOW ZORI — RENT DATA

### Status: FREE. No account required. Direct CSV download.

### What this provides:
- `medianRent1BR` field (annual 1BR rent in USD)

---

### 2.1 — Download Instructions

**Primary URL (attempt first):**
```
https://files.zillowstatic.com/research/public_csvs/zori/Metro_ZORI_AllHomesPlusMultifamily_SSA.csv
```

**Fallback (if primary 404s):**
Go to https://www.zillow.com/research/data/
Scroll to "Zillow Observed Rent Index (ZORI)" section.
Find the row: "Metro & U.S. | All homes + Multifamily | Smoothed, Seasonally Adjusted"
Right-click the download button → copy link address.

In Python:
```python
import requests, io
import pandas as pd

zori_url = "https://files.zillowstatic.com/research/public_csvs/zori/Metro_ZORI_AllHomesPlusMultifamily_SSA.csv"
r = requests.get(zori_url)
zori = pd.read_csv(io.StringIO(r.text))
zori.to_csv("data/raw/zillow/metro_zori.csv", index=False)
```

---

### 2.2 — Column Reference

| Column        | Description                                       |
|---------------|---------------------------------------------------|
| `RegionName`  | Metro area name (e.g. "New York, NY")             |
| `SizeRank`    | Market size rank (1 = largest)                    |
| `RegionID`    | Zillow internal ID (not the same as CBSA)         |
| Date columns  | Monthly ZORI value in dollars (e.g. `2024-12-31`) |

The last date column is the most recent month. Take that value × 12 for annual rent.

---

### 2.3 — Name Matching Strategy

Zillow names ≠ BLS names. Examples:

| BLS Name                               | Zillow Name          |
|----------------------------------------|----------------------|
| New York-Newark-Jersey City, NY-NJ-PA  | New York, NY         |
| San Francisco-Oakland-Hayward, CA      | San Francisco, CA    |
| Dallas-Fort Worth-Arlington, TX        | Dallas-Fort Worth, TX|
| Washington-Arlington-Alexandria, DC    | Washington, DC       |

Use fuzzy matching:
```python
from rapidfuzz import process, fuzz

def match_zillow_to_cbsa(zillow_name, cbsa_names_dict):
    """
    cbsa_names_dict: {cbsa_code: city_short_name}  e.g. {"41860": "San Francisco, CA"}
    Returns best matching CBSA code or None if score < 75
    """
    choices = {code: meta["name"] for code, meta in TARGET_CBSA_CODES.items()}
    result = process.extractOne(
        zillow_name,
        choices,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=75
    )
    return result[2] if result else None  # returns the CBSA code key
```

---

### 2.4 — Extraction Script (complete)

```python
# Assumes zori DataFrame already loaded from Section 2.1

# Get the most recent date column (last column after metadata cols)
date_cols = [c for c in zori.columns if c[:4].isdigit()]
latest_col = sorted(date_cols)[-1]
print(f"Using Zillow rent data from: {latest_col}")

# Build lookup: zillow_name → annual_rent
zori_lookup = {}
for _, row in zori.iterrows():
    annual_rent = row[latest_col] * 12
    zori_lookup[row["RegionName"]] = round(annual_rent / 100) * 100  # round to $100

# Match to cities dict using fuzzy matching
for cbsa, city in cities.items():
    cbsa_display = f"{city['name']}"
    match = process.extractOne(
        cbsa_display,
        zori_lookup,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=70
    )
    if match:
        cities[cbsa]["medianRent1BR"] = zori_lookup[match[0]]
    else:
        print(f"WARNING: No Zillow rent match for {city['name']} (CBSA {cbsa})")
        cities[cbsa]["medianRent1BR"] = None  # handle in validation step

print(f"Rent data matched for {sum(1 for c in cities.values() if c.get('medianRent1BR'))} cities")
```

---

## SECTION 3: TAX FOUNDATION — STATE TAX RATES

### Status: FREE. Hardcode directly — no file download needed.

### What this provides:
- `stateTaxRate` field (effective state + local income tax rate as decimal)

---

### 3.1 — Methodology

These are effective marginal rates for a single filer earning approximately $100,000/year.
They incorporate state income tax brackets and, where applicable, the major city income tax
surcharge (e.g. New York City adds ~3.876% on top of the state rate).

This is a deliberate simplification. The visualization is not a tax calculator.
All charts display a prominent tooltip: "Tax estimates are approximate."

Source reference: https://taxfoundation.org/data/all/state/state-income-tax-rates-2024/

---

### 3.2 — Complete Hardcoded Rate Table

```python
STATE_TAX_RATES = {
    # No income tax states
    "TX": 0.0000,
    "FL": 0.0000,
    "NV": 0.0000,
    "WA": 0.0000,
    "SD": 0.0000,
    "WY": 0.0000,
    "AK": 0.0000,
    "TN": 0.0000,
    "NH": 0.0000,

    # Low tax states (flat or low bracket)
    "PA": 0.0307,
    "IN": 0.0323,
    "AZ": 0.0250,
    "CO": 0.0440,
    "MI": 0.0425,
    "UT": 0.0455,

    # Moderate tax states
    "OH": 0.0400,
    "GA": 0.0550,
    "AL": 0.0500,
    "LA": 0.0430,
    "OK": 0.0490,
    "KS": 0.0570,
    "MO": 0.0540,
    "SC": 0.0650,
    "NC": 0.0475,
    "VA": 0.0575,
    "MA": 0.0500,
    "KY": 0.0450,
    "RI": 0.0599,
    "WI": 0.0530,
    "IL": 0.0495,
    "IA": 0.0570,

    # Higher tax states
    "MD": 0.0750,   # includes avg local tax ~3.2%
    "CT": 0.0699,
    "DC": 0.0850,   # DC has its own income tax
    "NJ": 0.0637,
    "MN": 0.0785,
    "VT": 0.0870,
    "OR": 0.0990,

    # Highest tax states
    "CA": 0.0930,
    "NY": 0.1080,   # includes NYC local tax ~3.876% for NYC metro
}

# Apply to cities dict
for cbsa, city in cities.items():
    state = city["state"]
    cities[cbsa]["stateTaxRate"] = STATE_TAX_RATES.get(state, 0.05)  # 0.05 fallback
```

---

### 3.3 — Special Cases

```
NY (NYC metro only): 0.1080 — includes NY state (6.85%) + NYC local (3.876% effective)
     For non-NYC NY metros (Buffalo, etc.): use 0.065 (state only)
MD: 0.075 — includes MD state (~4.75%) + average county tax (~3.2%)
DC: 0.085 — DC levies its own income tax, no state
```

Implement this exception for NYC vs. other NY metros:
```python
# After the main loop above, override Buffalo specifically
if "15380" in cities:  # Buffalo, NY CBSA
    cities["15380"]["stateTaxRate"] = 0.0650
```

---

## SECTION 4: COST OF LIVING INDEX

### Status: FREE. Two options. Use Option A (Numbeo) as primary.

### What this provides:
- `colIndex` field (national average = 100, higher = more expensive)

---

### Option A — Numbeo (RECOMMENDED)

**URL:** https://www.numbeo.com/cost-of-living/rankings_current.jsp

**Free API endpoint:**
```
https://www.numbeo.com/api/indices?api_key=free&country=United+States
```

NOTE: If the free API key is rate-limited, use the manual CSV export instead:
- Go to https://www.numbeo.com/cost-of-living/rankings_current.jsp
- Click "Export to CSV" button at the bottom of the table
- Save as: `data/raw/numbeo/us_col_index.csv`

**Column reference:**
| Column           | Description                                |
|------------------|--------------------------------------------|
| `city`           | City name (e.g. "San Francisco, CA")       |
| `col_index`      | Cost of Living Index (NYC ≈ 100 baseline)  |

IMPORTANT: Numbeo's index uses New York City as approximately 100.
To normalize to national average = 100 (to match ACCRA convention), apply this transform:
```python
# Numbeo NYC ≈ 100. US national average ≈ 72 on Numbeo scale.
# Multiply all Numbeo values by (100/72) to rescale national avg to 100.
NUMBEO_RESCALE_FACTOR = 100 / 72

numbeo_normalized = {city: round(val * NUMBEO_RESCALE_FACTOR) for city, val in numbeo_raw.items()}
```

**Extraction script:**
```python
import requests
from rapidfuzz import process, fuzz

# Try API first
try:
    r = requests.get("https://www.numbeo.com/api/indices?api_key=free&country=United+States", timeout=10)
    numbeo_data = r.json()
    numbeo_lookup = {}
    for item in numbeo_data.get("response", []):
        city_name = item.get("city", "")
        col_val = item.get("cost_of_living_index", None)
        if col_val:
            numbeo_lookup[city_name] = round(col_val * NUMBEO_RESCALE_FACTOR)
except Exception as e:
    print(f"API failed ({e}), load from CSV fallback")
    numbeo_df = pd.read_csv("data/raw/numbeo/us_col_index.csv")
    numbeo_lookup = dict(zip(numbeo_df["city"], (numbeo_df["col_index"] * NUMBEO_RESCALE_FACTOR).round()))

# Match to cities
for cbsa, city in cities.items():
    match = process.extractOne(
        city["name"],
        numbeo_lookup,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=65
    )
    if match:
        cities[cbsa]["colIndex"] = int(numbeo_lookup[match[0]])
    else:
        print(f"WARNING: No CoL index match for {city['name']}")
        cities[cbsa]["colIndex"] = 100  # use national average as safe fallback
```

---

### Option B — BEA Regional Price Parities (government alternative)

**URL:** https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area

**Download path:**
- Go to the page above
- Select "Interactive Data" → "Regional Price Parities"
- Table: "RPP by Metropolitan Statistical Area" (annual, most recent year)
- Export as CSV

**Key columns:** `GeoFips` (FIPS code, close to CBSA), `GeoName`, `RPP` (index, US=100)

Use BEA RPP only if Numbeo data is unavailable or agent has no internet access.
BEA RPP is at state level for some metros — use state RPP as fallback when metro is missing.

---

## SECTION 5: MIT LIVING WAGE — LIVABILITY THRESHOLD

### Status: FREE for manual use. Do NOT scrape. Collect manually or use HUD FMR.

### What this provides:
- Annual living wage for 1 adult, 0 children, per metro
- Stored in `public/data/living-wage.json` (NOT in cities.json)
- Used only for the threshold line on Chapter 3 chart

---

### 5.1 — URL Pattern

```
Pattern: https://livingwage.mit.edu/metros/{CBSA_CODE}
Example: https://livingwage.mit.edu/metros/41860   (San Francisco)
Example: https://livingwage.mit.edu/metros/35620   (New York)
Example: https://livingwage.mit.edu/metros/19100   (Dallas)
```

All 50 CBSA codes are in Section 1.4. Use that same list.

---

### 5.2 — Data to Collect Per City

On each MIT metro page, find the table titled "Living Wages" and record:
- Row: "1 Adult" (zero children)
- Column: "Annual" (not hourly)

---

### 5.3 — Output Format

```json
// public/data/living-wage.json
{
  "41860": 57200,
  "35620": 62800,
  "19100": 44600,
  "...": "..."
}
```

---

### 5.4 — Free Alternative: HUD Fair Market Rents

If the agent cannot collect MIT data manually, use HUD Fair Market Rents as the
livability baseline instead. HUD FMR is fully programmatic and free.

```
URL: https://www.huduser.gov/portal/datasets/fmr.html
Download: FY2025 FMR (Excel)
File: FY25_4050_FMRs.xlsx (or equivalent current year)
Key column: fmr_1 = 1-bedroom FMR (monthly)
Join key: CBSA code (column: cbsasub or metro column)
```

HUD FMR represents the 40th percentile rent — lower than Zillow's median,
but useful as a floor reference for the livability threshold.

---

## SECTION 6: DATA JOIN PIPELINE

### File: scripts/build-data.py (complete pipeline)

Run this script AFTER all raw data files are downloaded to `data/raw/`.

```python
"""
build-data.py
Joins all datasets into public/data/cities.json
Run from project root: python scripts/build-data.py
Dependencies: pip install pandas openpyxl rapidfuzz requests
"""

import pandas as pd
import json
import requests
import zipfile
import io
from rapidfuzz import process, fuzz

# ── CONFIG ──────────────────────────────────────────────────────────────────

TARGET_OCC_CODES = [
    "15-1252","11-1021","13-2011","29-1141","41-2031",
    "23-1011","25-2021","17-2141","27-1024","15-1211",
    "13-1161","29-1051","11-3031","43-3031","35-1012",
]

TARGET_CBSA_CODES = {
    "12060":{"name":"Atlanta, GA","short":"ATL","state":"GA","region":"South"},
    "12420":{"name":"Austin, TX","short":"AUS","state":"TX","region":"South"},
    "12580":{"name":"Baltimore, MD","short":"BAL","state":"MD","region":"Northeast"},
    "13820":{"name":"Birmingham, AL","short":"BHM","state":"AL","region":"South"},
    "14460":{"name":"Boston, MA","short":"BOS","state":"MA","region":"Northeast"},
    "15380":{"name":"Buffalo, NY","short":"BUF","state":"NY","region":"Northeast"},
    "16740":{"name":"Charlotte, NC","short":"CLT","state":"NC","region":"South"},
    "16980":{"name":"Chicago, IL","short":"CHI","state":"IL","region":"Midwest"},
    "17140":{"name":"Cincinnati, OH","short":"CIN","state":"OH","region":"Midwest"},
    "17460":{"name":"Cleveland, OH","short":"CLE","state":"OH","region":"Midwest"},
    "18140":{"name":"Columbus, OH","short":"CMH","state":"OH","region":"Midwest"},
    "19100":{"name":"Dallas, TX","short":"DAL","state":"TX","region":"South"},
    "19740":{"name":"Denver, CO","short":"DEN","state":"CO","region":"West"},
    "19820":{"name":"Detroit, MI","short":"DET","state":"MI","region":"Midwest"},
    "21340":{"name":"El Paso, TX","short":"ELP","state":"TX","region":"South"},
    "25540":{"name":"Hartford, CT","short":"HFD","state":"CT","region":"Northeast"},
    "26420":{"name":"Houston, TX","short":"HOU","state":"TX","region":"South"},
    "26900":{"name":"Indianapolis, IN","short":"IND","state":"IN","region":"Midwest"},
    "27260":{"name":"Jacksonville, FL","short":"JAX","state":"FL","region":"South"},
    "28140":{"name":"Kansas City, MO","short":"MCI","state":"MO","region":"Midwest"},
    "29820":{"name":"Las Vegas, NV","short":"LAS","state":"NV","region":"West"},
    "31080":{"name":"Los Angeles, CA","short":"LAX","state":"CA","region":"West"},
    "31140":{"name":"Louisville, KY","short":"SDF","state":"KY","region":"South"},
    "32820":{"name":"Memphis, TN","short":"MEM","state":"TN","region":"South"},
    "33100":{"name":"Miami, FL","short":"MIA","state":"FL","region":"South"},
    "33340":{"name":"Milwaukee, WI","short":"MKE","state":"WI","region":"Midwest"},
    "33460":{"name":"Minneapolis, MN","short":"MSP","state":"MN","region":"Midwest"},
    "34980":{"name":"Nashville, TN","short":"BNA","state":"TN","region":"South"},
    "35380":{"name":"New Orleans, LA","short":"MSY","state":"LA","region":"South"},
    "35620":{"name":"New York, NY","short":"NYC","state":"NY","region":"Northeast"},
    "36420":{"name":"Oklahoma City, OK","short":"OKC","state":"OK","region":"South"},
    "36740":{"name":"Orlando, FL","short":"MCO","state":"FL","region":"South"},
    "37980":{"name":"Philadelphia, PA","short":"PHL","state":"PA","region":"Northeast"},
    "38060":{"name":"Phoenix, AZ","short":"PHX","state":"AZ","region":"West"},
    "38300":{"name":"Pittsburgh, PA","short":"PIT","state":"PA","region":"Northeast"},
    "38900":{"name":"Portland, OR","short":"PDX","state":"OR","region":"West"},
    "39300":{"name":"Providence, RI","short":"PVD","state":"RI","region":"Northeast"},
    "39580":{"name":"Raleigh, NC","short":"RDU","state":"NC","region":"South"},
    "40060":{"name":"Richmond, VA","short":"RIC","state":"VA","region":"South"},
    "40140":{"name":"Riverside, CA","short":"RIV","state":"CA","region":"West"},
    "40900":{"name":"Sacramento, CA","short":"SMF","state":"CA","region":"West"},
    "41620":{"name":"Salt Lake City, UT","short":"SLC","state":"UT","region":"West"},
    "41700":{"name":"San Antonio, TX","short":"SAT","state":"TX","region":"South"},
    "41740":{"name":"San Diego, CA","short":"SAN","state":"CA","region":"West"},
    "41860":{"name":"San Francisco, CA","short":"SF","state":"CA","region":"West"},
    "41940":{"name":"San Jose, CA","short":"SJC","state":"CA","region":"West"},
    "42660":{"name":"Seattle, WA","short":"SEA","state":"WA","region":"West"},
    "41180":{"name":"St. Louis, MO","short":"STL","state":"MO","region":"Midwest"},
    "45300":{"name":"Tampa, FL","short":"TPA","state":"FL","region":"South"},
    "47900":{"name":"Washington, DC","short":"DC","state":"DC","region":"Northeast"},
}

STATE_TAX_RATES = {
    "TX":0.0,"FL":0.0,"NV":0.0,"WA":0.0,"SD":0.0,"WY":0.0,"AK":0.0,"TN":0.0,"NH":0.0,
    "PA":0.0307,"IN":0.0323,"AZ":0.025,"CO":0.044,"MI":0.0425,"UT":0.0455,
    "OH":0.04,"GA":0.055,"AL":0.05,"LA":0.043,"OK":0.049,"KS":0.057,"MO":0.054,
    "SC":0.065,"NC":0.0475,"VA":0.0575,"MA":0.05,"KY":0.045,"RI":0.0599,
    "WI":0.053,"IL":0.0495,"IA":0.057,"MD":0.075,"CT":0.0699,"DC":0.085,
    "NJ":0.0637,"MN":0.0785,"VT":0.087,"OR":0.099,"CA":0.093,"NY":0.108,
}

NUMBEO_RESCALE_FACTOR = 100 / 72

# ── STEP 1: BLS SALARIES ─────────────────────────────────────────────────────

print("Step 1: Loading BLS salary data...")
df = pd.read_excel("data/raw/bls/MSA_M2024_dl.xlsx", dtype={"AREA": str, "OCC_CODE": str})
df = df[df["AREA"].isin(TARGET_CBSA_CODES.keys())]
df = df[df["OCC_CODE"].isin(TARGET_OCC_CODES)]
df["A_MEDIAN"] = pd.to_numeric(df["A_MEDIAN"], errors="coerce")
df["A_MEAN"]   = pd.to_numeric(df["A_MEAN"],   errors="coerce")
df["wage"]     = df["A_MEDIAN"].fillna(df["A_MEAN"])
pivot = df.pivot_table(index="AREA", columns="OCC_CODE", values="wage", aggfunc="first")

cities = {}
for cbsa, meta in TARGET_CBSA_CODES.items():
    cities[cbsa] = {**meta, "id": cbsa, "salaries": {}}
    if cbsa in pivot.index:
        for occ in TARGET_OCC_CODES:
            val = pivot.loc[cbsa, occ] if occ in pivot.columns else None
            if pd.notna(val):
                cities[cbsa]["salaries"][occ] = int(round(val / 100) * 100)

print(f"  ✓ Loaded salaries for {len(cities)} cities")

# ── STEP 2: ZILLOW RENT ──────────────────────────────────────────────────────

print("Step 2: Loading Zillow rent data...")
zori_url = "https://files.zillowstatic.com/research/public_csvs/zori/Metro_ZORI_AllHomesPlusMultifamily_SSA.csv"
try:
    r = requests.get(zori_url, timeout=15)
    zori = pd.read_csv(io.StringIO(r.text))
except Exception as e:
    print(f"  Download failed: {e}. Loading from data/raw/zillow/metro_zori.csv")
    zori = pd.read_csv("data/raw/zillow/metro_zori.csv")

date_cols = [c for c in zori.columns if c[:4].isdigit()]
latest_col = sorted(date_cols)[-1]
print(f"  Using Zillow data from: {latest_col}")
zori_lookup = {row["RegionName"]: round((row[latest_col] * 12) / 100) * 100
               for _, row in zori.iterrows() if pd.notna(row[latest_col])}

matched = 0
for cbsa, city in cities.items():
    m = process.extractOne(city["name"], list(zori_lookup.keys()), scorer=fuzz.token_sort_ratio, score_cutoff=65)
    if m:
        cities[cbsa]["medianRent1BR"] = zori_lookup[m[0]]
        matched += 1
    else:
        print(f"  WARNING: No rent match for {city['name']}")
        cities[cbsa]["medianRent1BR"] = None

print(f"  ✓ Rent matched for {matched}/{len(cities)} cities")

# ── STEP 3: TAX RATES ────────────────────────────────────────────────────────

print("Step 3: Applying tax rates...")
for cbsa, city in cities.items():
    cities[cbsa]["stateTaxRate"] = STATE_TAX_RATES.get(city["state"], 0.05)
cities["15380"]["stateTaxRate"] = 0.065  # Buffalo: NY state only, no NYC surcharge
print("  ✓ Tax rates applied")

# ── STEP 4: COST OF LIVING INDEX ─────────────────────────────────────────────

print("Step 4: Loading cost of living index...")
try:
    r = requests.get("https://www.numbeo.com/api/indices?api_key=free&country=United+States", timeout=10)
    items = r.json().get("response", [])
    numbeo_lookup = {i["city"]: round(i["cost_of_living_index"] * NUMBEO_RESCALE_FACTOR)
                     for i in items if "cost_of_living_index" in i}
    print(f"  Numbeo API returned {len(numbeo_lookup)} cities")
except Exception as e:
    print(f"  Numbeo API failed: {e}. Load from CSV.")
    ndf = pd.read_csv("data/raw/numbeo/us_col_index.csv")
    numbeo_lookup = {row["city"]: round(row["col_index"] * NUMBEO_RESCALE_FACTOR) for _, row in ndf.iterrows()}

matched_col = 0
for cbsa, city in cities.items():
    m = process.extractOne(city["name"], list(numbeo_lookup.keys()), scorer=fuzz.token_sort_ratio, score_cutoff=60)
    if m:
        cities[cbsa]["colIndex"] = int(numbeo_lookup[m[0]])
        matched_col += 1
    else:
        print(f"  WARNING: No CoL index for {city['name']} — defaulting to 100")
        cities[cbsa]["colIndex"] = 100

print(f"  ✓ CoL index matched for {matched_col}/{len(cities)} cities")

# ── STEP 5: CLEANUP & OUTPUT ─────────────────────────────────────────────────

print("Step 5: Cleaning and writing output...")

# Drop cities missing critical fields
output = []
skipped = []
for cbsa, city in cities.items():
    missing_salary_count = sum(1 for occ in TARGET_OCC_CODES if occ not in city["salaries"])
    if city.get("medianRent1BR") is None:
        skipped.append((city["name"], "missing rent"))
        continue
    if missing_salary_count > 5:
        skipped.append((city["name"], f"missing {missing_salary_count} salary fields"))
        continue
    output.append(city)

for name, reason in skipped:
    print(f"  DROPPED: {name} — {reason}")

# Sort by city name for consistent output
output.sort(key=lambda x: x["name"])

with open("public/data/cities.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ cities.json written: {len(output)} cities")
print(f"  Dropped: {len(skipped)} cities")
```

---

## SECTION 7: VALIDATION RULES

After running the pipeline, validate cities.json against these expected values.
If any check fails, the data is wrong — do not proceed to building the app.

```python
import json

with open("public/data/cities.json") as f:
    cities = {c["id"]: c for c in json.load(f)}

errors = []

def check(condition, message):
    if not condition:
        errors.append(f"FAIL: {message}")

# ── Count checks
check(len(cities) >= 45, f"Expected >= 45 cities, got {len(cities)}")

# ── San Francisco spot checks
sf = cities.get("41860", {})
check(sf.get("state") == "CA", "SF state should be CA")
check(sf.get("region") == "West", "SF region should be West")
check(sf.get("stateTaxRate") == 0.093, f"SF tax rate should be 0.093, got {sf.get('stateTaxRate')}")
check(20000 <= sf.get("medianRent1BR", 0) <= 35000, f"SF rent out of range: {sf.get('medianRent1BR')}")
check(140 <= sf.get("colIndex", 0) <= 220, f"SF colIndex out of range: {sf.get('colIndex')}")
check(130000 <= sf.get("salaries", {}).get("15-1252", 0) <= 200000, "SF software dev salary out of range")

# ── Dallas spot checks (no-tax state)
dal = cities.get("19100", {})
check(dal.get("stateTaxRate") == 0.0, f"Dallas tax rate should be 0, got {dal.get('stateTaxRate')}")
check(12000 <= dal.get("medianRent1BR", 0) <= 22000, f"Dallas rent out of range: {dal.get('medianRent1BR')}")
check(95 <= dal.get("colIndex", 0) <= 120, f"Dallas colIndex out of range: {dal.get('colIndex')}")

# ── NYC spot checks (high tax with city surcharge)
nyc = cities.get("35620", {})
check(nyc.get("stateTaxRate") >= 0.10, f"NYC tax rate should be >= 0.10, got {nyc.get('stateTaxRate')}")
check(22000 <= nyc.get("medianRent1BR", 0) <= 38000, f"NYC rent out of range: {nyc.get('medianRent1BR')}")

# ── No-tax states have 0.0 rate
for cbsa, city in cities.items():
    if city["state"] in ["TX", "FL", "WA", "NV"]:
        check(city["stateTaxRate"] == 0.0, f"{city['name']} should have 0 tax rate")

# ── Every city has at least 10 of 15 occupation salaries
for cbsa, city in cities.items():
    count = len(city.get("salaries", {}))
    check(count >= 10, f"{city['name']} only has {count} occupation salaries (need >= 10)")

# ── Report
if errors:
    print("\n❌ VALIDATION FAILED:")
    for e in errors:
        print(f"   {e}")
else:
    print(f"\n✅ All validation checks passed. {len(cities)} cities ready.")
```

---

## SECTION 8: FALLBACK DATA

If network access is unavailable and the pipeline cannot run,
use the hardcoded 10-city seed from agent-build-spec.md Section 3.3.

The seed data in agent-build-spec.md is the single source of truth for the fallback.
Do not invent or estimate data values beyond what is in that seed.

The app will function correctly with 10 cities.
Display a banner: "Preview mode — full 50-city dataset requires data pipeline."

---

## END OF DATA ACQUISITION SPEC

Pipeline execution order:
1. Download all raw files (Sections 1.1, 2.1, 4)
2. Run: python scripts/build-data.py
3. Run validation (Section 7)
4. If validation passes: proceed to app build
5. If validation fails: diagnose using section-specific extraction scripts
```