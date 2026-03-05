# AGENT BUILD SPEC — "Where Does Your Salary Go?"
# Interactive Data Visualization for Young Professionals
# Version: 1.0 | Format: AI Agent Instruction Document

---

## HOW TO READ THIS DOCUMENT

This is a complete, self-contained build specification for an AI coding agent.
Each section is labeled with its purpose. Follow sections in order.
All decisions are pre-made — do not ask for clarification unless a DECISION_REQUIRED tag appears.
When a section says "implement," write and execute the code immediately.

---

## SECTION 0: PROJECT IDENTITY

```
PROJECT_NAME: salary-story
OUTPUT_TYPE: Static single-page web application
FRAMEWORK: React 18 + Vite
STYLING: Tailwind CSS + custom CSS variables
CHARTS: D3.js v7
SCROLL_EVENTS: Scrollama (npm: scrollama)
DATA_PROCESSING: Pre-baked static JSON (no runtime API calls)
HOSTING_TARGET: Vercel or Netlify (static export)
ENTRY_FILE: index.html (Vite root)
MAIN_COMPONENT: src/App.jsx
```

---

## SECTION 1: FILE & FOLDER STRUCTURE

Create the following structure exactly. Do not add files not listed here unless a later section instructs it.

```
salary-story/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
├── public/
│   └── data/
│       └── cities.json          ← Pre-baked dataset (see Section 3)
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css                ← Global styles + CSS variables
│   ├── data/
│   │   └── occupations.js       ← Occupation list + BLS SOC codes
│   ├── lib/
│   │   ├── calculations.js      ← Tax, rent burden, purchasing power math
│   │   └── scoring.js           ← City match scoring function
│   ├── components/
│   │   ├── Intro.jsx            ← Occupation/salary intake screen
│   │   ├── Chapter1.jsx         ← Raw salary bar chart
│   │   ├── Chapter2.jsx         ← Deduction peel animation
│   │   ├── Chapter3.jsx         ← Re-ranked purchasing power chart
│   │   ├── Chapter4.jsx         ← Hidden gem city cards
│   │   ├── CityCompare.jsx      ← Persistent city comparison sidebar
│   │   ├── ResultCard.jsx       ← Shareable best-city-match card
│   │   ├── Tooltip.jsx          ← Reusable chart tooltip
│   │   └── Nav.jsx              ← Top navigation with occupation selector
│   └── hooks/
│       ├── useUserProfile.js    ← Global state: occupation, salary
│       └── useScrollama.js      ← Scrollama integration hook
├── scripts/
│   └── build-data.py            ← Data pipeline (see Section 3)
└── README.md
```

---

## SECTION 2: DEPENDENCY LIST

### package.json dependencies block (exact versions):

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "d3": "^7.9.0",
    "scrollama": "^3.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Install command:
```bash
npm create vite@latest salary-story -- --template react
cd salary-story
npm install d3 scrollama
npm install -D tailwindcss autoprefixer postcss
npx tailwindcss init -p
```

---

## SECTION 3: DATA SPECIFICATION

### 3.1 — cities.json Schema

The file at `public/data/cities.json` is an array of city objects.
Each object MUST conform to this exact schema:

```typescript
interface City {
  id: string;              // CBSA code as string, e.g. "35620"
  name: string;            // Display name, e.g. "New York, NY"
  short: string;           // Short label for charts, e.g. "NYC"
  state: string;           // Two-letter state code, e.g. "NY"
  region: string;          // One of: "Northeast" | "South" | "Midwest" | "West"
  stateTaxRate: number;    // Effective state+local income tax rate (decimal), e.g. 0.065
  medianRent1BR: number;   // Annual 1BR rent in USD (monthly * 12), e.g. 27600
  colIndex: number;        // ACCRA cost-of-living index, national avg = 100
  salaries: {
    [occupationCode: string]: number;  // BLS median annual wage by occ code
    // e.g. "15-1252": 135000
  };
}
```

### 3.2 — Minimum required cities (50 total):

