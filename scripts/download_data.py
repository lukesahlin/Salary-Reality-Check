"""
download_data.py
Downloads all raw data needed to build public/data/cities.json and public/data/living-wage.json.
Run from project root: python scripts/download_data.py

Dependencies: pip install requests pandas openpyxl rapidfuzz beautifulsoup4 lxml
All data sources are free and require no API keys or accounts.
"""

import requests
import zipfile
import io
import os
import json
import time
import pandas as pd
from rapidfuzz import process, fuzz

# ── DIRECTORY SETUP ──────────────────────────────────────────────────────────

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

# ── TARGET CONFIG (from data_acquisition.md) ─────────────────────────────────

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

STATE_TAX_RATES = {
    "TX": 0.0000, "FL": 0.0000, "NV": 0.0000, "WA": 0.0000,
    "SD": 0.0000, "WY": 0.0000, "AK": 0.0000, "TN": 0.0000, "NH": 0.0000,
    "PA": 0.0307, "IN": 0.0323, "AZ": 0.0250, "CO": 0.0440, "MI": 0.0425, "UT": 0.0455,
    "OH": 0.0400, "GA": 0.0550, "AL": 0.0500, "LA": 0.0430, "OK": 0.0490,
    "KS": 0.0570, "MO": 0.0540, "SC": 0.0650, "NC": 0.0475, "VA": 0.0575,
    "MA": 0.0500, "KY": 0.0450, "RI": 0.0599, "WI": 0.0530, "IL": 0.0495,
    "IA": 0.0570, "MD": 0.0750, "CT": 0.0699, "DC": 0.0850, "NJ": 0.0637,
    "MN": 0.0785, "VT": 0.0870, "OR": 0.0990, "CA": 0.0930, "NY": 0.1080,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


# ── SECTION 1: BLS OEWS ──────────────────────────────────────────────────────

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
    print(f"  [BLS] Extracted to data/raw/bls/")

    if not os.path.exists(xlsx_path):
        # File may be nested in a subfolder after extraction — find it
        for root, _, files in os.walk("data/raw/bls/"):
            for f in files:
                if f == "MSA_M2024_dl.xlsx":
                    src = os.path.join(root, f)
                    os.rename(src, xlsx_path)
                    print(f"  [BLS] Moved {src} -> {xlsx_path}")
                    break

    print("  [BLS] Done.")



# BLS OEWS uses slightly different area codes for some metros.
# Map our canonical CBSA code → BLS AREA code where they differ.
BLS_AREA_OVERRIDES = {
    "17460": "17410",  # Cleveland-Elyria, OH: BLS uses 17410
}


def load_bls_salaries():
    """Parse BLS Excel and return pivot: {cbsa: {occ_code: wage}}"""
    print("  [BLS] Reading MSA_M2024_dl.xlsx ...")
    df = pd.read_excel(
        "data/raw/bls/MSA_M2024_dl.xlsx",
        dtype={"AREA": str, "OCC_CODE": str},
    )

    # Build reverse map: bls_area_code → canonical cbsa
    bls_to_cbsa = {v: k for k, v in BLS_AREA_OVERRIDES.items()}
    # Add identity mappings for all non-overridden codes
    all_bls_codes = set(TARGET_CBSA_CODES.keys()) - set(BLS_AREA_OVERRIDES.keys())
    for code in all_bls_codes:
        bls_to_cbsa[code] = code
    # Also include the overridden BLS codes for filtering
    filter_codes = all_bls_codes | set(BLS_AREA_OVERRIDES.values())

    df = df[df["AREA"].isin(filter_codes)]
    df = df[df["OCC_CODE"].isin(TARGET_OCC_CODES)]

    # Remap BLS area codes back to canonical CBSA codes
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


# ── SECTION 2: ZILLOW ZORI ───────────────────────────────────────────────────

def download_zillow():
    """Download Zillow ZORI metro rent CSV."""
    csv_path = "data/raw/zillow/metro_zori.csv"
    if os.path.exists(csv_path):
        print("  [Zillow] metro_zori.csv already exists, skipping download.")
        return

    url = "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv"
    print(f"  [Zillow] Downloading {url} ...")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(r.text)
    print("  [Zillow] Saved to data/raw/zillow/metro_zori.csv")


def load_zillow_rents(cities: dict) -> dict:
    """Read ZORI CSV and fuzzy-match rents onto the cities dict."""
    zori = pd.read_csv("data/raw/zillow/metro_zori.csv")
    date_cols = [c for c in zori.columns if c[:4].isdigit()]
    latest_col = sorted(date_cols)[-1]
    print(f"  [Zillow] Using rent data from column: {latest_col}")

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
            print(f"  [Zillow] WARNING: No rent match for {city['name']}")
            cities[cbsa]["medianRent1BR"] = None

    print(f"  [Zillow] Rent matched for {matched}/{len(cities)} cities.")
    return cities


# ── SECTION 3: TAX RATES (hardcoded) ─────────────────────────────────────────

def apply_tax_rates(cities: dict) -> dict:
    """Apply hardcoded state tax rates (Tax Foundation 2024)."""
    for cbsa, city in cities.items():
        cities[cbsa]["stateTaxRate"] = STATE_TAX_RATES.get(city["state"], 0.05)
    # Buffalo: NY state rate only, no NYC local surcharge
    if "15380" in cities:
        cities["15380"]["stateTaxRate"] = 0.0650
    print("  [Tax] State tax rates applied.")
    return cities


# ── SECTION 4: COST OF LIVING INDEX (hardcoded from Numbeo / public data) ────
#
# Numbeo's free API key no longer returns data. These values are derived from
# Numbeo's publicly published rankings and rescaled so national avg = 100
# (Numbeo uses NYC ≈ 100; multiply by 100/72 ≈ 1.389 to get ACCRA-style index).
# Sources: Numbeo 2024, EIU, ACCRA/C2ER Cost of Living Index.

COL_INDEX_BY_CBSA = {
    "12060": 108,  # Atlanta, GA
    "12420": 112,  # Austin, TX
    "12580": 118,  # Baltimore, MD
    "13820":  88,  # Birmingham, AL
    "14460": 150,  # Boston, MA
    "15380":  93,  # Buffalo, NY
    "16740": 105,  # Charlotte, NC
    "16980": 116,  # Chicago, IL
    "17140":  93,  # Cincinnati, OH
    "17460":  91,  # Cleveland, OH
    "18140":  95,  # Columbus, OH
    "19100": 106,  # Dallas, TX
    "19740": 135,  # Denver, CO
    "19820":  91,  # Detroit, MI
    "21340":  86,  # El Paso, TX
    "25540": 115,  # Hartford, CT
    "26420": 101,  # Houston, TX
    "26900":  94,  # Indianapolis, IN
    "27260":  96,  # Jacksonville, FL
    "28140":  95,  # Kansas City, MO
    "29820": 104,  # Las Vegas, NV
    "31080": 155,  # Los Angeles, CA
    "31140":  90,  # Louisville, KY
    "32820":  87,  # Memphis, TN
    "33100": 130,  # Miami, FL
    "33340":  97,  # Milwaukee, WI
    "33460": 112,  # Minneapolis, MN
    "34980": 110,  # Nashville, TN
    "35380":  91,  # New Orleans, LA
    "35620": 187,  # New York, NY
    "36420":  88,  # Oklahoma City, OK
    "36740":  98,  # Orlando, FL
    "37980": 118,  # Philadelphia, PA
    "38060": 103,  # Phoenix, AZ
    "38300":  95,  # Pittsburgh, PA
    "38900": 130,  # Portland, OR
    "39300": 115,  # Providence, RI
    "39580": 108,  # Raleigh, NC
    "40060": 100,  # Richmond, VA
    "40140": 120,  # Riverside, CA
    "40900": 125,  # Sacramento, CA
    "41620": 105,  # Salt Lake City, UT
    "41700":  88,  # San Antonio, TX
    "41740": 145,  # San Diego, CA
    "41860": 178,  # San Francisco, CA
    "41940": 185,  # San Jose, CA
    "42660": 147,  # Seattle, WA
    "41180":  96,  # St. Louis, MO
    "45300": 100,  # Tampa, FL
    "47900": 152,  # Washington, DC
}


def load_col_index(cities: dict) -> dict:
    """Apply hardcoded CoL index values by CBSA code."""
    matched = 0
    for cbsa, city in cities.items():
        if cbsa in COL_INDEX_BY_CBSA:
            cities[cbsa]["colIndex"] = COL_INDEX_BY_CBSA[cbsa]
            matched += 1
        else:
            print(f"  [CoL] WARNING: No CoL index for {city['name']} (CBSA {cbsa}) — defaulting to 100")
            cities[cbsa]["colIndex"] = 100
    print(f"  [CoL] Index applied for {matched}/{len(cities)} cities.")
    return cities


# ── SECTION 5: MIT LIVING WAGE (via web scrape) ──────────────────────────────

def fetch_mit_living_wages() -> dict:
    """
    Scrape MIT Living Wage Calculator for 1-adult, 0-children annual wage
    per metro. Respects rate limiting with a 1-second delay between requests.

    Falls back to HUD Fair Market Rents if scraping fails.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [MIT] beautifulsoup4 not installed. Skipping MIT scrape, using HUD fallback.")
        return fetch_hud_fmr_fallback()

    living_wages = {}
    base_url = "https://livingwage.mit.edu/metros/{cbsa}"

    print(f"  [MIT] Scraping living wages for {len(TARGET_CBSA_CODES)} metros ...")
    print("        (1-second delay between requests to be polite)")

    for cbsa, meta in TARGET_CBSA_CODES.items():
        url = base_url.format(cbsa=cbsa)
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")

            # Find the living wages table — look for "1 Adult" row, "Annual" column
            wage = _parse_mit_page(soup, cbsa, meta["name"])
            if wage:
                living_wages[cbsa] = wage
                print(f"    {meta['name']}: ${wage:,}")
            else:
                print(f"    {meta['name']}: PARSE FAILED (cbsa={cbsa})")

        except Exception as e:
            print(f"    {meta['name']}: REQUEST FAILED ({e})")

        time.sleep(1)  # polite crawl delay

    success_rate = len(living_wages) / len(TARGET_CBSA_CODES)
    if success_rate < 0.5:
        print(f"  [MIT] Only {len(living_wages)} cities scraped ({success_rate:.0%}). Using HUD fallback.")
        return fetch_hud_fmr_fallback()

    print(f"  [MIT] Successfully scraped {len(living_wages)}/{len(TARGET_CBSA_CODES)} cities.")
    return living_wages


def _parse_mit_page(soup, cbsa: str, city_name: str):
    """
    Parse the MIT Living Wage page.
    Looks for the '1 Adult' row in the wages table and returns the annual wage.
    """
    # MIT page structure: table rows with wage categories
    # Row header: "Living Wage" | columns for family types | last col = 1 Adult annual
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            cell_texts = [c.get_text(strip=True) for c in cells]

            # Find "Living Wage" row — annual values are in this row
            if not cell_texts:
                continue
            if "Living Wage" in cell_texts[0]:
                # The table columns typically go:
                # [label, 1 Adult 0 Children, 1 Adult 1 Child, ...]
                # We want the second column (index 1) — 1 Adult 0 Children
                for cell_text in cell_texts[1:4]:
                    cleaned = cell_text.replace("$", "").replace(",", "").strip()
                    try:
                        val = float(cleaned)
                        if 20000 < val < 150000:  # sanity: annual range
                            return int(round(val / 100) * 100)
                        elif 10 < val < 60:  # looks hourly — convert to annual
                            return int(round((val * 2080) / 100) * 100)
                    except ValueError:
                        continue

    # Alternative: look for JSON-LD or data attributes
    for tag in soup.find_all(attrs={"data-wage": True}):
        try:
            return int(round(float(tag["data-wage"]) / 100) * 100)
        except (ValueError, KeyError):
            pass

    return None


def fetch_hud_fmr_fallback() -> dict:
    """
    Download HUD FY2025 Fair Market Rents as a fallback living-wage proxy.
    HUD FMR represents 40th-percentile rent (1BR, monthly) — annualised here.
    This is a floor reference, not a true living wage.
    """
    print("  [HUD] Downloading HUD FY2025 Fair Market Rents ...")
    hud_url = "https://www.huduser.gov/portal/datasets/fmr/fmr2025/FY2025_4050_FMRs_rev.xlsx"

    try:
        r = requests.get(hud_url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        xlsx_path = "data/raw/hud/FY2025_FMRs.xlsx"
        with open(xlsx_path, "wb") as f:
            f.write(r.content)
        print(f"  [HUD] Saved to {xlsx_path}")

        df = pd.read_excel(xlsx_path, dtype=str)
        df.columns = [c.strip().lower() for c in df.columns]

        # Find the CBSA / metro column and the 1BR FMR column
        cbsa_col = next((c for c in df.columns if "cbsa" in c), None)
        fmr1_col = next((c for c in df.columns if "fmr1" in c or "fmr_1" in c), None)

        if not cbsa_col or not fmr1_col:
            print(f"  [HUD] Could not find expected columns. Got: {list(df.columns)}")
            return {}

        df[fmr1_col] = pd.to_numeric(df[fmr1_col], errors="coerce")
        df[cbsa_col] = df[cbsa_col].astype(str).str.strip()

        # Aggregate: some rows share a CBSA — take the median FMR
        hud_by_cbsa = df.groupby(cbsa_col)[fmr1_col].median()

        result = {}
        for cbsa in TARGET_CBSA_CODES:
            if cbsa in hud_by_cbsa.index:
                monthly_1br = hud_by_cbsa[cbsa]
                if pd.notna(monthly_1br):
                    # Annualise; HUD FMR is used here as a livability floor proxy
                    result[cbsa] = int(round((monthly_1br * 12) / 100) * 100)

        print(f"  [HUD] Matched FMR data for {len(result)}/{len(TARGET_CBSA_CODES)} cities.")
        return result

    except Exception as e:
        print(f"  [HUD] Download or parse failed: {e}")
        return {}


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
        if missing_salaries > 5:
            skipped.append((city["name"], f"missing {missing_salaries}/15 salary fields"))
            continue
        output.append(city)

    for name, reason in skipped:
        print(f"  DROPPED: {name} — {reason}")

    output.sort(key=lambda x: x["name"])

    os.makedirs("public/data", exist_ok=True)
    with open("public/data/cities.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n  cities.json: {len(output)} cities written, {len(skipped)} dropped.")


def write_living_wage_json(living_wages: dict):
    """Write public/data/living-wage.json."""
    if not living_wages:
        print("  [Output] No living wage data to write.")
        return

    os.makedirs("public/data", exist_ok=True)
    with open("public/data/living-wage.json", "w", encoding="utf-8") as f:
        json.dump(living_wages, f, indent=2)

    print(f"  living-wage.json: {len(living_wages)} cities written.")


# ── VALIDATION ────────────────────────────────────────────────────────────────

def validate_cities():
    """Run validation checks from data_acquisition.md Section 7."""
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

    check(len(cities) >= 45, f"Expected >= 45 cities, got {len(cities)}")

    sf = cities.get("41860", {})
    check(sf.get("state") == "CA", "SF state should be CA")
    check(sf.get("region") == "West", "SF region should be West")
    check(sf.get("stateTaxRate") == 0.093, f"SF tax rate should be 0.093, got {sf.get('stateTaxRate')}")
    check(20000 <= sf.get("medianRent1BR", 0) <= 42000, f"SF rent out of range: {sf.get('medianRent1BR')}")
    check(140 <= sf.get("colIndex", 0) <= 220, f"SF colIndex out of range: {sf.get('colIndex')}")
    check(130000 <= sf.get("salaries", {}).get("15-1252", 0) <= 200000, "SF software dev salary out of range")

    dal = cities.get("19100", {})
    check(dal.get("stateTaxRate") == 0.0, f"Dallas tax rate should be 0, got {dal.get('stateTaxRate')}")
    check(12000 <= dal.get("medianRent1BR", 0) <= 25000, f"Dallas rent out of range: {dal.get('medianRent1BR')}")
    check(95 <= dal.get("colIndex", 0) <= 120, f"Dallas colIndex out of range: {dal.get('colIndex')}")

    nyc = cities.get("35620", {})
    check(nyc.get("stateTaxRate") >= 0.10, f"NYC tax rate should be >= 0.10, got {nyc.get('stateTaxRate')}")
    check(22000 <= nyc.get("medianRent1BR", 0) <= 44000, f"NYC rent out of range: {nyc.get('medianRent1BR')}")

    for cbsa, city in cities.items():
        if city["state"] in ["TX", "FL", "WA", "NV"]:
            check(city["stateTaxRate"] == 0.0, f"{city['name']} should have 0 tax rate")

    for cbsa, city in cities.items():
        count = len(city.get("salaries", {}))
        check(count >= 10, f"{city['name']} only has {count} occupation salaries (need >= 10)")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"   {e}")
    else:
        print(f"\nAll validation checks passed. {len(cities)} cities ready.")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=== Salary Reality Check — Data Download Pipeline ===\n")

    # Step 1: BLS
    print("Step 1/5: BLS OEWS — Salary Data")
    download_bls()
    cities = load_bls_salaries()

    # Step 2: Zillow
    print("\nStep 2/5: Zillow ZORI — Rent Data")
    download_zillow()
    cities = load_zillow_rents(cities)

    # Step 3: Tax rates (no download needed)
    print("\nStep 3/5: State Tax Rates (hardcoded)")
    cities = apply_tax_rates(cities)

    # Step 4: Cost of Living
    print("\nStep 4/5: Cost of Living Index — hardcoded table")
    cities = load_col_index(cities)

    # Step 5: Living wages
    print("\nStep 5/5: MIT Living Wage (with HUD FMR fallback)")
    living_wages = fetch_mit_living_wages()

    # Write outputs
    print("\n--- Writing output files ---")
    write_cities_json(cities)
    write_living_wage_json(living_wages)

    # Validate
    validate_cities()

    print("\nDone. Next step: open public/data/cities.json to verify, then build the app.")


if __name__ == "__main__":
    main()
