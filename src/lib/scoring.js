import { purchasingPower, cityBreakdown } from './calculations.js'

// Weights: purchasingPower 60%, salaryGrowthProxy (colIndex inverted) 20%, rentBurden% 20%
export function cityScore(grossIncome, city) {
  const { aTax, rent } = cityBreakdown(grossIncome, city)
  const rentBurdenPct = rent / aTax  // lower is better
  const colPenalty = city.colIndex / 100 // higher colIndex = worse

  // Normalize: all scores are relative — caller should normalize across all cities
  return {
    cityId: city.id,
    ppScore: purchasingPower(grossIncome, city),
    rentBurdenScore: 1 - rentBurdenPct,
    colScore: 1 / colPenalty,
  }
}

export function rankCities(grossIncome, cities) {
  const scores = cities.map(c => ({ city: c, pp: purchasingPower(grossIncome, c) }))
  return scores.sort((a, b) => b.pp - a.pp)
}
