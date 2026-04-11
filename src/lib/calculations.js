// FEDERAL TAX: 2024 brackets, single filer
export function federalTax(grossIncome) {
  const brackets = [
    [11600,   0.10],
    [47150,   0.12],
    [100525,  0.22],
    [191950,  0.24],
    [243725,  0.32],
    [609350,  0.35],
    [Infinity, 0.37],
  ]
  return calcBracketTax(grossIncome, brackets)
}

// ── STATE TAX BRACKETS 2024 (single filer) ───────────────────────────────────
// Format: [[upperLimit, marginalRate], ...]
// Rate applies to income between the previous limit (or 0) and upperLimit.
const STATE_BRACKETS = {
  // ── No income tax ──────────────────────────────────────────────────────────
  AK: [], FL: [], NV: [], NH: [], SD: [], TN: [], TX: [], WA: [], WY: [],

  // ── Flat rates ─────────────────────────────────────────────────────────────
  AZ: [[Infinity, 0.0250]],  // Arizona: 2.5% flat (2023+)
  CO: [[Infinity, 0.0440]],  // Colorado: 4.4% flat (2024)
  GA: [[Infinity, 0.0549]],  // Georgia: 5.49% flat (2024 reform)
  IA: [[Infinity, 0.0440]],  // Iowa: simplified to ~4.4% (phasing to flat by 2026)
  ID: [[Infinity, 0.0580]],  // Idaho: 5.8% flat (2024)
  IL: [[Infinity, 0.0495]],  // Illinois: 4.95% flat
  IN: [[Infinity, 0.0305]],  // Indiana: 3.05% flat (2024)
  KY: [[Infinity, 0.0400]],  // Kentucky: 4.0% flat (2024)
  MI: [[Infinity, 0.0425]],  // Michigan: 4.25% flat
  NC: [[Infinity, 0.0475]],  // North Carolina: 4.75% flat (2024)
  PA: [[Infinity, 0.0307]],  // Pennsylvania: 3.07% flat
  UT: [[Infinity, 0.0455]],  // Utah: 4.55% flat (2024)

  // Massachusetts: 5% flat + 4% millionaire surtax on income over $1M
  MA: [[1_000_000, 0.0500], [Infinity, 0.0900]],

  // ── Progressive rates ──────────────────────────────────────────────────────

  // Alabama: 2% / 4% / 5%
  AL: [[500, 0.0200], [3_000, 0.0400], [Infinity, 0.0500]],

  // Arkansas: top rate 4.4% (2024 reduction)
  AR: [[5_000, 0.0200], [10_000, 0.0400], [Infinity, 0.0440]],

  // California: 1%–13.3% (10 brackets)
  CA: [
    [10_412,   0.0100],
    [24_684,   0.0200],
    [39_014,   0.0400],
    [54_081,   0.0600],
    [68_350,   0.0800],
    [349_137,  0.0930],
    [418_961,  0.1030],
    [698_271,  0.1130],
    [1_000_000, 0.1230],
    [Infinity, 0.1330],
  ],

  // Connecticut: 2%–6.99%
  CT: [
    [10_000,  0.0200],
    [50_000,  0.0450],
    [100_000, 0.0550],
    [200_000, 0.0600],
    [250_000, 0.0650],
    [500_000, 0.0690],
    [Infinity, 0.0699],
  ],

  // Washington DC: 4%–10.75%
  DC: [
    [10_000,   0.0400],
    [40_000,   0.0600],
    [60_000,   0.0650],
    [250_000,  0.0850],
    [500_000,  0.0925],
    [1_000_000, 0.0975],
    [Infinity, 0.1075],
  ],

  // Kansas: 3.1% / 5.25% / 5.7%
  KS: [[15_000, 0.0310], [30_000, 0.0525], [Infinity, 0.0570]],

  // Louisiana: 1.85% / 3.5% / 4.25% (2024; reform effective 2025)
  LA: [[12_500, 0.0185], [50_000, 0.0350], [Infinity, 0.0425]],

  // Maryland: 2%–5.75%
  MD: [
    [1_000,   0.0200],
    [2_000,   0.0300],
    [3_000,   0.0400],
    [100_000, 0.0475],
    [125_000, 0.0500],
    [150_000, 0.0525],
    [250_000, 0.0550],
    [Infinity, 0.0575],
  ],

  // Minnesota: 5.35% / 6.8% / 7.85% / 9.85%
  MN: [
    [30_070,  0.0535],
    [98_760,  0.0680],
    [183_340, 0.0785],
    [Infinity, 0.0985],
  ],

  // Missouri: graduated, top 4.95%
  MO: [
    [1_073,  0.0150],
    [2_146,  0.0200],
    [3_219,  0.0250],
    [4_292,  0.0300],
    [5_365,  0.0350],
    [6_438,  0.0400],
    [9_072,  0.0450],
    [Infinity, 0.0495],
  ],

  // Nebraska: 2.46% / 3.51% / 5.01% / 5.84%
  NE: [
    [3_700,  0.0246],
    [22_170, 0.0351],
    [35_730, 0.0501],
    [Infinity, 0.0584],
  ],

  // New Jersey: 1.4%–10.75%
  NJ: [
    [20_000,   0.0140],
    [35_000,   0.0175],
    [40_000,   0.0350],
    [75_000,   0.05525],
    [500_000,  0.0637],
    [1_000_000, 0.0897],
    [Infinity, 0.1075],
  ],

  // New Mexico: 1.7%–5.9%
  NM: [
    [5_500,   0.0170],
    [11_000,  0.0320],
    [16_000,  0.0470],
    [210_000, 0.0490],
    [Infinity, 0.0590],
  ],

  // New York: 4%–10.9%
  NY: [
    [8_500,     0.0400],
    [11_700,    0.0450],
    [13_900,    0.0525],
    [21_400,    0.0585],
    [80_650,    0.0625],
    [215_400,   0.0685],
    [1_077_550, 0.0965],
    [5_000_000, 0.1030],
    [Infinity,  0.1090],
  ],

  // Ohio: 0% up to $26,050; 2.75% up to $100,000; 3.5% above
  OH: [
    [26_050,  0.0000],
    [100_000, 0.0275],
    [Infinity, 0.0350],
  ],

  // Oklahoma: 0.5%–4.75%
  OK: [
    [1_000,  0.0050],
    [2_500,  0.0100],
    [3_750,  0.0200],
    [4_900,  0.0300],
    [7_200,  0.0400],
    [Infinity, 0.0475],
  ],

  // Oregon: 4.75%–9.9%
  OR: [
    [18_400,  0.0475],
    [46_200,  0.0675],
    [250_000, 0.0875],
    [Infinity, 0.0990],
  ],

  // Rhode Island: 3.75% / 4.75% / 5.99%
  RI: [
    [77_450,  0.0375],
    [176_050, 0.0475],
    [Infinity, 0.0599],
  ],

  // South Carolina: 0%–6.4% (post-reform 2024)
  SC: [
    [3_199,  0.0000],
    [6_409,  0.0300],
    [9_619,  0.0400],
    [12_819, 0.0500],
    [16_039, 0.0600],
    [Infinity, 0.0640],
  ],

  // Virginia: 2%–5.75%
  VA: [
    [3_000,  0.0200],
    [5_000,  0.0300],
    [17_000, 0.0500],
    [Infinity, 0.0575],
  ],

  // Wisconsin: 3.54% / 4.65% / 5.3% / 7.65%
  WI: [
    [13_810,  0.0354],
    [27_630,  0.0465],
    [304_170, 0.0530],
    [Infinity, 0.0765],
  ],
}

