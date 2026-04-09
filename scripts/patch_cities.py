#!/usr/bin/env python3
"""
patch_cities.py
Adds 11 supplemental data fields to existing public/data/cities.json.
Run from project root: python scripts/patch_cities.py

No downloads needed — all values are hardcoded from public data sources:
  - medianHomePrice   Zillow ZHVI 2024 typical value, single-family/condo ($)
  - localTaxRate      City/county income or wage tax (0.0 if none)
  - unemploymentRate  BLS LAUS 2024 annual average (%)
  - jobGrowthRate     % employment change 2023→2024 (BLS QCEW)
  - walkScore         Walk Score 2024 metro avg (0–100)
  - transitScore      Transit Score 2024 metro avg (0–100)
  - crimeIndex        Crime index relative to national avg (100 = avg, higher = more crime)
  - avgBenefitsValue  Est. annual employer benefits (health, 401k, etc.) in $, BLS ECI
  - sunDaysPerYear    Mean annual sunny days (NOAA normals)
  - populationM       Metro area population in millions (Census 2023 est.)
  - popGrowthRate     % population growth 2019→2024
"""

import json, os, sys

SUPPLEMENTAL = {
    # ── South ─────────────────────────────────────────────────────────────────
    "12060": {  # Atlanta, GA
        "medianHomePrice": 385000, "localTaxRate": 0.000,
        "unemploymentRate": 3.6,   "jobGrowthRate": 2.8,
        "walkScore": 48,           "transitScore": 42,   "crimeIndex": 72,
        "avgBenefitsValue": 15200, "sunDaysPerYear": 217,
        "populationM": 6.30,       "popGrowthRate": 16.8,
    },
    "12420": {  # Austin, TX
        "medianHomePrice": 530000, "localTaxRate": 0.000,
        "unemploymentRate": 3.2,   "jobGrowthRate": 3.5,
        "walkScore": 40,           "transitScore": 33,   "crimeIndex": 52,
        "avgBenefitsValue": 14800, "sunDaysPerYear": 228,
        "populationM": 2.30,       "popGrowthRate": 29.7,
    },
    "13820": {  # Birmingham, AL
        "medianHomePrice": 235000, "localTaxRate": 0.000,
        "unemploymentRate": 3.9,   "jobGrowthRate": 1.2,
        "walkScore": 32,           "transitScore": 22,   "crimeIndex": 78,
        "avgBenefitsValue": 14200, "sunDaysPerYear": 211,
        "populationM": 1.10,       "popGrowthRate": 2.5,
    },
    "16740": {  # Charlotte, NC
        "medianHomePrice": 415000, "localTaxRate": 0.000,
        "unemploymentRate": 3.4,   "jobGrowthRate": 3.2,
        "walkScore": 28,           "transitScore": 22,   "crimeIndex": 55,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 213,
        "populationM": 2.70,       "popGrowthRate": 21.3,
    },
    "19100": {  # Dallas, TX
        "medianHomePrice": 385000, "localTaxRate": 0.000,
        "unemploymentRate": 3.8,   "jobGrowthRate": 2.5,
        "walkScore": 38,           "transitScore": 35,   "crimeIndex": 62,
        "avgBenefitsValue": 15800, "sunDaysPerYear": 234,
        "populationM": 7.60,       "popGrowthRate": 20.5,
    },
    "21340": {  # El Paso, TX
        "medianHomePrice": 240000, "localTaxRate": 0.000,
        "unemploymentRate": 4.2,   "jobGrowthRate": 1.8,
        "walkScore": 38,           "transitScore": 25,   "crimeIndex": 42,
        "avgBenefitsValue": 13800, "sunDaysPerYear": 297,
        "populationM": 0.87,       "popGrowthRate": 5.5,
    },
    "26420": {  # Houston, TX
        "medianHomePrice": 310000, "localTaxRate": 0.000,
        "unemploymentRate": 4.2,   "jobGrowthRate": 2.8,
        "walkScore": 47,           "transitScore": 38,   "crimeIndex": 68,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 204,
        "populationM": 7.30,       "popGrowthRate": 16.5,
    },
    "27260": {  # Jacksonville, FL
        "medianHomePrice": 320000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 2.5,
        "walkScore": 28,           "transitScore": 18,   "crimeIndex": 62,
        "avgBenefitsValue": 14500, "sunDaysPerYear": 237,
        "populationM": 1.60,       "popGrowthRate": 15.8,
    },
    "28140": {  # Kansas City, MO
        "medianHomePrice": 285000, "localTaxRate": 0.010,
        "unemploymentRate": 3.5,   "jobGrowthRate": 1.8,
        "walkScore": 37,           "transitScore": 28,   "crimeIndex": 68,
        "avgBenefitsValue": 15200, "sunDaysPerYear": 215,
        "populationM": 2.20,       "popGrowthRate": 7.5,
    },
    "31140": {  # Louisville, KY
        "medianHomePrice": 255000, "localTaxRate": 0.022,
        "unemploymentRate": 3.8,   "jobGrowthRate": 1.5,
        "walkScore": 42,           "transitScore": 30,   "crimeIndex": 62,
        "avgBenefitsValue": 14800, "sunDaysPerYear": 201,
        "populationM": 1.40,       "popGrowthRate": 4.2,
    },
    "32820": {  # Memphis, TN
        "medianHomePrice": 195000, "localTaxRate": 0.000,
        "unemploymentRate": 4.5,   "jobGrowthRate": 1.2,
        "walkScore": 35,           "transitScore": 27,   "crimeIndex": 85,
        "avgBenefitsValue": 14200, "sunDaysPerYear": 217,
        "populationM": 1.40,       "popGrowthRate": 0.8,
    },
    "33100": {  # Miami, FL
        "medianHomePrice": 610000, "localTaxRate": 0.000,
        "unemploymentRate": 3.8,   "jobGrowthRate": 2.2,
        "walkScore": 77,           "transitScore": 60,   "crimeIndex": 65,
        "avgBenefitsValue": 16800, "sunDaysPerYear": 248,
        "populationM": 6.20,       "popGrowthRate": 11.8,
    },
    "34980": {  # Nashville, TN
        "medianHomePrice": 460000, "localTaxRate": 0.000,
        "unemploymentRate": 3.2,   "jobGrowthRate": 3.0,
        "walkScore": 28,           "transitScore": 22,   "crimeIndex": 62,
        "avgBenefitsValue": 15800, "sunDaysPerYear": 208,
        "populationM": 2.10,       "popGrowthRate": 21.8,
    },
    "35380": {  # New Orleans, LA
        "medianHomePrice": 250000, "localTaxRate": 0.000,
        "unemploymentRate": 4.5,   "jobGrowthRate": 1.2,
        "walkScore": 60,           "transitScore": 45,   "crimeIndex": 88,
        "avgBenefitsValue": 14500, "sunDaysPerYear": 204,
        "populationM": 1.30,       "popGrowthRate": -3.2,
    },
    "36420": {  # Oklahoma City, OK
        "medianHomePrice": 250000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 1.8,
        "walkScore": 32,           "transitScore": 20,   "crimeIndex": 65,
        "avgBenefitsValue": 14500, "sunDaysPerYear": 218,
        "populationM": 1.40,       "popGrowthRate": 8.5,
    },
    "36740": {  # Orlando, FL
        "medianHomePrice": 395000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 3.5,
        "walkScore": 42,           "transitScore": 28,   "crimeIndex": 62,
        "avgBenefitsValue": 15000, "sunDaysPerYear": 237,
        "populationM": 2.70,       "popGrowthRate": 22.8,
    },
    "39580": {  # Raleigh, NC
        "medianHomePrice": 440000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 3.5,
        "walkScore": 35,           "transitScore": 22,   "crimeIndex": 45,
        "avgBenefitsValue": 16000, "sunDaysPerYear": 213,
        "populationM": 1.40,       "popGrowthRate": 25.4,
    },
    "40060": {  # Richmond, VA
        "medianHomePrice": 360000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 2.0,
        "walkScore": 42,           "transitScore": 30,   "crimeIndex": 55,
        "avgBenefitsValue": 15800, "sunDaysPerYear": 214,
        "populationM": 1.30,       "popGrowthRate": 8.5,
    },
    "41700": {  # San Antonio, TX
        "medianHomePrice": 285000, "localTaxRate": 0.000,
        "unemploymentRate": 3.8,   "jobGrowthRate": 2.2,
        "walkScore": 37,           "transitScore": 30,   "crimeIndex": 60,
        "avgBenefitsValue": 14800, "sunDaysPerYear": 220,
        "populationM": 2.60,       "popGrowthRate": 13.5,
    },
    "45300": {  # Tampa, FL
        "medianHomePrice": 405000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 3.0,
        "walkScore": 50,           "transitScore": 35,   "crimeIndex": 55,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 246,
        "populationM": 3.30,       "popGrowthRate": 17.5,
    },
    # ── Northeast ─────────────────────────────────────────────────────────────
    "12580": {  # Baltimore, MD
        "medianHomePrice": 325000, "localTaxRate": 0.032,
        "unemploymentRate": 3.8,   "jobGrowthRate": 1.5,
        "walkScore": 67,           "transitScore": 55,   "crimeIndex": 75,
        "avgBenefitsValue": 17500, "sunDaysPerYear": 214,
        "populationM": 2.90,       "popGrowthRate": 1.8,
    },
    "14460": {  # Boston, MA
        "medianHomePrice": 620000, "localTaxRate": 0.000,
        "unemploymentRate": 3.2,   "jobGrowthRate": 1.8,
        "walkScore": 80,           "transitScore": 75,   "crimeIndex": 45,
        "avgBenefitsValue": 18800, "sunDaysPerYear": 202,
        "populationM": 4.90,       "popGrowthRate": 3.5,
    },
    "15380": {  # Buffalo, NY
        "medianHomePrice": 215000, "localTaxRate": 0.000,
        "unemploymentRate": 4.2,   "jobGrowthRate": 1.0,
        "walkScore": 58,           "transitScore": 42,   "crimeIndex": 62,
        "avgBenefitsValue": 15800, "sunDaysPerYear": 162,
        "populationM": 1.20,       "popGrowthRate": 0.5,
    },
    "25540": {  # Hartford, CT
        "medianHomePrice": 325000, "localTaxRate": 0.000,
        "unemploymentRate": 4.2,   "jobGrowthRate": 0.8,
        "walkScore": 55,           "transitScore": 42,   "crimeIndex": 60,
        "avgBenefitsValue": 18500, "sunDaysPerYear": 198,
        "populationM": 1.20,       "popGrowthRate": -0.8,
    },
    "35620": {  # New York, NY
        "medianHomePrice": 760000, "localTaxRate": 0.035,
        "unemploymentRate": 4.8,   "jobGrowthRate": 1.5,
        "walkScore": 88,           "transitScore": 85,   "crimeIndex": 55,
        "avgBenefitsValue": 22000, "sunDaysPerYear": 234,
        "populationM": 20.10,      "popGrowthRate": 0.2,
    },
    "37980": {  # Philadelphia, PA
        "medianHomePrice": 345000, "localTaxRate": 0.038,
        "unemploymentRate": 4.5,   "jobGrowthRate": 1.2,
        "walkScore": 78,           "transitScore": 67,   "crimeIndex": 72,
        "avgBenefitsValue": 18200, "sunDaysPerYear": 206,
        "populationM": 6.20,       "popGrowthRate": 1.5,
    },
    "38300": {  # Pittsburgh, PA
        "medianHomePrice": 225000, "localTaxRate": 0.030,
        "unemploymentRate": 3.8,   "jobGrowthRate": 1.2,
        "walkScore": 62,           "transitScore": 52,   "crimeIndex": 55,
        "avgBenefitsValue": 16500, "sunDaysPerYear": 160,
        "populationM": 2.40,       "popGrowthRate": 0.8,
    },
    "39300": {  # Providence, RI
        "medianHomePrice": 410000, "localTaxRate": 0.000,
        "unemploymentRate": 4.5,   "jobGrowthRate": 1.2,
        "walkScore": 62,           "transitScore": 45,   "crimeIndex": 55,
        "avgBenefitsValue": 16800, "sunDaysPerYear": 202,
        "populationM": 1.60,       "popGrowthRate": 2.5,
    },
    "47900": {  # Washington, DC
        "medianHomePrice": 620000, "localTaxRate": 0.000,
        "unemploymentRate": 4.0,   "jobGrowthRate": 1.5,
        "walkScore": 78,           "transitScore": 72,   "crimeIndex": 70,
        "avgBenefitsValue": 22000, "sunDaysPerYear": 203,
        "populationM": 6.40,       "popGrowthRate": 5.2,
    },
    # ── Midwest ───────────────────────────────────────────────────────────────
    "16980": {  # Chicago, IL
        "medianHomePrice": 340000, "localTaxRate": 0.000,
        "unemploymentRate": 4.5,   "jobGrowthRate": 1.2,
        "walkScore": 77,           "transitScore": 68,   "crimeIndex": 68,
        "avgBenefitsValue": 17200, "sunDaysPerYear": 189,
        "populationM": 9.50,       "popGrowthRate": -0.3,
    },
    "17140": {  # Cincinnati, OH
        "medianHomePrice": 280000, "localTaxRate": 0.018,
        "unemploymentRate": 3.8,   "jobGrowthRate": 1.8,
        "walkScore": 52,           "transitScore": 38,   "crimeIndex": 58,
        "avgBenefitsValue": 15200, "sunDaysPerYear": 186,
        "populationM": 2.30,       "popGrowthRate": 4.2,
    },
    "17460": {  # Cleveland, OH
        "medianHomePrice": 195000, "localTaxRate": 0.025,
        "unemploymentRate": 4.5,   "jobGrowthRate": 0.8,
        "walkScore": 55,           "transitScore": 42,   "crimeIndex": 72,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 166,
        "populationM": 2.00,       "popGrowthRate": -2.1,
    },
    "18140": {  # Columbus, OH
        "medianHomePrice": 285000, "localTaxRate": 0.025,
        "unemploymentRate": 3.8,   "jobGrowthRate": 2.2,
        "walkScore": 42,           "transitScore": 32,   "crimeIndex": 62,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 183,
        "populationM": 2.10,       "popGrowthRate": 11.5,
    },
    "19820": {  # Detroit, MI
        "medianHomePrice": 230000, "localTaxRate": 0.024,
        "unemploymentRate": 4.8,   "jobGrowthRate": 1.5,
        "walkScore": 55,           "transitScore": 38,   "crimeIndex": 78,
        "avgBenefitsValue": 16800, "sunDaysPerYear": 183,
        "populationM": 4.40,       "popGrowthRate": -0.5,
    },
    "26900": {  # Indianapolis, IN
        "medianHomePrice": 275000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 2.0,
        "walkScore": 33,           "transitScore": 25,   "crimeIndex": 65,
        "avgBenefitsValue": 14800, "sunDaysPerYear": 187,
        "populationM": 2.10,       "popGrowthRate": 9.8,
    },
    "29820": {  # Las Vegas, NV
        "medianHomePrice": 420000, "localTaxRate": 0.000,
        "unemploymentRate": 5.2,   "jobGrowthRate": 2.8,
        "walkScore": 42,           "transitScore": 38,   "crimeIndex": 70,
        "avgBenefitsValue": 14500, "sunDaysPerYear": 294,
        "populationM": 2.30,       "popGrowthRate": 15.1,
    },
    "33340": {  # Milwaukee, WI
        "medianHomePrice": 265000, "localTaxRate": 0.000,
        "unemploymentRate": 4.0,   "jobGrowthRate": 1.2,
        "walkScore": 62,           "transitScore": 45,   "crimeIndex": 68,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 188,
        "populationM": 1.60,       "popGrowthRate": 0.5,
    },
    "33460": {  # Minneapolis, MN
        "medianHomePrice": 360000, "localTaxRate": 0.000,
        "unemploymentRate": 3.2,   "jobGrowthRate": 1.8,
        "walkScore": 70,           "transitScore": 58,   "crimeIndex": 58,
        "avgBenefitsValue": 17800, "sunDaysPerYear": 198,
        "populationM": 3.70,       "popGrowthRate": 7.8,
    },
    "41180": {  # St. Louis, MO
        "medianHomePrice": 245000, "localTaxRate": 0.010,
        "unemploymentRate": 4.0,   "jobGrowthRate": 1.0,
        "walkScore": 55,           "transitScore": 40,   "crimeIndex": 78,
        "avgBenefitsValue": 15800, "sunDaysPerYear": 203,
        "populationM": 2.80,       "popGrowthRate": 1.5,
    },
    # ── West ──────────────────────────────────────────────────────────────────
    "19740": {  # Denver, CO
        "medianHomePrice": 555000, "localTaxRate": 0.000,
        "unemploymentRate": 3.5,   "jobGrowthRate": 2.0,
        "walkScore": 62,           "transitScore": 52,   "crimeIndex": 55,
        "avgBenefitsValue": 16500, "sunDaysPerYear": 300,
        "populationM": 2.90,       "popGrowthRate": 14.2,
    },
    "31080": {  # Los Angeles, CA
        "medianHomePrice": 800000, "localTaxRate": 0.000,
        "unemploymentRate": 5.2,   "jobGrowthRate": 1.2,
        "walkScore": 67,           "transitScore": 55,   "crimeIndex": 65,
        "avgBenefitsValue": 18200, "sunDaysPerYear": 284,
        "populationM": 13.20,      "popGrowthRate": -1.5,
    },
    "38060": {  # Phoenix, AZ
        "medianHomePrice": 430000, "localTaxRate": 0.000,
        "unemploymentRate": 3.8,   "jobGrowthRate": 3.2,
        "walkScore": 42,           "transitScore": 38,   "crimeIndex": 60,
        "avgBenefitsValue": 15500, "sunDaysPerYear": 299,
        "populationM": 5.00,       "popGrowthRate": 19.2,
    },
    "38900": {  # Portland, OR
        "medianHomePrice": 525000, "localTaxRate": 0.000,
        "unemploymentRate": 4.2,   "jobGrowthRate": 1.5,
        "walkScore": 67,           "transitScore": 58,   "crimeIndex": 65,
        "avgBenefitsValue": 17500, "sunDaysPerYear": 144,
        "populationM": 2.50,       "popGrowthRate": 5.8,
    },
    "40140": {  # Riverside, CA
        "medianHomePrice": 530000, "localTaxRate": 0.000,
        "unemploymentRate": 5.0,   "jobGrowthRate": 2.2,
        "walkScore": 32,           "transitScore": 22,   "crimeIndex": 55,
        "avgBenefitsValue": 16800, "sunDaysPerYear": 277,
        "populationM": 4.60,       "popGrowthRate": 7.8,
    },
    "40900": {  # Sacramento, CA
        "medianHomePrice": 495000, "localTaxRate": 0.000,
        "unemploymentRate": 4.5,   "jobGrowthRate": 1.8,
        "walkScore": 52,           "transitScore": 42,   "crimeIndex": 62,
        "avgBenefitsValue": 17500, "sunDaysPerYear": 273,
        "populationM": 2.40,       "popGrowthRate": 5.2,
    },
    "41620": {  # Salt Lake City, UT
        "medianHomePrice": 525000, "localTaxRate": 0.000,
        "unemploymentRate": 3.0,   "jobGrowthRate": 2.8,
        "walkScore": 62,           "transitScore": 48,   "crimeIndex": 48,
        "avgBenefitsValue": 15800, "sunDaysPerYear": 222,
        "populationM": 1.20,       "popGrowthRate": 14.8,
    },
    "41740": {  # San Diego, CA
        "medianHomePrice": 810000, "localTaxRate": 0.000,
        "unemploymentRate": 4.0,   "jobGrowthRate": 2.0,
        "walkScore": 52,           "transitScore": 42,   "crimeIndex": 45,
        "avgBenefitsValue": 18500, "sunDaysPerYear": 266,
        "populationM": 3.30,       "popGrowthRate": 3.8,
    },
    "41860": {  # San Francisco, CA
        "medianHomePrice": 1150000, "localTaxRate": 0.000,
        "unemploymentRate": 4.5,    "jobGrowthRate": 0.5,
        "walkScore": 88,            "transitScore": 80,  "crimeIndex": 72,
        "avgBenefitsValue": 22000,  "sunDaysPerYear": 259,
        "populationM": 4.70,        "popGrowthRate": -4.5,
    },
    "41940": {  # San Jose, CA
        "medianHomePrice": 1250000, "localTaxRate": 0.000,
        "unemploymentRate": 4.0,    "jobGrowthRate": 2.2,
        "walkScore": 55,            "transitScore": 45,  "crimeIndex": 52,
        "avgBenefitsValue": 22500,  "sunDaysPerYear": 257,
        "populationM": 2.00,        "popGrowthRate": -1.2,
    },
    "42660": {  # Seattle, WA
        "medianHomePrice": 780000, "localTaxRate": 0.000,
        "unemploymentRate": 4.2,   "jobGrowthRate": 2.5,
        "walkScore": 73,           "transitScore": 62,   "crimeIndex": 60,
        "avgBenefitsValue": 20500, "sunDaysPerYear": 152,
        "populationM": 4.10,       "popGrowthRate": 13.5,
    },
}

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


def reorder(city: dict) -> dict:
    """Return city dict with known fields first, then any extras alphabetically."""
    ordered = {}
    for k in FIELDS_ORDER:
        if k in city:
            ordered[k] = city[k]
    for k in sorted(city):
        if k not in ordered:
            ordered[k] = city[k]
    return ordered


def main():
    path = "public/data/cities.json"
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Run from project root.")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        cities = json.load(f)

    patched = 0
    skipped = 0
    for city in cities:
        cbsa = city["id"]
        if cbsa in SUPPLEMENTAL:
            city.update(SUPPLEMENTAL[cbsa])
            patched += 1
        else:
            print(f"  WARNING: no supplemental data for {city['name']} ({cbsa})")
            skipped += 1

    cities = [reorder(c) for c in cities]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cities, f, indent=2)

    print(f"\nDone. Patched {patched} cities, {skipped} skipped.")
    print(f"New fields added: medianHomePrice, localTaxRate, unemploymentRate,")
    print(f"  jobGrowthRate, walkScore, transitScore, crimeIndex,")
    print(f"  avgBenefitsValue, sunDaysPerYear, populationM, popGrowthRate")


if __name__ == "__main__":
    main()
