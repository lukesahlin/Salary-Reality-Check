"""
download_data.py
Downloads all raw data needed to build public/data/cities.json and public/data/living-wage.json.
Run from project root: python scripts/download_data.py

Dependencies: pip install requests pandas openpyxl rapidfuzz beautifulsoup4 lxml

All data sources are free and require no API keys.
"""

import requests
import zipfile
import io
import os
import json
import time
import pandas as pd
from rapidfuzz import process, fuzz

# ── DIRECTORY SETUP ───────────────────────────────────────────────────────────

DIRS = [
    "data/raw/bls",
    "data/raw/zillow",
    "data/raw/numbeo",
    "data/raw/hud",
    "public/data",
    "scripts",
]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

# ── OCCUPATION CODES (BLS SOC) ────────────────────────────────────────────────

TARGET_OCC_CODES = [
    # Tech
    "15-1252",  # Software Developer / Engineer
    "15-1211",  # Computer Systems Analyst
    "15-1244",  # Network & Computer Systems Administrator
    "15-1232",  # Computer User Support Specialist
    "15-1255",  # Web Developer
    "15-2051",  # Data Scientist
    "15-2031",  # Operations Research Analyst
    # Management & Business
    "11-1021",  # General & Operations Manager
    "11-3031",  # Financial Manager
    "11-9041",  # Architectural & Engineering Manager
    "13-1111",  # Management Analyst / Consultant
    "13-1071",  # Human Resources Specialist
    "13-1081",  # Logistician
    "13-2011",  # Accountant / Auditor
    "13-1161",  # Market Research Analyst
    "43-3031",  # Bookkeeping / Accounting Clerk
    "43-6014",  # Secretary / Administrative Assistant
    # Legal
    "23-1011",  # Lawyer / Attorney
    # Healthcare
    "29-1141",  # Registered Nurse
    "29-1071",  # Physician Assistant
    "29-2061",  # Licensed Practical / Vocational Nurse
    "29-1051",  # Pharmacist
    "29-2034",  # Radiologic Technologist
    "21-1014",  # Mental Health Counselor
    # Engineering
    "17-2141",  # Mechanical Engineer
    "17-2051",  # Civil Engineer
    "17-2071",  # Electrical Engineer
    "17-2112",  # Industrial Engineer
    # Education
    "25-2021",  # Elementary School Teacher
    "25-1099",  # Postsecondary Teacher (College Professor)
    # Trades & Services
    "47-2111",  # Electrician
    "47-2152",  # Plumber / Pipefitter
    "33-3051",  # Police / Sheriff's Patrol Officer
    # Creative & Other
    "27-1024",  # Graphic Designer
    "35-1012",  # Food Service Manager
    "41-2031",  # Retail Sales Worker
]

# ── TARGET CITIES (CBSA codes) ────────────────────────────────────────────────

TARGET_CBSA_CODES = {
    # ── South ────────────────────────────────────────────────────────────────
    "12060": {"name": "Atlanta, GA",          "short": "ATL", "state": "GA", "region": "South"},
    "12420": {"name": "Austin, TX",           "short": "AUS", "state": "TX", "region": "South"},
    "13820": {"name": "Birmingham, AL",       "short": "BHM", "state": "AL", "region": "South"},
    "12940": {"name": "Baton Rouge, LA",      "short": "BTR", "state": "LA", "region": "South"},
    "16700": {"name": "Charleston, SC",       "short": "CHS", "state": "SC", "region": "South"},
    "16740": {"name": "Charlotte, NC",        "short": "CLT", "state": "NC", "region": "South"},
    "16860": {"name": "Chattanooga, TN",      "short": "CHA", "state": "TN", "region": "South"},
    "17900": {"name": "Columbia, SC",         "short": "CAE", "state": "SC", "region": "South"},
    "19100": {"name": "Dallas, TX",           "short": "DAL", "state": "TX", "region": "South"},
    "21340": {"name": "El Paso, TX",          "short": "ELP", "state": "TX", "region": "South"},
    "24660": {"name": "Greensboro, NC",       "short": "GSO", "state": "NC", "region": "South"},
    "24860": {"name": "Greenville, SC",       "short": "GSP", "state": "SC", "region": "South"},
    "26420": {"name": "Houston, TX",          "short": "HOU", "state": "TX", "region": "South"},
    "26620": {"name": "Huntsville, AL",       "short": "HSV", "state": "AL", "region": "South"},
    "27260": {"name": "Jacksonville, FL",     "short": "JAX", "state": "FL", "region": "South"},
    "28140": {"name": "Kansas City, MO",      "short": "MCI", "state": "MO", "region": "South"},
    "28940": {"name": "Knoxville, TN",        "short": "TYS", "state": "TN", "region": "South"},
    "30780": {"name": "Little Rock, AR",      "short": "LIT", "state": "AR", "region": "South"},
    "31140": {"name": "Louisville, KY",       "short": "SDF", "state": "KY", "region": "South"},
    "32820": {"name": "Memphis, TN",          "short": "MEM", "state": "TN", "region": "South"},
    "33100": {"name": "Miami, FL",            "short": "MIA", "state": "FL", "region": "South"},
    "15980": {"name": "Cape Coral, FL",       "short": "RSW", "state": "FL", "region": "South"},
    "34980": {"name": "Nashville, TN",        "short": "BNA", "state": "TN", "region": "South"},
    "35380": {"name": "New Orleans, LA",      "short": "MSY", "state": "LA", "region": "South"},
    "36420": {"name": "Oklahoma City, OK",    "short": "OKC", "state": "OK", "region": "South"},
    "36740": {"name": "Orlando, FL",          "short": "MCO", "state": "FL", "region": "South"},
    "39580": {"name": "Raleigh, NC",          "short": "RDU", "state": "NC", "region": "South"},
    "40060": {"name": "Richmond, VA",         "short": "RIC", "state": "VA", "region": "South"},
    "41700": {"name": "San Antonio, TX",      "short": "SAT", "state": "TX", "region": "South"},
    "45300": {"name": "Tampa, FL",            "short": "TPA", "state": "FL", "region": "South"},
    "47260": {"name": "Virginia Beach, VA",   "short": "ORF", "state": "VA", "region": "South"},
    "49180": {"name": "Winston-Salem, NC",    "short": "INT", "state": "NC", "region": "South"},
    # ── Northeast ────────────────────────────────────────────────────────────
    "12580": {"name": "Baltimore, MD",        "short": "BAL", "state": "MD", "region": "Northeast"},
    "14460": {"name": "Boston, MA",           "short": "BOS", "state": "MA", "region": "Northeast"},
    "15380": {"name": "Buffalo, NY",          "short": "BUF", "state": "NY", "region": "Northeast"},
    "25420": {"name": "Harrisburg, PA",       "short": "MDT", "state": "PA", "region": "Northeast"},
    "25540": {"name": "Hartford, CT",         "short": "HFD", "state": "CT", "region": "Northeast"},
    "35300": {"name": "New Haven, CT",        "short": "HVN", "state": "CT", "region": "Northeast"},
    "35620": {"name": "New York, NY",         "short": "NYC", "state": "NY", "region": "Northeast"},
    "37980": {"name": "Philadelphia, PA",     "short": "PHL", "state": "PA", "region": "Northeast"},
    "38300": {"name": "Pittsburgh, PA",       "short": "PIT", "state": "PA", "region": "Northeast"},
    "39300": {"name": "Providence, RI",       "short": "PVD", "state": "RI", "region": "Northeast"},
    "40380": {"name": "Rochester, NY",        "short": "ROC", "state": "NY", "region": "Northeast"},
    "47900": {"name": "Washington, DC",       "short": "DC",  "state": "DC", "region": "Northeast"},
    # ── Midwest ──────────────────────────────────────────────────────────────
    "10420": {"name": "Akron, OH",            "short": "CAK", "state": "OH", "region": "Midwest"},
    "16980": {"name": "Chicago, IL",          "short": "CHI", "state": "IL", "region": "Midwest"},
    "17140": {"name": "Cincinnati, OH",       "short": "CIN", "state": "OH", "region": "Midwest"},
    "17460": {"name": "Cleveland, OH",        "short": "CLE", "state": "OH", "region": "Midwest"},
    "18140": {"name": "Columbus, OH",         "short": "CMH", "state": "OH", "region": "Midwest"},
    "19430": {"name": "Dayton, OH",           "short": "DAY", "state": "OH", "region": "Midwest"},
    "19780": {"name": "Des Moines, IA",       "short": "DSM", "state": "IA", "region": "Midwest"},
    "19820": {"name": "Detroit, MI",          "short": "DET", "state": "MI", "region": "Midwest"},
    "24340": {"name": "Grand Rapids, MI",     "short": "GRR", "state": "MI", "region": "Midwest"},
    "26900": {"name": "Indianapolis, IN",     "short": "IND", "state": "IN", "region": "Midwest"},
    "31540": {"name": "Madison, WI",          "short": "MSN", "state": "WI", "region": "Midwest"},
    "33340": {"name": "Milwaukee, WI",        "short": "MKE", "state": "WI", "region": "Midwest"},
    "33460": {"name": "Minneapolis, MN",      "short": "MSP", "state": "MN", "region": "Midwest"},
    "36540": {"name": "Omaha, NE",            "short": "OMA", "state": "NE", "region": "Midwest"},
    "41180": {"name": "St. Louis, MO",        "short": "STL", "state": "MO", "region": "Midwest"},
    "48620": {"name": "Wichita, KS",          "short": "ICT", "state": "KS", "region": "Midwest"},
    # ── West ─────────────────────────────────────────────────────────────────
    "10740": {"name": "Albuquerque, NM",      "short": "ABQ", "state": "NM", "region": "West"},
    "14260": {"name": "Boise, ID",            "short": "BOI", "state": "ID", "region": "West"},
    "17820": {"name": "Colorado Springs, CO", "short": "COS", "state": "CO", "region": "West"},
    "19740": {"name": "Denver, CO",           "short": "DEN", "state": "CO", "region": "West"},
    "23420": {"name": "Fresno, CA",           "short": "FAT", "state": "CA", "region": "West"},
    "29820": {"name": "Las Vegas, NV",        "short": "LAS", "state": "NV", "region": "West"},
    "31080": {"name": "Los Angeles, CA",      "short": "LAX", "state": "CA", "region": "West"},
    "32580": {"name": "McAllen, TX",          "short": "MFE", "state": "TX", "region": "West"},
    "36260": {"name": "Ogden, UT",            "short": "OGD", "state": "UT", "region": "West"},
    "38060": {"name": "Phoenix, AZ",          "short": "PHX", "state": "AZ", "region": "West"},
    "38900": {"name": "Portland, OR",         "short": "PDX", "state": "OR", "region": "West"},
    "39340": {"name": "Provo, UT",            "short": "PVU", "state": "UT", "region": "West"},
    "40140": {"name": "Riverside, CA",        "short": "RIV", "state": "CA", "region": "West"},
    "40900": {"name": "Sacramento, CA",       "short": "SMF", "state": "CA", "region": "West"},
    "41620": {"name": "Salt Lake City, UT",   "short": "SLC", "state": "UT", "region": "West"},
    "41740": {"name": "San Diego, CA",        "short": "SAN", "state": "CA", "region": "West"},
    "41860": {"name": "San Francisco, CA",    "short": "SF",  "state": "CA", "region": "West"},
    "41940": {"name": "San Jose, CA",         "short": "SJC", "state": "CA", "region": "West"},
    "42660": {"name": "Seattle, WA",          "short": "SEA", "state": "WA", "region": "West"},
    "44060": {"name": "Spokane, WA",          "short": "GEG", "state": "WA", "region": "West"},
    "44700": {"name": "Stockton, CA",         "short": "SCK", "state": "CA", "region": "West"},
    "46060": {"name": "Tucson, AZ",           "short": "TUS", "state": "AZ", "region": "West"},
    "46140": {"name": "Tulsa, OK",            "short": "TUL", "state": "OK", "region": "West"},
}