```
Atlanta GA, Austin TX, Baltimore MD, Birmingham AL, Boston MA,
Buffalo NY, Charlotte NC, Chicago IL, Cincinnati OH, Cleveland OH,
Columbus OH, Dallas TX, Denver CO, Detroit MI, El Paso TX,
Hartford CT, Houston TX, Indianapolis IN, Jacksonville FL, Kansas City MO,
Las Vegas NV, Los Angeles CA, Louisville KY, Memphis TN, Miami FL,
Milwaukee WI, Minneapolis MN, Nashville TN, New Orleans LA, New York NY,
Oklahoma City OK, Orlando FL, Philadelphia PA, Phoenix AZ, Pittsburgh PA,
Portland OR, Providence RI, Raleigh NC, Richmond VA, Riverside CA,
Sacramento CA, Salt Lake City UT, San Antonio TX, San Diego CA,
San Francisco CA, San Jose CA, Seattle WA, St. Louis MO, Tampa FL,
Washington DC
```

### 3.3 — Seed data (use this hardcoded fallback if build-data.py cannot run)

Because the agent may not have network access, provide a hardcoded seed of 10 cities
with realistic 2024 figures in the cities.json file directly. The Python script
is provided for production data refresh only.

Hardcoded seed (10 cities, occupation code "15-1252" = Software Developers):

```json
[
  { "id":"41860","name":"San Francisco, CA","short":"SF","state":"CA","region":"West","stateTaxRate":0.093,"medianRent1BR":26400,"colIndex":178,"salaries":{"15-1252":168000,"11-1021":148000,"13-2011":112000,"29-1141":108000,"41-2031":42000} },
  { "id":"42660","name":"Seattle, WA","short":"SEA","state":"WA","region":"West","stateTaxRate":0.0,"medianRent1BR":22800,"colIndex":147,"salaries":{"15-1252":152000,"11-1021":138000,"13-2011":98000,"29-1141":99000,"41-2031":40000} },
  { "id":"35620","name":"New York, NY","short":"NYC","state":"NY","region":"Northeast","stateTaxRate":0.108,"medianRent1BR":28800,"colIndex":187,"salaries":{"15-1252":142000,"11-1021":155000,"13-2011":118000,"29-1141":115000,"41-2031":41000} },
  { "id":"16980","name":"Chicago, IL","short":"CHI","state":"IL","region":"Midwest","stateTaxRate":0.0495,"medianRent1BR":18000,"colIndex":116,"salaries":{"15-1252":112000,"11-1021":118000,"13-2011":88000,"29-1141":84000,"41-2031":36000} },
  { "id":"19100","name":"Dallas, TX","short":"DAL","state":"TX","region":"South","stateTaxRate":0.0,"medianRent1BR":16800,"colIndex":106,"salaries":{"15-1252":118000,"11-1021":122000,"13-2011":86000,"29-1141":78000,"41-2031":35000} },
  { "id":"12060","name":"Atlanta, GA","short":"ATL","state":"GA","region":"South","stateTaxRate":0.055,"medianRent1BR":16200,"colIndex":108,"salaries":{"15-1252":108000,"11-1021":114000,"13-2011":82000,"29-1141":72000,"41-2031":33000} },
  { "id":"38060","name":"Phoenix, AZ","short":"PHX","state":"AZ","region":"West","stateTaxRate":0.025,"medianRent1BR":15600,"colIndex":103,"salaries":{"15-1252":104000,"11-1021":108000,"13-2011":78000,"29-1141":74000,"41-2031":32000} },
  { "id":"26420","name":"Houston, TX","short":"HOU","state":"TX","region":"South","stateTaxRate":0.0,"medianRent1BR":15000,"colIndex":101,"salaries":{"15-1252":112000,"11-1021":116000,"13-2011":84000,"29-1141":76000,"41-2031":34000} },
  { "id":"33460","name":"Minneapolis, MN","short":"MSP","state":"MN","region":"Midwest","stateTaxRate":0.0785,"medianRent1BR":16200,"colIndex":112,"salaries":{"15-1252":110000,"11-1021":112000,"13-2011":86000,"29-1141":82000,"41-2031":37000} },
  { "id":"47900","name":"Washington, DC","short":"DC","state":"DC","region":"Northeast","stateTaxRate":0.085,"medianRent1BR":25200,"colIndex":152,"salaries":{"15-1252":138000,"11-1021":148000,"13-2011":108000,"29-1141":102000,"41-2031":44000} }
]
```

---

## SECTION 4: OCCUPATION LIST

### File: `src/data/occupations.js`