// Walk bracket table and compute tax owed
function calcBracketTax(income, brackets) {
  if (!brackets || brackets.length === 0) return 0
  let tax = 0
  let prev = 0
  for (const [limit, rate] of brackets) {
    if (income <= prev) break
    tax += (Math.min(income, limit) - prev) * rate
    prev = limit
    if (limit === Infinity) break
  }
  return Math.round(tax)
}

// STATE TAX: progressive brackets keyed by two-letter state code
export function stateTax(grossIncome, state) {
  const brackets = STATE_BRACKETS[state] ?? []
  return calcBracketTax(grossIncome, brackets)
}

// Effective state tax rate at a given income (for display)
export function stateEffectiveRate(grossIncome, state) {
  if (!grossIncome) return 0
  return stateTax(grossIncome, state) / grossIncome
}

// LOCAL TAX: city/county income or wage tax (0 for most cities)
export function localTax(grossIncome, localTaxRate) {
  return Math.round(grossIncome * (localTaxRate || 0))
}

// ── HOUSING COST ─────────────────────────────────────────────────────────────
// 30-year fixed rate mortgage (2025 market rate)
const MORTGAGE_RATE_30YR = 0.070
const DOWN_PAYMENT_PCT   = 0.20   // 20% down assumed

// Annual mortgage payment on (1 - DOWN_PAYMENT_PCT) of homePrice
export function annualMortgage(homePrice) {
  if (!homePrice) return 0
  const principal = homePrice * (1 - DOWN_PAYMENT_PCT)
  const r = MORTGAGE_RATE_30YR / 12
  const n = 360
  const monthly = principal * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1)
  return Math.round(monthly * 12)
}