# ── STATE TAX RATES (Tax Foundation 2024, effective top marginal) ─────────────

STATE_TAX_RATES = {
    "TX": 0.0000, "FL": 0.0000, "NV": 0.0000, "WA": 0.0000,
    "SD": 0.0000, "WY": 0.0000, "AK": 0.0000, "TN": 0.0000, "NH": 0.0000,
    "PA": 0.0307, "IN": 0.0323, "AZ": 0.0250, "CO": 0.0440, "MI": 0.0425,
    "UT": 0.0455, "OH": 0.0400, "GA": 0.0550, "AL": 0.0500, "LA": 0.0430,
    "OK": 0.0490, "KS": 0.0570, "MO": 0.0540, "SC": 0.0650, "NC": 0.0475,
    "VA": 0.0575, "MA": 0.0500, "KY": 0.0450, "RI": 0.0599, "WI": 0.0530,
    "IL": 0.0495, "IA": 0.0570, "MD": 0.0750, "CT": 0.0699, "DC": 0.0850,
    "NJ": 0.0637, "MN": 0.0785, "VT": 0.0870, "OR": 0.0990, "CA": 0.0930,
    "NY": 0.1080, "NM": 0.0590, "ID": 0.0580, "AR": 0.0490, "NE": 0.0684,
    "DE": 0.0660, "MT": 0.0675, "ME": 0.0715, "HI": 0.1100,
}

# ── BLS AREA CODE OVERRIDES (BLS uses different codes for some metros) ────────