```javascript
export const OCCUPATIONS = [
  { code: "15-1252", label: "Software Developer / Engineer" },
  { code: "11-1021", label: "General & Operations Manager" },
  { code: "13-2011", label: "Accountant / Auditor" },
  { code: "29-1141", label: "Registered Nurse" },
  { code: "41-2031", label: "Retail Sales Worker" },
  { code: "23-1011", label: "Lawyer / Attorney" },
  { code: "25-2021", label: "Elementary School Teacher" },
  { code: "17-2141", label: "Mechanical Engineer" },
  { code: "27-1024", label: "Graphic Designer" },
  { code: "15-1211", label: "Computer Systems Analyst" },
  { code: "13-1161", label: "Market Research Analyst" },
  { code: "29-1051", label: "Pharmacist" },
  { code: "11-3031", label: "Financial Manager" },
  { code: "43-3031", label: "Bookkeeping / Accounting Clerk" },
  { code: "35-1012", label: "Food Service Manager" },
];

export const DEFAULT_OCCUPATION = "15-1252";
```

---

## SECTION 5: CALCULATION ENGINE

### File: `src/lib/calculations.js`

Implement these functions exactly as specified:

```javascript
// FEDERAL TAX: 2024 brackets, single filer
export function federalTax(grossIncome) {
  const brackets = [
    { min: 0,       max: 11600,  rate: 0.10 },
    { min: 11600,   max: 47150,  rate: 0.12 },
    { min: 47150,   max: 100525, rate: 0.22 },
    { min: 100525,  max: 191950, rate: 0.24 },
    { min: 191950,  max: 243725, rate: 0.32 },
    { min: 243725,  max: 609350, rate: 0.35 },
    { min: 609350,  max: Infinity, rate: 0.37 },
  ];
  let tax = 0;
  for (const b of brackets) {
    if (grossIncome <= b.min) break;
    tax += (Math.min(grossIncome, b.max) - b.min) * b.rate;
  }
  return Math.round(tax);
}

// STATE TAX: flat effective rate from city.stateTaxRate
export function stateTax(grossIncome, stateTaxRate) {
  return Math.round(grossIncome * stateTaxRate);
}

// FICA (Social Security + Medicare): 7.65% up to SS wage base
export function ficaTax(grossIncome) {
  const ssTax = Math.min(grossIncome, 168600) * 0.062;
  const medicareTax = grossIncome * 0.0145;
  return Math.round(ssTax + medicareTax);
}

// TOTAL TAX
export function totalTax(grossIncome, stateTaxRate) {
  return federalTax(grossIncome) + stateTax(grossIncome, stateTaxRate) + ficaTax(grossIncome);
}

// AFTER-TAX INCOME
export function afterTaxIncome(grossIncome, stateTaxRate) {
  return grossIncome - totalTax(grossIncome, stateTaxRate);
}

// RENT BURDEN (annual)
export function rentBurden(city) {
  return city.medianRent1BR; // already annual in schema
}

// COST OF LIVING ADJUSTED RESIDUAL
// residualIncome = afterTax - rent, then adjusted for non-rent CoL
export function purchasingPower(grossIncome, city) {
  const aTax = afterTaxIncome(grossIncome, city.stateTaxRate);
  const rent = rentBurden(city);
  const residual = aTax - rent;
  // Non-rent CoL: treat 60% of colIndex as the relevant multiplier for remaining spend
  const nonRentColMultiplier = 1 / (1 + (city.colIndex / 100 - 1) * 0.6);
  return Math.round(residual * nonRentColMultiplier);
}

// FULL BREAKDOWN for a city (used in tooltips and compare panel)
export function cityBreakdown(grossIncome, city) {
  const gross = grossIncome;
  const fedTax = federalTax(gross);
  const stTax = stateTax(gross, city.stateTaxRate);
  const fica = ficaTax(gross);
  const aTax = gross - fedTax - stTax - fica;
  const rent = rentBurden(city);
  const residual = aTax - rent;
  const pp = purchasingPower(gross, city);
  return { gross, fedTax, stTax, fica, aTax, rent, residual, pp };
}
```

### File: `src/lib/scoring.js`

