import { purchasingPower, cityBreakdown } from './calculations.js'

// Weights: purchasingPower 60%, salaryGrowthProxy (colIndex inverted) 20%, rentBurden% 20%
export function rankCities(salaryFor, cities) {
  const scores = cities.map(c => ({ city: c, pp: purchasingPower(salaryFor(c), c) }))
  return scores.sort((a, b) => b.pp - a.pp)
}