BLS_AREA_OVERRIDES = {
    "17460": "17410",  # Cleveland-Elyria, OH
    "32580": "32580",  # McAllen — verify if needed
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# ── SECTION 1: BLS OEWS ───────────────────────────────────────────────────────

def download_bls():
    """Download BLS OEWS bulk ZIP and extract the metro salary Excel file."""
    xlsx_path = "data/raw/bls/MSA_M2024_dl.xlsx"
    if os.path.exists(xlsx_path):
        print("  [BLS] MSA_M2024_dl.xlsx already exists, skipping download.")
        return

    url = "https://www.bls.gov/oes/special.requests/oesm24ma.zip"
    print(f"  [BLS] Downloading {url} (~50 MB) ...")
    r = requests.get(url, headers=HEADERS, timeout=120)
    r.raise_for_status()

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("data/raw/bls/")
    print("  [BLS] Extracted to data/raw/bls/")

    if not os.path.exists(xlsx_path):
        for root, _, files in os.walk("data/raw/bls/"):
            for f in files:
                if f == "MSA_M2024_dl.xlsx":
                    src = os.path.join(root, f)
                    os.rename(src, xlsx_path)
                    print(f"  [BLS] Moved {src} -> {xlsx_path}")
                    break

    print("  [BLS] Done.")


def load_bls_salaries():
    """Parse BLS Excel and return pivot: {cbsa: {occ_code: wage}}"""
    print("  [BLS] Reading MSA_M2024_dl.xlsx ...")
    df = pd.read_excel(
        "data/raw/bls/MSA_M2024_dl.xlsx",
        dtype={"AREA": str, "OCC_CODE": str},
    )

    bls_to_cbsa = {v: k for k, v in BLS_AREA_OVERRIDES.items()}
    all_bls_codes = set(TARGET_CBSA_CODES.keys()) - set(BLS_AREA_OVERRIDES.keys())
    for code in all_bls_codes:
        bls_to_cbsa[code] = code
    filter_codes = all_bls_codes | set(BLS_AREA_OVERRIDES.values())

    df = df[df["AREA"].isin(filter_codes)]
    df = df[df["OCC_CODE"].isin(TARGET_OCC_CODES)]

    df = df.copy()
    df["AREA"] = df["AREA"].map(lambda x: bls_to_cbsa.get(x, x))

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

    print(f"  [BLS] Salary data loaded for {len(cities)} cities.")
    return cities


# ── SECTION 2: ZILLOW ZORI (rent) ────────────────────────────────────────────

def download_zillow_zori():
    """Download Zillow ZORI metro rent CSV."""
    csv_path = "data/raw/zillow/metro_zori.csv"
    if os.path.exists(csv_path):
        print("  [Zillow ZORI] metro_zori.csv already exists, skipping.")
        return

    url = "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv"
    print(f"  [Zillow ZORI] Downloading {url} ...")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(r.text)
    print("  [Zillow ZORI] Saved.")


def load_zillow_rents(cities: dict) -> dict:
    """Read ZORI CSV and fuzzy-match annual rents onto the cities dict."""
    zori = pd.read_csv("data/raw/zillow/metro_zori.csv")
    date_cols = [c for c in zori.columns if c[:4].isdigit()]
    latest_col = sorted(date_cols)[-1]
    print(f"  [Zillow ZORI] Using column: {latest_col}")

    zori_lookup = {
        row["RegionName"]: round((row[latest_col] * 12) / 100) * 100
        for _, row in zori.iterrows()
        if pd.notna(row[latest_col])
    }

    matched = 0
    for cbsa, city in cities.items():
        m = process.extractOne(
            city["name"],
            list(zori_lookup.keys()),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=65,
        )
        if m:
            cities[cbsa]["medianRent1BR"] = zori_lookup[m[0]]
            matched += 1
        else:
            print(f"  [Zillow ZORI] WARNING: No rent match for {city['name']}")
            cities[cbsa]["medianRent1BR"] = None

    print(f"  [Zillow ZORI] Rent matched for {matched}/{len(cities)} cities.")
    return cities


# ── SECTION 3: ZILLOW ZHVI (home prices) ─────────────────────────────────────

def download_zillow_zhvi():
    """Download Zillow ZHVI metro home value index CSV."""
    csv_path = "data/raw/zillow/metro_zhvi.csv"
    if os.path.exists(csv_path):
        print("  [Zillow ZHVI] metro_zhvi.csv already exists, skipping.")
        return

    url = "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
    print(f"  [Zillow ZHVI] Downloading {url} ...")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(r.text)
    print("  [Zillow ZHVI] Saved.")


def load_zhvi_home_prices(cities: dict) -> dict:
    """Read ZHVI CSV and fuzzy-match median home prices onto the cities dict."""
    zhvi = pd.read_csv("data/raw/zillow/metro_zhvi.csv")
    date_cols = [c for c in zhvi.columns if c[:4].isdigit()]
    latest_col = sorted(date_cols)[-1]
    print(f"  [Zillow ZHVI] Using column: {latest_col}")

    zhvi_lookup = {
        row["RegionName"]: int(round(row[latest_col] / 1000) * 1000)
        for _, row in zhvi.iterrows()
        if pd.notna(row[latest_col])
    }

    matched = 0
    for cbsa, city in cities.items():
        m = process.extractOne(
            city["name"],
            list(zhvi_lookup.keys()),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=65,
        )
        if m:
            cities[cbsa]["medianHomePrice"] = zhvi_lookup[m[0]]
            matched += 1
        else:
            print(f"  [Zillow ZHVI] WARNING: No home price match for {city['name']}")
            # Fall back to hardcoded value if available
            if cbsa in SUPPLEMENTAL_DATA and "medianHomePrice" in SUPPLEMENTAL_DATA[cbsa]:
                cities[cbsa]["medianHomePrice"] = SUPPLEMENTAL_DATA[cbsa]["medianHomePrice"]
            else:
                cities[cbsa]["medianHomePrice"] = None

    print(f"  [Zillow ZHVI] Home prices matched for {matched}/{len(cities)} cities.")
    return cities


# ── SECTION 4: TAX RATES ──────────────────────────────────────────────────────

def apply_tax_rates(cities: dict) -> dict:
    """Apply hardcoded state and local tax rates."""
    for cbsa, city in cities.items():
        cities[cbsa]["stateTaxRate"] = STATE_TAX_RATES.get(city["state"], 0.05)
    # Buffalo: NY state rate only, no NYC surcharge
    if "15380" in cities:
        cities["15380"]["stateTaxRate"] = 0.0650
    print("  [Tax] State tax rates applied.")
    return cities


# ── SECTION 5: COST OF LIVING INDEX (Numbeo 2024 / ACCRA-indexed) ────────────

COL_INDEX_BY_CBSA = {
    # ── South ─────────────────────────────────────────────────────────────────
    "12060": 108,  # Atlanta, GA
    "12420": 112,  # Austin, TX
    "12940":  88,  # Baton Rouge, LA
    "13820":  88,  # Birmingham, AL
    "15980":  98,  # Cape Coral, FL
    "16700": 108,  # Charleston, SC
    "16740": 105,  # Charlotte, NC
    "16860":  91,  # Chattanooga, TN
    "17900":  92,  # Columbia, SC
    "19100": 106,  # Dallas, TX
    "21340":  86,  # El Paso, TX
    "24660":  94,  # Greensboro, NC
    "24860":  91,  # Greenville, SC
    "26420": 101,  # Houston, TX
    "26620":  91,  # Huntsville, AL
    "27260":  96,  # Jacksonville, FL
    "28140":  95,  # Kansas City, MO
    "28940":  89,  # Knoxville, TN
    "30780":  86,  # Little Rock, AR
    "31140":  90,  # Louisville, KY
    "32820":  87,  # Memphis, TN
    "33100": 130,  # Miami, FL
    "34980": 110,  # Nashville, TN
    "35380":  91,  # New Orleans, LA
    "36420":  88,  # Oklahoma City, OK
    "36740":  98,  # Orlando, FL
    "39580": 108,  # Raleigh, NC
    "40060": 100,  # Richmond, VA
    "41700":  88,  # San Antonio, TX
    "45300": 100,  # Tampa, FL
    "47260":  97,  # Virginia Beach, VA
    "49180":  90,  # Winston-Salem, NC
    # ── Northeast ─────────────────────────────────────────────────────────────
    "12580": 118,  # Baltimore, MD
    "14460": 150,  # Boston, MA
    "15380":  93,  # Buffalo, NY
    "25420":  96,  # Harrisburg, PA
    "25540": 115,  # Hartford, CT
    "35300": 118,  # New Haven, CT
    "35620": 187,  # New York, NY
    "37980": 118,  # Philadelphia, PA
    "38300":  95,  # Pittsburgh, PA
    "39300": 115,  # Providence, RI
    "40380":  95,  # Rochester, NY
    "47900": 152,  # Washington, DC
    # ── Midwest ───────────────────────────────────────────────────────────────
    "10420":  88,  # Akron, OH
    "16980": 116,  # Chicago, IL
    "17140":  93,  # Cincinnati, OH
    "17460":  91,  # Cleveland, OH
    "18140":  95,  # Columbus, OH
    "19430":  87,  # Dayton, OH
    "19780":  91,  # Des Moines, IA
    "19820":  91,  # Detroit, MI
    "24340":  93,  # Grand Rapids, MI
    "26900":  94,  # Indianapolis, IN
    "31540": 102,  # Madison, WI
    "33340":  97,  # Milwaukee, WI
    "33460": 112,  # Minneapolis, MN
    "36540":  90,  # Omaha, NE
    "41180":  96,  # St. Louis, MO
    "48620":  86,  # Wichita, KS
    # ── West ──────────────────────────────────────────────────────────────────
    "10740":  94,  # Albuquerque, NM
    "14260": 103,  # Boise, ID
    "17820": 103,  # Colorado Springs, CO
    "19740": 135,  # Denver, CO
    "23420":  97,  # Fresno, CA
    "29820": 104,  # Las Vegas, NV
    "31080": 155,  # Los Angeles, CA
    "32580":  79,  # McAllen, TX
    "36260":  95,  # Ogden, UT
    "38060": 103,  # Phoenix, AZ
    "38900": 130,  # Portland, OR
    "39340":  95,  # Provo, UT
    "40140": 120,  # Riverside, CA
    "40900": 125,  # Sacramento, CA
    "41620": 105,  # Salt Lake City, UT
    "41740": 145,  # San Diego, CA
    "41860": 178,  # San Francisco, CA
    "41940": 185,  # San Jose, CA
    "42660": 147,  # Seattle, WA
    "44060":  95,  # Spokane, WA
    "44700": 105,  # Stockton, CA
    "46060":  92,  # Tucson, AZ
    "46140":  88,  # Tulsa, OK
}


def load_col_index(cities: dict) -> dict:
    for cbsa, city in cities.items():
        if cbsa in COL_INDEX_BY_CBSA:
            cities[cbsa]["colIndex"] = COL_INDEX_BY_CBSA[cbsa]
        else:
            print(f"  [CoL] WARNING: No CoL index for {city['name']} ({cbsa}) — defaulting 100")
            cities[cbsa]["colIndex"] = 100
    print(f"  [CoL] Applied for {len(COL_INDEX_BY_CBSA)} cities.")
    return cities


# ── SECTION 6: SUPPLEMENTAL DATA (hardcoded from public sources) ──────────────
#
# Sources:
#   walkScore / transitScore  — Walk Score 2024 metro averages
#   crimeIndex                — FBI UCR / local police data, 100 = national avg
#   unemploymentRate          — BLS LAUS 2024 annual avg (%)
#   jobGrowthRate             — BLS QCEW 2023→2024 % employment change
#   avgBenefitsValue          — BLS ECI employer benefits estimate ($)
#   sunDaysPerYear            — NOAA 30-year climate normals
#   populationM               — Census 2023 metro estimates (millions)
#   popGrowthRate             — % change 2019→2024
#   localTaxRate              — City/county income or wage tax (0 if none)

SUPPLEMENTAL_DATA = {
    # South
    "12060": {"walkScore":48,"transitScore":42,"crimeIndex":72,"unemploymentRate":3.6,"jobGrowthRate":2.8,"avgBenefitsValue":15200,"sunDaysPerYear":217,"populationM":6.30,"popGrowthRate":16.8,"localTaxRate":0.000,"medianHomePrice":385000},
    "12420": {"walkScore":40,"transitScore":33,"crimeIndex":52,"unemploymentRate":3.2,"jobGrowthRate":3.5,"avgBenefitsValue":14800,"sunDaysPerYear":228,"populationM":2.30,"popGrowthRate":29.7,"localTaxRate":0.000,"medianHomePrice":530000},
    "12940": {"walkScore":33,"transitScore":20,"crimeIndex":72,"unemploymentRate":4.2,"jobGrowthRate":1.5,"avgBenefitsValue":14200,"sunDaysPerYear":228,"populationM":0.87,"popGrowthRate": 2.1,"localTaxRate":0.000,"medianHomePrice":245000},
    "13820": {"walkScore":32,"transitScore":22,"crimeIndex":78,"unemploymentRate":3.9,"jobGrowthRate":1.2,"avgBenefitsValue":14200,"sunDaysPerYear":211,"populationM":1.10,"popGrowthRate": 2.5,"localTaxRate":0.000,"medianHomePrice":235000},
    "15980": {"walkScore":30,"transitScore":15,"crimeIndex":28,"unemploymentRate":4.0,"jobGrowthRate":3.5,"avgBenefitsValue":14000,"sunDaysPerYear":271,"populationM":0.77,"popGrowthRate":22.5,"localTaxRate":0.000,"medianHomePrice":380000},
    "16700": {"walkScore":52,"transitScore":22,"crimeIndex":45,"unemploymentRate":3.5,"jobGrowthRate":3.2,"avgBenefitsValue":14800,"sunDaysPerYear":228,"populationM":0.80,"popGrowthRate":18.6,"localTaxRate":0.000,"medianHomePrice":410000},
    "16740": {"walkScore":28,"transitScore":22,"crimeIndex":55,"unemploymentRate":3.4,"jobGrowthRate":3.2,"avgBenefitsValue":15500,"sunDaysPerYear":213,"populationM":2.70,"popGrowthRate":21.3,"localTaxRate":0.000,"medianHomePrice":415000},
    "16860": {"walkScore":38,"transitScore":22,"crimeIndex":52,"unemploymentRate":3.8,"jobGrowthRate":2.0,"avgBenefitsValue":14200,"sunDaysPerYear":204,"populationM":0.58,"popGrowthRate": 9.3,"localTaxRate":0.000,"medianHomePrice":310000},
    "17900": {"walkScore":37,"transitScore":20,"crimeIndex":60,"unemploymentRate":3.8,"jobGrowthRate":1.8,"avgBenefitsValue":14200,"sunDaysPerYear":213,"populationM":0.84,"popGrowthRate": 9.8,"localTaxRate":0.000,"medianHomePrice":265000},
    "19100": {"walkScore":38,"transitScore":35,"crimeIndex":62,"unemploymentRate":3.8,"jobGrowthRate":2.5,"avgBenefitsValue":15800,"sunDaysPerYear":234,"populationM":7.60,"popGrowthRate":20.5,"localTaxRate":0.000,"medianHomePrice":385000},
    "21340": {"walkScore":38,"transitScore":25,"crimeIndex":42,"unemploymentRate":4.2,"jobGrowthRate":1.8,"avgBenefitsValue":13800,"sunDaysPerYear":297,"populationM":0.87,"popGrowthRate": 5.5,"localTaxRate":0.000,"medianHomePrice":240000},
    "24660": {"walkScore":38,"transitScore":22,"crimeIndex":55,"unemploymentRate":3.8,"jobGrowthRate":2.0,"avgBenefitsValue":14800,"sunDaysPerYear":213,"populationM":0.77,"popGrowthRate": 7.5,"localTaxRate":0.000,"medianHomePrice":310000},
    "24860": {"walkScore":33,"transitScore":17,"crimeIndex":45,"unemploymentRate":3.5,"jobGrowthRate":2.8,"avgBenefitsValue":14200,"sunDaysPerYear":217,"populationM":0.93,"popGrowthRate":15.2,"localTaxRate":0.000,"medianHomePrice":305000},
    "26420": {"walkScore":47,"transitScore":38,"crimeIndex":68,"unemploymentRate":4.2,"jobGrowthRate":2.8,"avgBenefitsValue":15500,"sunDaysPerYear":204,"populationM":7.30,"popGrowthRate":16.5,"localTaxRate":0.000,"medianHomePrice":310000},
    "26620": {"walkScore":32,"transitScore":17,"crimeIndex":33,"unemploymentRate":3.2,"jobGrowthRate":2.8,"avgBenefitsValue":14500,"sunDaysPerYear":204,"populationM":0.49,"popGrowthRate":12.4,"localTaxRate":0.000,"medianHomePrice":330000},
    "27260": {"walkScore":28,"transitScore":18,"crimeIndex":62,"unemploymentRate":3.5,"jobGrowthRate":2.5,"avgBenefitsValue":14500,"sunDaysPerYear":237,"populationM":1.60,"popGrowthRate":15.8,"localTaxRate":0.000,"medianHomePrice":320000},
    "28140": {"walkScore":37,"transitScore":28,"crimeIndex":68,"unemploymentRate":3.5,"jobGrowthRate":1.8,"avgBenefitsValue":15200,"sunDaysPerYear":215,"populationM":2.20,"popGrowthRate": 7.5,"localTaxRate":0.010,"medianHomePrice":285000},
    "28940": {"walkScore":36,"transitScore":18,"crimeIndex":45,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":14200,"sunDaysPerYear":204,"populationM":0.87,"popGrowthRate": 9.5,"localTaxRate":0.000,"medianHomePrice":340000},
    "30780": {"walkScore":37,"transitScore":18,"crimeIndex":68,"unemploymentRate":3.8,"jobGrowthRate":1.5,"avgBenefitsValue":13800,"sunDaysPerYear":217,"populationM":0.74,"popGrowthRate": 4.5,"localTaxRate":0.000,"medianHomePrice":235000},
    "31140": {"walkScore":42,"transitScore":30,"crimeIndex":62,"unemploymentRate":3.8,"jobGrowthRate":1.5,"avgBenefitsValue":14800,"sunDaysPerYear":201,"populationM":1.40,"popGrowthRate": 4.2,"localTaxRate":0.022,"medianHomePrice":255000},
    "32820": {"walkScore":35,"transitScore":27,"crimeIndex":85,"unemploymentRate":4.5,"jobGrowthRate":1.2,"avgBenefitsValue":14200,"sunDaysPerYear":217,"populationM":1.40,"popGrowthRate": 0.8,"localTaxRate":0.000,"medianHomePrice":195000},
    "33100": {"walkScore":77,"transitScore":60,"crimeIndex":65,"unemploymentRate":3.8,"jobGrowthRate":2.2,"avgBenefitsValue":16800,"sunDaysPerYear":248,"populationM":6.20,"popGrowthRate":11.8,"localTaxRate":0.000,"medianHomePrice":610000},
    "34980": {"walkScore":28,"transitScore":22,"crimeIndex":62,"unemploymentRate":3.2,"jobGrowthRate":3.0,"avgBenefitsValue":15800,"sunDaysPerYear":208,"populationM":2.10,"popGrowthRate":21.8,"localTaxRate":0.000,"medianHomePrice":460000},
    "35380": {"walkScore":60,"transitScore":45,"crimeIndex":88,"unemploymentRate":4.5,"jobGrowthRate":1.2,"avgBenefitsValue":14500,"sunDaysPerYear":204,"populationM":1.30,"popGrowthRate":-3.2,"localTaxRate":0.000,"medianHomePrice":250000},
    "36420": {"walkScore":32,"transitScore":20,"crimeIndex":65,"unemploymentRate":3.5,"jobGrowthRate":1.8,"avgBenefitsValue":14500,"sunDaysPerYear":218,"populationM":1.40,"popGrowthRate": 8.5,"localTaxRate":0.000,"medianHomePrice":250000},
    "36740": {"walkScore":42,"transitScore":28,"crimeIndex":62,"unemploymentRate":3.5,"jobGrowthRate":3.5,"avgBenefitsValue":15000,"sunDaysPerYear":237,"populationM":2.70,"popGrowthRate":22.8,"localTaxRate":0.000,"medianHomePrice":395000},
    "39580": {"walkScore":35,"transitScore":22,"crimeIndex":45,"unemploymentRate":3.5,"jobGrowthRate":3.5,"avgBenefitsValue":16000,"sunDaysPerYear":213,"populationM":1.40,"popGrowthRate":25.4,"localTaxRate":0.000,"medianHomePrice":440000},
    "40060": {"walkScore":42,"transitScore":30,"crimeIndex":55,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":15800,"sunDaysPerYear":214,"populationM":1.30,"popGrowthRate": 8.5,"localTaxRate":0.000,"medianHomePrice":360000},
    "41700": {"walkScore":37,"transitScore":30,"crimeIndex":60,"unemploymentRate":3.8,"jobGrowthRate":2.2,"avgBenefitsValue":14800,"sunDaysPerYear":220,"populationM":2.60,"popGrowthRate":13.5,"localTaxRate":0.000,"medianHomePrice":285000},
    "45300": {"walkScore":50,"transitScore":35,"crimeIndex":55,"unemploymentRate":3.5,"jobGrowthRate":3.0,"avgBenefitsValue":15500,"sunDaysPerYear":246,"populationM":3.30,"popGrowthRate":17.5,"localTaxRate":0.000,"medianHomePrice":405000},
    "47260": {"walkScore":33,"transitScore":22,"crimeIndex":33,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":15000,"sunDaysPerYear":233,"populationM":1.80,"popGrowthRate": 3.8,"localTaxRate":0.000,"medianHomePrice":340000},
    "49180": {"walkScore":35,"transitScore":17,"crimeIndex":52,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":14500,"sunDaysPerYear":213,"populationM":0.67,"popGrowthRate": 9.2,"localTaxRate":0.000,"medianHomePrice":285000},
    # Northeast
    "12580": {"walkScore":67,"transitScore":55,"crimeIndex":75,"unemploymentRate":3.8,"jobGrowthRate":1.5,"avgBenefitsValue":17500,"sunDaysPerYear":214,"populationM":2.90,"popGrowthRate": 1.8,"localTaxRate":0.032,"medianHomePrice":325000},
    "14460": {"walkScore":80,"transitScore":75,"crimeIndex":45,"unemploymentRate":3.2,"jobGrowthRate":1.8,"avgBenefitsValue":18800,"sunDaysPerYear":202,"populationM":4.90,"popGrowthRate": 3.5,"localTaxRate":0.000,"medianHomePrice":620000},
    "15380": {"walkScore":58,"transitScore":42,"crimeIndex":62,"unemploymentRate":4.2,"jobGrowthRate":1.0,"avgBenefitsValue":15800,"sunDaysPerYear":162,"populationM":1.20,"popGrowthRate": 0.5,"localTaxRate":0.000,"medianHomePrice":215000},
    "25420": {"walkScore":42,"transitScore":25,"crimeIndex":40,"unemploymentRate":3.8,"jobGrowthRate":1.5,"avgBenefitsValue":16500,"sunDaysPerYear":207,"populationM":0.62,"popGrowthRate": 3.8,"localTaxRate":0.000,"medianHomePrice":270000},
    "25540": {"walkScore":55,"transitScore":42,"crimeIndex":60,"unemploymentRate":4.2,"jobGrowthRate":0.8,"avgBenefitsValue":18500,"sunDaysPerYear":198,"populationM":1.20,"popGrowthRate":-0.8,"localTaxRate":0.000,"medianHomePrice":325000},
    "35300": {"walkScore":72,"transitScore":50,"crimeIndex":60,"unemploymentRate":4.5,"jobGrowthRate":0.8,"avgBenefitsValue":18000,"sunDaysPerYear":200,"populationM":0.56,"popGrowthRate": 0.8,"localTaxRate":0.000,"medianHomePrice":370000},
    "35620": {"walkScore":88,"transitScore":85,"crimeIndex":55,"unemploymentRate":4.8,"jobGrowthRate":1.5,"avgBenefitsValue":22000,"sunDaysPerYear":234,"populationM":20.10,"popGrowthRate": 0.2,"localTaxRate":0.035,"medianHomePrice":760000},
    "37980": {"walkScore":78,"transitScore":67,"crimeIndex":72,"unemploymentRate":4.5,"jobGrowthRate":1.2,"avgBenefitsValue":18200,"sunDaysPerYear":206,"populationM":6.20,"popGrowthRate": 1.5,"localTaxRate":0.038,"medianHomePrice":345000},
    "38300": {"walkScore":62,"transitScore":52,"crimeIndex":55,"unemploymentRate":3.8,"jobGrowthRate":1.2,"avgBenefitsValue":16500,"sunDaysPerYear":160,"populationM":2.40,"popGrowthRate": 0.8,"localTaxRate":0.030,"medianHomePrice":225000},
    "39300": {"walkScore":62,"transitScore":45,"crimeIndex":55,"unemploymentRate":4.5,"jobGrowthRate":1.2,"avgBenefitsValue":16800,"sunDaysPerYear":202,"populationM":1.60,"popGrowthRate": 2.5,"localTaxRate":0.000,"medianHomePrice":410000},
    "40380": {"walkScore":55,"transitScore":35,"crimeIndex":52,"unemploymentRate":4.2,"jobGrowthRate":0.8,"avgBenefitsValue":15800,"sunDaysPerYear":167,"populationM":1.08,"popGrowthRate": 0.5,"localTaxRate":0.000,"medianHomePrice":245000},
    "47900": {"walkScore":78,"transitScore":72,"crimeIndex":70,"unemploymentRate":4.0,"jobGrowthRate":1.5,"avgBenefitsValue":22000,"sunDaysPerYear":203,"populationM":6.40,"popGrowthRate": 5.2,"localTaxRate":0.000,"medianHomePrice":620000},
    # Midwest
    "10420": {"walkScore":42,"transitScore":22,"crimeIndex":55,"unemploymentRate":4.5,"jobGrowthRate":0.5,"avgBenefitsValue":15200,"sunDaysPerYear":166,"populationM":0.70,"popGrowthRate":-0.5,"localTaxRate":0.025,"medianHomePrice":185000},
    "16980": {"walkScore":77,"transitScore":68,"crimeIndex":68,"unemploymentRate":4.5,"jobGrowthRate":1.2,"avgBenefitsValue":17200,"sunDaysPerYear":189,"populationM":9.50,"popGrowthRate":-0.3,"localTaxRate":0.000,"medianHomePrice":340000},
    "17140": {"walkScore":52,"transitScore":38,"crimeIndex":58,"unemploymentRate":3.8,"jobGrowthRate":1.8,"avgBenefitsValue":15200,"sunDaysPerYear":186,"populationM":2.30,"popGrowthRate": 4.2,"localTaxRate":0.018,"medianHomePrice":280000},
    "17460": {"walkScore":55,"transitScore":42,"crimeIndex":72,"unemploymentRate":4.5,"jobGrowthRate":0.8,"avgBenefitsValue":15500,"sunDaysPerYear":166,"populationM":2.00,"popGrowthRate":-2.1,"localTaxRate":0.025,"medianHomePrice":195000},
    "18140": {"walkScore":42,"transitScore":32,"crimeIndex":62,"unemploymentRate":3.8,"jobGrowthRate":2.2,"avgBenefitsValue":15500,"sunDaysPerYear":183,"populationM":2.10,"popGrowthRate":11.5,"localTaxRate":0.025,"medianHomePrice":285000},
    "19430": {"walkScore":38,"transitScore":23,"crimeIndex":58,"unemploymentRate":4.0,"jobGrowthRate":0.5,"avgBenefitsValue":15000,"sunDaysPerYear":178,"populationM":0.81,"popGrowthRate": 0.5,"localTaxRate":0.025,"medianHomePrice":200000},
    "19780": {"walkScore":42,"transitScore":28,"crimeIndex":38,"unemploymentRate":3.2,"jobGrowthRate":2.2,"avgBenefitsValue":15000,"sunDaysPerYear":198,"populationM":0.70,"popGrowthRate":11.2,"localTaxRate":0.000,"medianHomePrice":270000},
    "19820": {"walkScore":55,"transitScore":38,"crimeIndex":78,"unemploymentRate":4.8,"jobGrowthRate":1.5,"avgBenefitsValue":16800,"sunDaysPerYear":183,"populationM":4.40,"popGrowthRate":-0.5,"localTaxRate":0.024,"medianHomePrice":230000},
    "24340": {"walkScore":48,"transitScore":27,"crimeIndex":45,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":15200,"sunDaysPerYear":175,"populationM":1.07,"popGrowthRate": 7.4,"localTaxRate":0.000,"medianHomePrice":275000},
    "26900": {"walkScore":33,"transitScore":25,"crimeIndex":65,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":14800,"sunDaysPerYear":187,"populationM":2.10,"popGrowthRate": 9.8,"localTaxRate":0.000,"medianHomePrice":275000},
    "31540": {"walkScore":55,"transitScore":38,"crimeIndex":32,"unemploymentRate":2.8,"jobGrowthRate":2.5,"avgBenefitsValue":16800,"sunDaysPerYear":185,"populationM":0.67,"popGrowthRate": 8.1,"localTaxRate":0.000,"medianHomePrice":350000},
    "33340": {"walkScore":62,"transitScore":45,"crimeIndex":68,"unemploymentRate":4.0,"jobGrowthRate":1.2,"avgBenefitsValue":15500,"sunDaysPerYear":188,"populationM":1.60,"popGrowthRate": 0.5,"localTaxRate":0.000,"medianHomePrice":265000},
    "33460": {"walkScore":70,"transitScore":58,"crimeIndex":58,"unemploymentRate":3.2,"jobGrowthRate":1.8,"avgBenefitsValue":17800,"sunDaysPerYear":198,"populationM":3.70,"popGrowthRate": 7.8,"localTaxRate":0.000,"medianHomePrice":360000},
    "36540": {"walkScore":38,"transitScore":25,"crimeIndex":42,"unemploymentRate":3.0,"jobGrowthRate":2.0,"avgBenefitsValue":15000,"sunDaysPerYear":195,"populationM":0.97,"popGrowthRate": 7.8,"localTaxRate":0.000,"medianHomePrice":295000},
    "41180": {"walkScore":55,"transitScore":40,"crimeIndex":78,"unemploymentRate":4.0,"jobGrowthRate":1.0,"avgBenefitsValue":15800,"sunDaysPerYear":203,"populationM":2.80,"popGrowthRate": 1.5,"localTaxRate":0.010,"medianHomePrice":245000},
    "48620": {"walkScore":37,"transitScore":20,"crimeIndex":60,"unemploymentRate":4.0,"jobGrowthRate":1.5,"avgBenefitsValue":14500,"sunDaysPerYear":212,"populationM":0.64,"popGrowthRate": 3.5,"localTaxRate":0.000,"medianHomePrice":210000},
    # West
    "10740": {"walkScore":44,"transitScore":28,"crimeIndex":68,"unemploymentRate":4.5,"jobGrowthRate":1.5,"avgBenefitsValue":14500,"sunDaysPerYear":297,"populationM":0.92,"popGrowthRate": 3.5,"localTaxRate":0.000,"medianHomePrice":295000},
    "14260": {"walkScore":42,"transitScore":22,"crimeIndex":35,"unemploymentRate":3.2,"jobGrowthRate":3.5,"avgBenefitsValue":14800,"sunDaysPerYear":205,"populationM":0.82,"popGrowthRate":28.4,"localTaxRate":0.000,"medianHomePrice":445000},
    "17820": {"walkScore":37,"transitScore":24,"crimeIndex":40,"unemploymentRate":4.0,"jobGrowthRate":2.0,"avgBenefitsValue":14800,"sunDaysPerYear":243,"populationM":0.76,"popGrowthRate":10.7,"localTaxRate":0.000,"medianHomePrice":390000},
    "19740": {"walkScore":62,"transitScore":52,"crimeIndex":55,"unemploymentRate":3.5,"jobGrowthRate":2.0,"avgBenefitsValue":16500,"sunDaysPerYear":300,"populationM":2.90,"popGrowthRate":14.2,"localTaxRate":0.000,"medianHomePrice":555000},
    "23420": {"walkScore":43,"transitScore":29,"crimeIndex":70,"unemploymentRate":6.0,"jobGrowthRate":1.5,"avgBenefitsValue":15500,"sunDaysPerYear":272,"populationM":1.00,"popGrowthRate": 3.8,"localTaxRate":0.000,"medianHomePrice":355000},
    "29820": {"walkScore":42,"transitScore":38,"crimeIndex":70,"unemploymentRate":5.2,"jobGrowthRate":2.8,"avgBenefitsValue":14500,"sunDaysPerYear":294,"populationM":2.30,"popGrowthRate":15.1,"localTaxRate":0.000,"medianHomePrice":420000},
    "31080": {"walkScore":67,"transitScore":55,"crimeIndex":65,"unemploymentRate":5.2,"jobGrowthRate":1.2,"avgBenefitsValue":18200,"sunDaysPerYear":284,"populationM":13.20,"popGrowthRate":-1.5,"localTaxRate":0.000,"medianHomePrice":800000},
    "32580": {"walkScore":33,"transitScore":18,"crimeIndex":42,"unemploymentRate":5.5,"jobGrowthRate":2.0,"avgBenefitsValue":12500,"sunDaysPerYear":228,"populationM":0.88,"popGrowthRate": 8.8,"localTaxRate":0.000,"medianHomePrice":185000},
    "36260": {"walkScore":32,"transitScore":22,"crimeIndex":28,"unemploymentRate":3.2,"jobGrowthRate":2.5,"avgBenefitsValue":14800,"sunDaysPerYear":222,"populationM":0.68,"popGrowthRate":15.3,"localTaxRate":0.000,"medianHomePrice":430000},
    "38060": {"walkScore":42,"transitScore":38,"crimeIndex":60,"unemploymentRate":3.8,"jobGrowthRate":3.2,"avgBenefitsValue":15500,"sunDaysPerYear":299,"populationM":5.00,"popGrowthRate":19.2,"localTaxRate":0.000,"medianHomePrice":430000},
    "38900": {"walkScore":67,"transitScore":58,"crimeIndex":65,"unemploymentRate":4.2,"jobGrowthRate":1.5,"avgBenefitsValue":17500,"sunDaysPerYear":144,"populationM":2.50,"popGrowthRate": 5.8,"localTaxRate":0.000,"medianHomePrice":525000},
    "39340": {"walkScore":35,"transitScore":25,"crimeIndex":22,"unemploymentRate":2.8,"jobGrowthRate":3.0,"avgBenefitsValue":14500,"sunDaysPerYear":225,"populationM":0.67,"popGrowthRate":20.8,"localTaxRate":0.000,"medianHomePrice":480000},
    "40140": {"walkScore":32,"transitScore":22,"crimeIndex":55,"unemploymentRate":5.0,"jobGrowthRate":2.2,"avgBenefitsValue":16800,"sunDaysPerYear":277,"populationM":4.60,"popGrowthRate": 7.8,"localTaxRate":0.000,"medianHomePrice":530000},
    "40900": {"walkScore":52,"transitScore":42,"crimeIndex":62,"unemploymentRate":4.5,"jobGrowthRate":1.8,"avgBenefitsValue":17500,"sunDaysPerYear":273,"populationM":2.40,"popGrowthRate": 5.2,"localTaxRate":0.000,"medianHomePrice":495000},
    "41620": {"walkScore":62,"transitScore":48,"crimeIndex":48,"unemploymentRate":3.0,"jobGrowthRate":2.8,"avgBenefitsValue":15800,"sunDaysPerYear":222,"populationM":1.20,"popGrowthRate":14.8,"localTaxRate":0.000,"medianHomePrice":525000},
    "41740": {"walkScore":52,"transitScore":42,"crimeIndex":45,"unemploymentRate":4.0,"jobGrowthRate":2.0,"avgBenefitsValue":18500,"sunDaysPerYear":266,"populationM":3.30,"popGrowthRate": 3.8,"localTaxRate":0.000,"medianHomePrice":810000},
    "41860": {"walkScore":88,"transitScore":80,"crimeIndex":72,"unemploymentRate":4.5,"jobGrowthRate":0.5,"avgBenefitsValue":22000,"sunDaysPerYear":259,"populationM":4.70,"popGrowthRate":-4.5,"localTaxRate":0.000,"medianHomePrice":1150000},
    "41940": {"walkScore":55,"transitScore":45,"crimeIndex":52,"unemploymentRate":4.0,"jobGrowthRate":2.2,"avgBenefitsValue":22500,"sunDaysPerYear":257,"populationM":2.00,"popGrowthRate":-1.2,"localTaxRate":0.000,"medianHomePrice":1250000},
    "42660": {"walkScore":73,"transitScore":62,"crimeIndex":60,"unemploymentRate":4.2,"jobGrowthRate":2.5,"avgBenefitsValue":20500,"sunDaysPerYear":152,"populationM":4.10,"popGrowthRate":13.5,"localTaxRate":0.000,"medianHomePrice":780000},
    "44060": {"walkScore":48,"transitScore":30,"crimeIndex":45,"unemploymentRate":4.0,"jobGrowthRate":2.0,"avgBenefitsValue":15200,"sunDaysPerYear":196,"populationM":0.57,"popGrowthRate":10.2,"localTaxRate":0.000,"medianHomePrice":370000},
    "44700": {"walkScore":43,"transitScore":25,"crimeIndex":72,"unemploymentRate":7.0,"jobGrowthRate":1.5,"avgBenefitsValue":15500,"sunDaysPerYear":250,"populationM":0.78,"popGrowthRate": 6.2,"localTaxRate":0.000,"medianHomePrice":415000},
    "46060": {"walkScore":43,"transitScore":28,"crimeIndex":52,"unemploymentRate":4.5,"jobGrowthRate":2.0,"avgBenefitsValue":14500,"sunDaysPerYear":286,"populationM":1.02,"popGrowthRate": 5.5,"localTaxRate":0.000,"medianHomePrice":320000},
    "46140": {"walkScore":38,"transitScore":22,"crimeIndex":62,"unemploymentRate":3.8,"jobGrowthRate":1.8,"avgBenefitsValue":14500,"sunDaysPerYear":218,"populationM":1.01,"popGrowthRate": 5.8,"localTaxRate":0.000,"medianHomePrice":250000},
}


def apply_supplemental_data(cities: dict) -> dict:
    """Merge hardcoded supplemental data (walkScore, crime, demographics, etc.) into cities."""
    matched = 0
    for cbsa, city in cities.items():
        if cbsa in SUPPLEMENTAL_DATA:
            cities[cbsa].update(SUPPLEMENTAL_DATA[cbsa])
            matched += 1
        else:
            print(f"  [Supplemental] WARNING: No supplemental data for {city['name']} ({cbsa})")
    print(f"  [Supplemental] Applied for {matched}/{len(cities)} cities.")
    return cities


# ── SECTION 7: MIT LIVING WAGE ────────────────────────────────────────────────

def fetch_mit_living_wages() -> dict:
    """Scrape MIT Living Wage Calculator for 1-adult, 0-children annual wage per metro."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [MIT] beautifulsoup4 not installed. Using HUD fallback.")
        return fetch_hud_fmr_fallback()

    living_wages = {}
    base_url = "https://livingwage.mit.edu/metros/{cbsa}"

    print(f"  [MIT] Scraping living wages for {len(TARGET_CBSA_CODES)} metros ...")
    print("        (1-second delay between requests)")

    for cbsa, meta in TARGET_CBSA_CODES.items():
        url = base_url.format(cbsa=cbsa)
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "lxml")
            wage = _parse_mit_page(soup, cbsa, meta["name"])
            if wage:
                living_wages[cbsa] = wage
                print(f"    {meta['name']}: ${wage:,}")
            else:
                print(f"    {meta['name']}: PARSE FAILED")
        except Exception as e:
            print(f"    {meta['name']}: REQUEST FAILED ({e})")
        time.sleep(1)

    success_rate = len(living_wages) / len(TARGET_CBSA_CODES)
    if success_rate < 0.5:
        print(f"  [MIT] Only {len(living_wages)} cities scraped. Using HUD fallback.")
        return fetch_hud_fmr_fallback()

    print(f"  [MIT] Scraped {len(living_wages)}/{len(TARGET_CBSA_CODES)} cities.")
    return living_wages


def _parse_mit_page(soup, cbsa: str, city_name: str):
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            cell_texts = [c.get_text(strip=True) for c in cells]
            if not cell_texts:
                continue
            if "Living Wage" in cell_texts[0]:
                for cell_text in cell_texts[1:4]:
                    cleaned = cell_text.replace("$", "").replace(",", "").strip()
                    try:
                        val = float(cleaned)
                        if 20000 < val < 150000:
                            return int(round(val / 100) * 100)
                        elif 10 < val < 60:
                            return int(round((val * 2080) / 100) * 100)
                    except ValueError:
                        continue
    return None


def fetch_hud_fmr_fallback() -> dict:
    """Download HUD FY2025 Fair Market Rents as a living-wage fallback."""
    print("  [HUD] Downloading HUD FY2025 Fair Market Rents ...")
    hud_url = "https://www.huduser.gov/portal/datasets/fmr/fmr2025/FY2025_4050_FMRs_rev.xlsx"
    try:
        r = requests.get(hud_url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        xlsx_path = "data/raw/hud/FY2025_FMRs.xlsx"
        with open(xlsx_path, "wb") as f:
            f.write(r.content)

        df = pd.read_excel(xlsx_path, dtype=str)
        df.columns = [c.strip().lower() for c in df.columns]
        cbsa_col = next((c for c in df.columns if "cbsa" in c), None)
        fmr1_col = next((c for c in df.columns if "fmr1" in c or "fmr_1" in c), None)

        if not cbsa_col or not fmr1_col:
            print(f"  [HUD] Could not find expected columns. Got: {list(df.columns)}")
            return {}

        df[fmr1_col] = pd.to_numeric(df[fmr1_col], errors="coerce")
        df[cbsa_col] = df[cbsa_col].astype(str).str.strip()
        hud_by_cbsa = df.groupby(cbsa_col)[fmr1_col].median()

        result = {}
        for cbsa in TARGET_CBSA_CODES:
            if cbsa in hud_by_cbsa.index:
                monthly_1br = hud_by_cbsa[cbsa]
                if pd.notna(monthly_1br):
                    result[cbsa] = int(round((monthly_1br * 12) / 100) * 100)

        print(f"  [HUD] Matched FMR for {len(result)}/{len(TARGET_CBSA_CODES)} cities.")
        return result
    except Exception as e:
        print(f"  [HUD] Failed: {e}")
        return {}


# ── FIELD ORDER ───────────────────────────────────────────────────────────────

FIELDS_ORDER = [
    "name", "short", "state", "region", "id", "salaries",
    "medianRent1BR", "medianHomePrice",
    "stateTaxRate", "localTaxRate",
    "colIndex",
    "unemploymentRate", "jobGrowthRate",
    "walkScore", "transitScore", "crimeIndex",
    "avgBenefitsValue", "sunDaysPerYear",
    "populationM", "popGrowthRate",
]


def reorder_city(city: dict) -> dict:
    ordered = {}
    for k in FIELDS_ORDER:
        if k in city:
            ordered[k] = city[k]
    for k in sorted(city):
        if k not in ordered:
            ordered[k] = city[k]
    return ordered


# ── OUTPUT ────────────────────────────────────────────────────────────────────

def write_cities_json(cities: dict):
    """Write public/data/cities.json, dropping cities with critical missing data."""
    output = []
    skipped = []
    for cbsa, city in cities.items():
        missing_salaries = sum(1 for occ in TARGET_OCC_CODES if occ not in city.get("salaries", {}))
        if city.get("medianRent1BR") is None:
            skipped.append((city["name"], "missing rent"))
            continue
        if missing_salaries > len(TARGET_OCC_CODES) // 2:
            skipped.append((city["name"], f"missing {missing_salaries}/{len(TARGET_OCC_CODES)} salary fields"))
            continue
        output.append(reorder_city(city))

    for name, reason in skipped:
        print(f"  DROPPED: {name} — {reason}")

    output.sort(key=lambda x: x["name"])

    with open("public/data/cities.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  cities.json: {len(output)} cities written, {len(skipped)} dropped.")


def write_living_wage_json(living_wages: dict):
    if not living_wages:
        print("  [Output] No living wage data to write.")
        return
    with open("public/data/living-wage.json", "w", encoding="utf-8") as f:
        json.dump(living_wages, f, indent=2)
    print(f"  living-wage.json: {len(living_wages)} cities written.")


# ── VALIDATION ────────────────────────────────────────────────────────────────

def validate_cities():
    print("\n--- Running validation ---")
    try:
        with open("public/data/cities.json", encoding="utf-8") as f:
            cities = {c["id"]: c for c in json.load(f)}
    except FileNotFoundError:
        print("FAIL: public/data/cities.json not found.")
        return

    errors = []

    def check(condition, message):
        if not condition:
            errors.append(f"FAIL: {message}")

    check(len(cities) >= 60, f"Expected >= 60 cities, got {len(cities)}")

    sf = cities.get("41860", {})
    check(sf.get("state") == "CA", "SF state should be CA")
    check(sf.get("stateTaxRate") == 0.093, f"SF tax rate should be 0.093, got {sf.get('stateTaxRate')}")
    check(20000 <= sf.get("medianRent1BR", 0) <= 50000, f"SF rent out of range: {sf.get('medianRent1BR')}")
    check(130000 <= sf.get("salaries", {}).get("15-1252", 0) <= 220000, "SF software dev salary out of range")
    check(sf.get("walkScore", 0) >= 70, "SF walkScore should be >= 70")
    check(sf.get("medianHomePrice", 0) >= 800000, "SF medianHomePrice should be >= $800k")

    dal = cities.get("19100", {})
    check(dal.get("stateTaxRate") == 0.0, f"Dallas tax rate should be 0, got {dal.get('stateTaxRate')}")
    check(dal.get("localTaxRate") == 0.0, f"Dallas localTaxRate should be 0, got {dal.get('localTaxRate')}")

    nyc = cities.get("35620", {})
    check(nyc.get("stateTaxRate") >= 0.10, f"NYC tax rate should be >= 0.10")
    check(nyc.get("walkScore", 0) >= 80, "NYC walkScore should be >= 80")
    check(nyc.get("populationM", 0) >= 15, "NYC population should be >= 15M")

    for cbsa, city in cities.items():
        if city["state"] in ["TX", "FL", "WA", "NV"]:
            check(city["stateTaxRate"] == 0.0, f"{city['name']} should have 0 state tax rate")
        count = len(city.get("salaries", {}))
        check(count >= 15, f"{city['name']} only has {count} occupation salaries (need >= 15)")

    # Check all new supplemental fields present
    new_fields = ["medianHomePrice", "localTaxRate", "unemploymentRate", "jobGrowthRate",
                  "walkScore", "transitScore", "crimeIndex", "avgBenefitsValue",
                  "sunDaysPerYear", "populationM", "popGrowthRate"]
    for cbsa, city in list(cities.items())[:5]:
        for field in new_fields:
            check(field in city, f"{city['name']} missing field: {field}")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"   {e}")
    else:
        print(f"\nAll validation checks passed. {len(cities)} cities ready.")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=== Salary Reality Check — Data Download Pipeline ===\n")
    print(f"  Target: {len(TARGET_CBSA_CODES)} cities, {len(TARGET_OCC_CODES)} occupations\n")

    print("Step 1/7: BLS OEWS — Salary Data")
    download_bls()
    cities = load_bls_salaries()

    print("\nStep 2/7: Zillow ZORI — Rent Data")
    download_zillow_zori()
    cities = load_zillow_rents(cities)

    print("\nStep 3/7: Zillow ZHVI — Home Price Data")
    download_zillow_zhvi()
    cities = load_zhvi_home_prices(cities)

    print("\nStep 4/7: State Tax Rates (hardcoded)")
    cities = apply_tax_rates(cities)

    print("\nStep 5/7: Cost of Living Index (hardcoded)")
    cities = load_col_index(cities)

    print("\nStep 6/7: Supplemental Data (walk scores, crime, demographics, etc.)")
    cities = apply_supplemental_data(cities)

    print("\nStep 7/7: MIT Living Wage (with HUD FMR fallback)")
    living_wages = fetch_mit_living_wages()

    print("\n--- Writing output files ---")
    write_cities_json(cities)
    write_living_wage_json(living_wages)

    validate_cities()

    print("\nDone. Run `npm run dev` to preview, then `npm run build` to deploy.")


if __name__ == "__main__":
    main()