```javascript
// Weights: purchasingPower 60%, salaryGrowthProxy (colIndex inverted) 20%, rentBurden% 20%
export function cityScore(grossIncome, city) {
  const { pp, aTax, rent } = cityBreakdown(grossIncome, city); // import cityBreakdown
  const rentBurdenPct = rent / aTax;  // lower is better
  const colPenalty = city.colIndex / 100; // higher colIndex = worse
  
  // Normalize: all scores are relative — caller should normalize across all cities
  return {
    cityId: city.id,
    ppScore: pp,
    rentBurdenScore: 1 - rentBurdenPct,
    colScore: 1 / colPenalty,
  };
}

export function rankCities(grossIncome, cities) {
  const scores = cities.map(c => ({ city: c, pp: purchasingPower(grossIncome, c) }));
  return scores.sort((a, b) => b.pp - a.pp);
}

// Import purchasingPower from calculations.js
import { purchasingPower, cityBreakdown } from './calculations.js';
```

---

## SECTION 6: GLOBAL STATE HOOK

### File: `src/hooks/useUserProfile.js`

Use React Context + useReducer for global state. Do NOT use Redux or Zustand.

```javascript
// State shape:
{
  occupation: { code: string, label: string },  // selected occupation
  salary: number | null,                         // null = use BLS median
  usingCustomSalary: boolean,
  pinnedCities: string[],                        // array of city IDs, max 3
  compareOpen: boolean,                           // sidebar visibility
}

// Actions:
// SET_OCCUPATION — payload: { code, label }
// SET_SALARY     — payload: number
// CLEAR_SALARY   — no payload, resets to BLS median
// PIN_CITY       — payload: cityId (max 3, ignore if already pinned)
// UNPIN_CITY     — payload: cityId
// TOGGLE_COMPARE — no payload
```

Provide a `useUserProfile()` hook that returns `[state, dispatch]`.
Wrap `<App />` in the context provider in `src/main.jsx`.

Helper selector: `export function getEffectiveSalary(state, cities)` —
returns `state.salary` if set, else looks up BLS median for `state.occupation.code`
from the provided cities array (use first city that has the occ code to get the median,
or return 75000 as fallback).

---

## SECTION 7: COMPONENT SPECIFICATIONS

Build each component in order. Each component spec includes: props, behavior, and D3/visual notes.

---

### 7.1 — `<Nav />`

**Props:** none (reads from useUserProfile context)

**Behavior:**
- Sticky top bar, always visible
- Left: project title "Salary Reality Check" in a serif font
- Center: occupation dropdown (populated from OCCUPATIONS list)
- Right: salary input field (optional, placeholder = "or enter yours")
  - Shows a small tag below if custom salary is active: "Using your salary · ✕"
  - Clicking ✕ clears back to BLS median
- On occupation change: dispatch SET_OCCUPATION, all charts re-render
- On salary input: debounce 400ms, dispatch SET_SALARY on valid number

---

### 7.2 — `<Intro />`

**Props:** `onComplete: () => void`

**Behavior:**
- Full-screen intake shown BEFORE the main story
- Headline: "Before we start, tell us about yourself"
- Occupation dropdown (same as Nav)
- Optional salary input with toggle "I'd rather use the national median"
- CTA button: "Show me the data →"
- On submit: calls onComplete(), Nav becomes visible, story begins
- Skip link: "Skip and use Software Developer median" (sets defaults and calls onComplete)

---

### 7.3 — `<Chapter1 />` — The Salary Illusion

**Props:** `cities: City[], effectiveSalary: number, occupationLabel: string`

**Visual:** Horizontal bar chart, sorted descending by the city's median salary for the selected occupation.

**D3 Implementation Notes:**
- SVG inside a div ref; use `useEffect` to mount/update D3
- X axis: dollar values, formatted with `d3.format("$,.0f")`
- Y axis: city short names
- Bars colored by region using this palette:
  ```
  West: #2c6fad, Northeast: #c0392b, South: #d4883a, Midwest: #4a9c6d
  ```
- On mount: bars animate from width=0 to full width over 800ms with staggered delays (index * 30ms)
- Tooltip on hover (use `<Tooltip />` component): show city name, gross salary, occupation
- If user has custom salary: add a vertical line marker at their salary with label "Your salary"
- Scrollama trigger: chapter enters viewport → trigger bar animation

**Narrative text panel (left column):**
```
Headline: "On paper, the numbers look great."
Body: "A software developer in San Francisco earns nearly $168,000 a year.
In Seattle, $152,000. These numbers are real. But they don't tell the
whole story — not even close."
```

