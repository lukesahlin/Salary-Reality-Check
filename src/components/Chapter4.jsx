import { useMemo } from 'react'
import { rankCities } from '../lib/scoring.js'
import ResultCard from './ResultCard.jsx'

export default function Chapter4({ cities, salaryFor, occupation }) {
  const ranked = useMemo(() => rankCities(salaryFor, cities), [cities, salaryFor])

  // Top city by gross salary for the selected occupation
  const occCode = occupation?.code
  const salaryRanked = useMemo(() => {
    return [...cities]
      .filter(c => c.salaries?.[occCode])
      .sort((a, b) => b.salaries[occCode] - a.salaries[occCode])
  }, [cities, occCode])

  const top5BySalary = new Set(salaryRanked.slice(0, 5).map(c => c.id))
  const topCity = ranked[0]?.city

  // Hidden gems: ranked 3-10 by PP but NOT in top 5 by gross salary
  const gems = ranked
    .slice(2, 12)
    .filter(({ city }) => !top5BySalary.has(city.id))
    .slice(0, 3)

  const ppRankMap = Object.fromEntries(ranked.map(({ city }, i) => [city.id, i + 1]))

  if (!gems.length) return null

  return (
    <section id="chapter4" className="py-20 px-6 bg-[#fafaf7]">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-4 flex items-center gap-3">
            <span className="w-7 h-px bg-[#c0392b] inline-block" />
            Chapter 4 — Hidden Gem Spotlight
          </p>
          <h2
            className="font-bold text-[#0f0f0f] mb-4"
            style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(28px, 4vw, 42px)', fontWeight: 900 }}
          >
            Cities you might not have considered.
          </h2>
          <p className="text-[#6b6560] text-base max-w-xl leading-relaxed">
            These metros don't make headlines for big salaries — but after taxes, rent, and cost of living,
            they deliver exceptional purchasing power for <strong>{occupation?.label}</strong>s.
          </p>
        </div>

        {/* Cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {gems.map(({ city }) => (
            <ResultCard
              key={city.id}
              city={city}
              rank={salaryRanked.findIndex(c => c.id === city.id) + 1}
              ppRank={ppRankMap[city.id]}
              salaryFor={salaryFor}
              topCity={topCity}
            />
          ))}
        </div>

        {/* Full ranking summary */}
        <div className="border-t border-[rgba(15,15,15,0.1)] pt-12">
          <h3
            className="font-bold text-[#0f0f0f] mb-6"
            style={{ fontFamily: 'var(--font-display)', fontSize: 22 }}
          >
            Full purchasing power ranking
          </h3>
          <div className="space-y-2">
            {ranked.slice(0, 15).map(({ city, pp }, i) => (
              <div
                key={city.id}
                className="flex items-center gap-4 py-2 border-b border-[rgba(15,15,15,0.06)] hover:bg-white px-3 transition-colors"
              >
                <span className="w-6 text-right font-mono text-xs text-[#aaa]">{i + 1}</span>
                <div className="flex-1">
                  <span className="text-sm font-medium text-[#0f0f0f]">{city.name}</span>
                  <span className="ml-2 text-xs text-[#aaa] font-mono">{city.region}</span>
                </div>
                <span className="font-mono text-sm text-[#27ae60] font-semibold">
                  ${Math.round(pp / 1000)}k
                </span>
                {i < 5 && (
                  <span className="w-1.5 h-1.5 rounded-full bg-[#b8922a]" aria-label="Top 5" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Data note */}
        <p className="mt-10 text-xs text-[#aaa] font-mono leading-relaxed">
          Based on BLS OEWS May 2024 salary data, Zillow ZORI rent index (Jan 2026), and Tax Foundation 2024 rates.
          Purchasing power = after-tax income − median 1BR rent, adjusted for local cost of living.
          Estimates are approximate and do not account for all individual circumstances.
        </p>
      </div>
    </section>
  )
}