// Annual property tax estimate (1.1% of home value, national avg)
export function annualPropertyTax(homePrice) {
  return Math.round((homePrice || 0) * 0.011)
}

// Total annual housing cost — rent or buy
// mode: 'rent' | 'buy'
export function annualHousingCost(city, mode = 'rent') {
  if (mode === 'buy') {
    return annualMortgage(city.medianHomePrice) + annualPropertyTax(city.medianHomePrice)
  }
  return city.medianRent1BR
}

// FICA (Social Security + Medicare): 7.65% up to SS wage base
export function ficaTax(grossIncome) {
  const ssTax = Math.min(grossIncome, 168600) * 0.062
  const medicareTax = grossIncome * 0.0145
  return Math.round(ssTax + medicareTax)
}

// TOTAL TAX
export function totalTax(grossIncome, city) {
  return (
    federalTax(grossIncome) +
    stateTax(grossIncome, city.state) +
    localTax(grossIncome, city.localTaxRate) +
    ficaTax(grossIncome)
  )
}

// AFTER-TAX INCOME
export function afterTaxIncome(grossIncome, city) {
  return grossIncome - totalTax(grossIncome, city)
}

// HOUSING BURDEN (annual) — rent or mortgage+tax
export function rentBurden(city, mode = 'rent') {
  return annualHousingCost(city, mode)
}

// COST OF LIVING ADJUSTED RESIDUAL
// residualIncome = afterTax - housing, then adjusted for non-housing CoL
export function purchasingPower(grossIncome, city, mode = 'rent') {
  const aTax = afterTaxIncome(grossIncome, city)
  const housing = annualHousingCost(city, mode)
  const residual = aTax - housing
  // Non-housing CoL: treat 60% of colIndex as the relevant multiplier for remaining spend
  const nonRentColMultiplier = 1 / (1 + (city.colIndex / 100 - 1) * 0.6)
  return Math.round(residual * nonRentColMultiplier)
}

// HOME PRICE TO INCOME RATIO (years of gross salary to buy median home)
export function homePriceToIncomeRatio(grossIncome, city) {
  if (!city.medianHomePrice || grossIncome <= 0) return null
  return +(city.medianHomePrice / grossIncome).toFixed(1)
}

// EFFECTIVE TOTAL TAX RATE
export function effectiveTaxRate(grossIncome, city) {
  return totalTax(grossIncome, city) / grossIncome
}

// FULL BREAKDOWN for a city (used in tooltips and compare panel)
// mode: 'rent' | 'buy'
export function cityBreakdown(grossIncome, city, mode = 'rent') {
  const gross = grossIncome
  const fedTax = federalTax(gross)
  const stTax = stateTax(gross, city.state)
  const locTax = localTax(gross, city.localTaxRate)
  const fica = ficaTax(gross)
  const aTax = gross - fedTax - stTax - locTax - fica
  const rent = annualHousingCost(city, mode)
  const residual = aTax - rent
  const pp = purchasingPower(gross, city, mode)
  const hpRatio = homePriceToIncomeRatio(gross, city)
  return { gross, fedTax, stTax, locTax, fica, aTax, rent, residual, pp, hpRatio }
}

// BREAK-EVEN SALARY: find gross income in destCity that yields the same
// purchasing power as sourcePP. Returns null if unachievable below $2M.
export function breakEvenSalary(sourcePP, destCity, mode = 'rent') {
  if (sourcePP <= 0) return null
  let lo = 0, hi = 2_000_000
  // Quick check: is $2M enough?
  if (purchasingPower(hi, destCity, mode) < sourcePP) return null
  for (let i = 0; i < 64; i++) {
    const mid = (lo + hi) / 2
    if (purchasingPower(mid, destCity, mode) < sourcePP) lo = mid
    else hi = mid
  }
  return Math.round(hi / 100) * 100  // round to nearest $100
}

// FORMAT helper
export function fmt(n) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}

// FORMAT compact (e.g. $1.2M, $85K)
export function fmtCompact(n) {
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (Math.abs(n) >= 1_000) return `$${Math.round(n / 1_000)}K`
  return fmt(n)
}
