# Salary Reality Check

A scrollytelling data visualization that shows what your salary actually buys across 50 US metro areas — after taxes, rent, and cost of living.

# Github Pages Link
<https://lukesahlin.github.io/Salary-Reality-Check/>

## What it does

Enter your occupation and salary. The app walks you through four chapters:

1. How your pay compares to local medians across 50 cities
2. What gets taken out — federal tax, state tax, FICA, and rent
3. How cities re-rank once purchasing power is accounted for
4. Hidden gems: cities that punch above their weight

## Data sources

- **Salaries**: BLS Occupational Employment and Wage Statistics (OEWS) 2024
- **Rent**: Zillow Observed Rent Index (ZORI), latest available
- **Cost of living**: Numbeo index (hardcoded from 2024 survey)
- **Taxes**: Federal brackets (2024), state income tax rates (hardcoded)
- **Living wage**: MIT Living Wage Calculator / HUD Fair Market Rents

## Setup

### 1. Generate the data

Requires Python 3.10+ and the following packages:

```
pip install requests pandas openpyxl beautifulsoup4 rapidfuzz
```

Run the pipeline:

```
python scripts/download_data.py
```

This downloads BLS and Zillow data, applies tax and CoL data, and writes `public/data/cities.json`.

### 2. Install dependencies

```
npm install
```

### 3. Run the dev server

```
npm run dev
```

Open `http://localhost:5173`.

### 4. Build for production

```
npm run build
```

Output goes to `dist/`. Deploy as a static site.

## Tech stack

- React 18 + Vite 5
- D3.js v7 (all charts)
- Scrollama (scroll-triggered steps)
- Tailwind CSS

## URL params

Results are shareable. The URL supports:

- `?occ=15-1252` — preselects an occupation (BLS SOC code)
- `?salary=95000` — presets a salary and skips the intro form

Example: `/?occ=29-1141&salary=80000`