---

### 7.4 — `<Chapter2 />` — Peeling Back the Layers

**Props:** `cities: City[], effectiveSalary: number`

**Visual:** Stacked horizontal bar chart showing salary broken into segments:
1. Federal tax (color: `#e74c3c`)
2. State + local tax (color: `#e67e22`)
3. FICA (color: `#f39c12`)
4. Rent (color: `#8e44ad`)
5. Remaining / purchasing residual (color: `#27ae60`)

**Scrollama Steps (4 steps, one text panel each):**
- Step 0: Show full salary bars only (Chapter 1 state)
- Step 1: Add federal tax segment — text: "First, the federal government takes its share."
- Step 2: Add state + FICA segments — text: "Then your state adds its own tax. Plus FICA."
- Step 3: Add rent segment — text: "Then there's rent. In high-cost cities, this is the killer."
- Step 4: Show only residual — text: "This is what you actually have left."

**D3 Implementation Notes:**
- Use `d3.stack()` on the breakdown data
- Each new segment animates in from the right edge of the previous segment
- Transition duration: 600ms ease-in-out per step
- Cities sorted by residual income in Step 4 (re-sort with animated transition)
- Show city labels in both sorted orders to make the rank change visible

---

### 7.5 — `<Chapter3 />` — The Real Ranking

**Props:** `cities: City[], effectiveSalary: number`

**Visual:** Horizontal bar chart, re-ranked by `purchasingPower()` value.

**Behavior:**
- On chapter enter: animate bars from Chapter 2's order to new purchasing-power order
- Use D3 data join with key = city.id so bars physically move (translate Y) during re-sort
- Transition: 1000ms, ease cubic-in-out, staggered by 50ms per bar
- Bars now show the `purchasingPower()` value (not gross salary)
- Color bars by their rank change: green if they moved up, red if moved down, gray if same
- Add delta indicator on each bar: "▲ 8 spots" or "▼ 12 spots"
- Highlight the top 5 with a subtle gold left border

**Narrative text:**
```
Headline: "The leaderboard just flipped."
Body: "After taxes, rent, and the real cost of living, the cities that
looked richest on paper are no longer at the top. Some mid-sized
cities you may have never considered are suddenly looking very attractive."
```

---

### 7.6 — `<Chapter4 />` — Hidden Gem Spotlight

**Props:** `cities: City[], effectiveSalary: number, occupation: Occupation`

**Behavior:**
- Use `rankCities()` to get sorted list
- Filter to cities ranked 3–10 in purchasing power that are NOT in the top 5 by gross salary
  (these are the "hidden gems" — high value, not obvious choices)
- Display top 3 of these as "City Cards"

**City Card design (per card):**
```
┌──────────────────────────────┐
│ 🏙  Austin, TX               │
│ ──────────────────────────── │
│ Gross Salary      $118,000   │
│ After-Tax         $89,200    │
│ Rent (annual)    -$16,800    │
│ Purchasing Power  $61,400    │
│ ──────────────────────────── │
│ Rank: #4 in real value       │
│ vs. San Francisco: +$18,200  │
│                              │
│  [Compare]   [Share ↗]       │
└──────────────────────────────┘
```

**Share button behavior:**
- Construct URL: `?occ=15-1252&salary=118000&city=19100`
- Copy to clipboard + show "Copied!" toast
- Also generate a text snippet: "My $118k salary goes $18,200 further in Austin than SF — see for yourself: [URL]"

---

### 7.7 — `<CityCompare />`

**Props:** none (reads pinnedCities from context)

**Behavior:**
- Fixed right sidebar, width 320px, toggled by `compareOpen` state
- Header: "Compare Cities (up to 3)"
- For each pinned city: show full `cityBreakdown()` as a vertical waterfall table
- Remove button (×) per city
- "Add a city" dropdown of all 50 cities not yet pinned
- Bottom: "Best value among these: [City Name]" — highlights the winner

---

### 7.8 — `<Tooltip />`

**Props:** `visible: boolean, x: number, y: number, content: object`

Render as a fixed-position div (not SVG foreignObject).
Position relative to the chart container using a portal (ReactDOM.createPortal to body).
Auto-flip horizontally if within 200px of right edge of viewport.

---

## SECTION 8: SCROLL MECHANICS

