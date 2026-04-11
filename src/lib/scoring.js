import { purchasingPower, homePriceToIncomeRatio } from './calculations.js'

/**
 * Rank cities purely by purchasing power.
 */
export function rankCities(salaryFor, cities, housingMode = 'rent') {
  const scores = cities.map(c => ({ city: c, pp: purchasingPower(salaryFor(c), c, housingMode) }))
  return scores.sort((a, b) => b.pp - a.pp)
}

/**
 * Compute a composite livability score (0–100) for a city given a gross salary.
 *
 * Weights:
 *   40%  Financial (purchasing power + home affordability)
 *   20%  Job market (unemployment rate + job growth)
 *   15%  Walkability / transit (walk + transit score)
 *   15%  Safety (crime index, inverted)
 *   10%  Lifestyle (sun days + population growth proxy)
 *
 * All sub-scores are normalized 0–1 across the provided city set before weighting.
 */
export function cityScore(grossIncome, city, allCities, housingMode = 'rent') {
  const fin   = _financialScore(grossIncome, city, allCities, housingMode)
  const jobs  = _jobMarketScore(city, allCities)
  const walk  = _walkabilityScore(city)
  const safe  = _safetyScore(city, allCities)
  const life  = _lifestyleScore(city, allCities)

  const composite = fin * 0.40 + jobs * 0.20 + walk * 0.15 + safe * 0.15 + life * 0.10
  return Math.round(composite * 100)
}

/**
 * Rank cities by composite score.
 * Returns array of { city, score, pp, breakdown } sorted descending.
 */
export function rankCitiesByScore(salaryFor, cities, housingMode = 'rent') {
  return cities
    .map(c => {
      const gross = salaryFor(c)
      const pp    = purchasingPower(gross, c, housingMode)
      const score = cityScore(gross, c, cities, housingMode)
      return { city: c, score, pp }
    })
    .sort((a, b) => b.score - a.score)
}

// ── Sub-scorers ───────────────────────────────────────────────────────────────

function _financialScore(grossIncome, city, allCities, housingMode = 'rent') {
  const pp = purchasingPower(grossIncome, city, housingMode)
  const allPP = allCities.map(c => purchasingPower(grossIncome, c, housingMode))
  const ppScore = _normalize(pp, Math.min(...allPP), Math.max(...allPP))

  const hpRatio = homePriceToIncomeRatio(grossIncome, city)
  let affordScore = 0.5
  if (hpRatio !== null) {
    // Lower ratio = more affordable. Clamp 2–15x range.
    affordScore = _normalize(hpRatio, 15, 2) // inverted: 2x = best, 15x = worst
  }

  return ppScore * 0.7 + affordScore * 0.3
}

function _jobMarketScore(city, allCities) {
  // Lower unemployment = better; higher job growth = better
  const unempRates  = allCities.map(c => c.unemploymentRate ?? 4.0)
  const growthRates = allCities.map(c => c.jobGrowthRate ?? 1.5)

  const unempScore  = _normalize(city.unemploymentRate ?? 4.0, Math.max(...unempRates), Math.min(...unempRates)) // inverted
  const growthScore = _normalize(city.jobGrowthRate ?? 1.5, Math.min(...growthRates), Math.max(...growthRates))

  return unempScore * 0.5 + growthScore * 0.5
}

function _walkabilityScore(city) {
  // Walk Score and Transit Score are already 0–100
  const walk    = (city.walkScore    ?? 40) / 100
  const transit = (city.transitScore ?? 30) / 100
  return walk * 0.6 + transit * 0.4
}

function _safetyScore(city, allCities) {
  // crimeIndex: higher = more crime, so invert
  const rates = allCities.map(c => c.crimeIndex ?? 55)
  return _normalize(city.crimeIndex ?? 55, Math.max(...rates), Math.min(...rates))
}

function _lifestyleScore(city, allCities) {
  const sunValues    = allCities.map(c => c.sunDaysPerYear ?? 200)
  const growthValues = allCities.map(c => c.popGrowthRate  ?? 5)

  const sunScore    = _normalize(city.sunDaysPerYear ?? 200, Math.min(...sunValues), Math.max(...sunValues))
  const growthScore = _normalize(city.popGrowthRate  ?? 5,   Math.min(...growthValues), Math.max(...growthValues))

  return sunScore * 0.6 + growthScore * 0.4
}

/** Normalize val from [lo, hi] to [0, 1], clamped. */
function _normalize(val, lo, hi) {
  if (hi === lo) return 0.5
  return Math.max(0, Math.min(1, (val - lo) / (hi - lo)))
}
