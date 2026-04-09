// FEDERAL TAX: 2024 brackets, single filer
export function federalTax(grossIncome) {
  const brackets = [
    { min: 0,       max: 11600,   rate: 0.10 },
    { min: 11600,   max: 47150,   rate: 0.12 },
    { min: 47150,   max: 100525,  rate: 0.22 },
    { min: 100525,  max: 191950,  rate: 0.24 },
    { min: 191950,  max: 243725,  rate: 0.32 },
    { min: 243725,  max: 609350,  rate: 0.35 },
    { min: 609350,  max: Infinity, rate: 0.37 },
  ]
  let tax = 0
  for (const b of brackets) {
    if (grossIncome <= b.min) break
    tax += (Math.min(grossIncome, b.max) - b.min) * b.rate
  }
  return Math.round(tax)
}

// STATE TAX: flat effective rate from city.stateTaxRate
export function stateTax(grossIncome, stateTaxRate) {
  return Math.round(grossIncome * stateTaxRate)
}

// LOCAL TAX: city/county income or wage tax (0 for most cities)
export function localTax(grossIncome, localTaxRate) {
  return Math.round(grossIncome * (localTaxRate || 0))
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
    stateTax(grossIncome, city.stateTaxRate) +
    localTax(grossIncome, city.localTaxRate) +
    ficaTax(grossIncome)
  )
}

// AFTER-TAX INCOME
export function afterTaxIncome(grossIncome, city) {
  return grossIncome - totalTax(grossIncome, city)
}

// RENT BURDEN (annual)
export function rentBurden(city) {
  return city.medianRent1BR // already annual in schema
}

// COST OF LIVING ADJUSTED RESIDUAL
// residualIncome = afterTax - rent, then adjusted for non-rent CoL
export function purchasingPower(grossIncome, city) {
  const aTax = afterTaxIncome(grossIncome, city)
  const rent = rentBurden(city)
  const residual = aTax - rent
  // Non-rent CoL: treat 60% of colIndex as the relevant multiplier for remaining spend
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
export function cityBreakdown(grossIncome, city) {
  const gross = grossIncome
  const fedTax = federalTax(gross)
  const stTax = stateTax(gross, city.stateTaxRate)
  const locTax = localTax(gross, city.localTaxRate)
  const fica = ficaTax(gross)
  const aTax = gross - fedTax - stTax - locTax - fica
  const rent = rentBurden(city)
  const residual = aTax - rent
  const pp = purchasingPower(gross, city)
  const hpRatio = homePriceToIncomeRatio(gross, city)
  return { gross, fedTax, stTax, locTax, fica, aTax, rent, residual, pp, hpRatio }
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