### File: `src/hooks/useScrollama.js`

```javascript
// Returns: currentStep (number), ref to attach to scroll container
import { useEffect, useRef, useState } from 'react';
import scrollama from 'scrollama';

export function useScrollama(stepCount, offset = 0.5) {
  const containerRef = useRef(null);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const scroller = scrollama();
    scroller
      .setup({ step: '.scroll-step', offset, debug: false })
      .onStepEnter(({ index }) => setCurrentStep(index))
      .onStepExit(({ index, direction }) => {
        if (direction === 'up' && index === 0) setCurrentStep(-1);
      });
    return () => scroller.destroy();
  }, []);

  return { currentStep, containerRef };
}
```

**Layout pattern for each scrollytelling chapter:**
```jsx
<div className="chapter-container" style={{ position: 'relative' }}>
  {/* Sticky chart panel */}
  <div style={{ position: 'sticky', top: '80px', height: 'calc(100vh - 80px)' }}>
    <ChartComponent step={currentStep} />
  </div>
  {/* Scrolling text steps */}
  <div className="steps-container">
    {steps.map((step, i) => (
      <div key={i} className="scroll-step" style={{ minHeight: '100vh', padding: '40vh 0' }}>
        <div className="text-panel">{step.text}</div>
      </div>
    ))}
  </div>
</div>
```

---

## SECTION 9: STYLING SYSTEM

### File: `src/index.css`

Define these CSS custom properties at `:root`:

```css
:root {
  --color-ink: #0f0f0f;
  --color-paper: #fafaf7;
  --color-muted: #6b6560;
  --color-accent: #c0392b;
  --color-gold: #b8922a;
  --color-rule: rgba(15,15,15,0.1);

  /* Chart colors */
  --chart-west: #2c6fad;
  --chart-northeast: #c0392b;
  --chart-south: #d4883a;
  --chart-midwest: #4a9c6d;
  --chart-federal: #e74c3c;
  --chart-state: #e67e22;
  --chart-fica: #f39c12;
  --chart-rent: #8e44ad;
  --chart-residual: #27ae60;

  /* Typography */
  --font-display: 'Playfair Display', Georgia, serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'DM Mono', 'Fira Code', monospace;
}
```

Add these Google Fonts to `index.html` `<head>`:
```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Tailwind config additions (`tailwind.config.js`):
```javascript
module.exports = {
  content: ['./index.html', './src/**/*.{jsx,js}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Playfair Display', 'Georgia', 'serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['DM Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        ink: '#0f0f0f',
        paper: '#fafaf7',
        accent: '#c0392b',
        gold: '#b8922a',
      }
    }
  }
}
```

---

## SECTION 10: APP ASSEMBLY

### File: `src/App.jsx`

**State:**
- `introComplete: boolean` — controls whether to show `<Intro />` or the main story
- `cities: City[]` — loaded from `/data/cities.json` via `useEffect` on mount
- `loading: boolean` — true while fetching cities.json

**Render logic:**
```
if loading → show full-screen loading state ("Loading salary data...")
if !introComplete → show <Intro onComplete={() => setIntroComplete(true)} />
else → show <Nav /> + all four chapter components in a vertical scroll layout
      + <CityCompare /> sidebar (conditionally rendered based on compareOpen state)
```

**Chapter layout order:**
1. `<Chapter1 />` — with scroll trigger
2. `<Chapter2 />` — with 4-step scrollama
3. `<Chapter3 />` — with animated re-sort
4. `<Chapter4 />` — city cards + result

**URL parameter handling (on mount):**
- Parse `?occ=CODE&salary=NUMBER` from `window.location.search`
- If present, pre-fill occupation and salary, skip Intro, jump directly to Chapter 4
- This enables the share links from Chapter 4 to work

---

## SECTION 11: RESPONSIVE BEHAVIOR

### Breakpoints:
- `< 768px` (mobile): Replace sticky scroll layout with tabbed stepper
  - "Previous" / "Next" buttons advance the chapter step
  - Chart takes full screen width, text panel below chart
  - CityCompare becomes a bottom drawer instead of sidebar
- `768px–1024px` (tablet): Sticky layout works but reduce chart font sizes
- `>1024px` (desktop): Full sticky side-by-side layout

---

## SECTION 12: PYTHON DATA PIPELINE (OPTIONAL / PRODUCTION)

### File: `scripts/build-data.py`

This script is for production data freshness. It is NOT required for the initial build.
The agent should create this file but does not need to execute it.

```python
"""
build-data.py — Fetches and joins salary, rent, tax, and CoL data into cities.json
Run: python scripts/build-data.py
Output: public/data/cities.json
Requires: pip install pandas requests python-dotenv
"""

# STEP 1: Load BLS OEWS data (download from https://www.bls.gov/oes/tables.htm)
# File: national_M{YEAR}_dl.xlsx or metro area files
# Filter to occupation codes in OCCUPATIONS list
# Group by CBSA code, take median annual wage per occupation

# STEP 2: Load Zillow ZORI data (from https://www.zillow.com/research/data/)
# File: Metro_zori_uc_sfrcondomfr_sm_month.csv
# Take most recent month, convert monthly to annual (* 12)
# Join on metro area name (fuzzy match to CBSA name if needed)

# STEP 3: Tax Foundation state rates
# Hardcode effective rates per state from https://taxfoundation.org/data/all/state/
# (These change annually but infrequently — hardcode is acceptable)

# STEP 4: ACCRA / C2ER Cost of Living Index
# Purchase from C2ER or use MIT Living Wage as proxy
# Join on metro area

# STEP 5: Join all datasets on CBSA code
# Drop cities missing salary data for more than 5 occupation codes
# Round all dollar values to nearest $100
# Output to public/data/cities.json

print("Data pipeline — implement joins here")
```

---

## SECTION 13: PERFORMANCE REQUIREMENTS

The agent must verify these after the initial build is complete:

1. `cities.json` must be < 200KB uncompressed (achieve by rounding values, removing unused fields)
2. All D3 transitions must complete in < 1200ms (enforce via transition duration caps)
3. No chart should render more than 600 SVG elements simultaneously
4. Occupation change must re-render all charts in < 300ms (pre-compute all values on load, not on interaction)
5. The Intro screen must be interactive in < 1 second (no data loading on this screen)

---

## SECTION 14: ACCESSIBILITY REQUIREMENTS

1. All SVG bar elements must have `role="img"` and `aria-label` with their full data value
2. Color is never the sole differentiator — add pattern fills or data labels to all charts
3. All interactive elements (dropdowns, buttons, bars) must be keyboard-focusable with visible focus rings
4. Tooltip content must be duplicated in a visually-hidden `<span>` for screen readers
5. Contrast ratio for all text on chart backgrounds must pass WCAG AA (4.5:1)

---

## SECTION 15: BUILD & DEPLOY

### Development:
```bash
npm run dev
```

### Production build:
```bash
npm run build
# Output: dist/ folder — deploy to Vercel or Netlify as static site
```

### Vercel deploy (one command):
```bash
npx vercel --prod
```

### Environment variables needed: NONE
All data is static. No API keys required.

---

## SECTION 16: COMPLETION CHECKLIST

The agent should verify each item before declaring the build complete:

- [ ] cities.json loads without errors and contains ≥ 10 cities
- [ ] Occupation dropdown changes update all four chapters
- [ ] Custom salary input overrides BLS median in all calculations
- [ ] Chapter 2 shows all 5 scroll steps (federal, state, FICA, rent, residual)
- [ ] Chapter 3 animated re-sort plays correctly (bars change position)
- [ ] Chapter 4 shows 3 city cards with correct breakdown numbers
- [ ] Share link correctly encodes occupation + salary in URL params
- [ ] URL params on load correctly restore shared state
- [ ] City compare sidebar opens/closes and shows up to 3 cities
- [ ] Mobile layout uses stepper, not sticky scroll
- [ ] All calculations match manual verification:
  - SF Software Dev ($168k): fedTax ≈ $36k, stateTax ≈ $15.6k, FICA ≈ $11.5k, rent ≈ $26.4k, residual ≈ $78.5k
  - Dallas Software Dev ($118k): fedTax ≈ $23.3k, stateTax = $0, FICA ≈ $9.8k, rent ≈ $16.8k, residual ≈ $68.1k
- [ ] No console errors in production build
- [ ] Lighthouse Performance score > 85

---

## END OF SPEC

This document is the single source of truth for the build.
All implementation decisions are pre-made.
Begin with SECTION 1 (file structure), proceed in order through SECTION 16.
```