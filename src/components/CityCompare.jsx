import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { cityBreakdown, fmt } from '../lib/calculations.js'
import { purchasingPower } from '../lib/calculations.js'

export default function CityCompare({ cities, salaryFor }) {
  const [state, dispatch] = useUserProfile()
  const { pinnedCities, compareOpen } = state

  const pinned = pinnedCities.map(id => cities.find(c => c.id === id)).filter(Boolean)
  const available = cities.filter(c => !pinnedCities.includes(c.id))

  const bestCity = pinned.reduce((best, city) => {
    const pp = purchasingPower(salaryFor(city), city)
    return !best || pp > purchasingPower(effectiveSalary, best) ? city : best
  }, null)

  if (!compareOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-40"
        onClick={() => dispatch({ type: 'TOGGLE_COMPARE' })}
        aria-hidden
      />

      {/* Sidebar */}
      <aside
        className="fixed right-0 top-0 h-full w-80 bg-white border-l border-[rgba(15,15,15,0.1)] z-50 flex flex-col shadow-2xl"
        role="complementary"
        aria-label="City comparison sidebar"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[rgba(15,15,15,0.08)]">
          <h2 className="font-bold text-[#0f0f0f] text-sm font-mono uppercase tracking-widest">
            Compare Cities
            <span className="ml-2 text-[#aaa] font-normal">(up to 3)</span>
          </h2>
          <button
            onClick={() => dispatch({ type: 'TOGGLE_COMPARE' })}
            className="text-[#aaa] hover:text-[#0f0f0f] text-lg transition-colors"
            aria-label="Close compare sidebar"
          >
            ×
          </button>
        </div>

        {/* Pinned cities */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-6">
          {pinned.length === 0 && (
            <p className="text-sm text-[#aaa] font-mono text-center mt-8">
              No cities pinned yet.<br />Click Compare on any city card.
            </p>
          )}

          {pinned.map(city => {
            const bd = cityBreakdown(salaryFor(city), city)
            const isBest = bestCity?.id === city.id
            return (
              <div key={city.id} className={`border rounded-sm p-4 ${isBest ? 'border-[#b8922a]' : 'border-[rgba(15,15,15,0.1)]'}`}>
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="font-bold text-sm text-[#0f0f0f]" style={{ fontFamily: 'var(--font-display)' }}>
                      {city.name}
                    </span>
                    {isBest && (
                      <span className="ml-2 text-xs font-mono text-[#b8922a]">★ Best value</span>
                    )}
                  </div>
                  <button
                    onClick={() => dispatch({ type: 'UNPIN_CITY', payload: city.id })}
                    className="text-[#aaa] hover:text-[#c0392b] text-sm ml-2 transition-colors"
                    aria-label={`Remove ${city.name} from comparison`}
                  >
                    ×
                  </button>
                </div>

                {/* Waterfall breakdown */}
                <div className="space-y-1">
                  {[
                    { label: 'Gross', value: bd.gross },
                    { label: 'Federal Tax', value: -bd.fedTax, negative: true },
                    { label: 'State Tax', value: -bd.stTax, negative: true },
                    { label: 'FICA', value: -bd.fica, negative: true },
                    { label: 'After-Tax', value: bd.aTax, divider: true },
                    { label: 'Rent', value: -bd.rent, negative: true },
                    { label: 'Purchasing Power', value: bd.pp, highlight: true },
                  ].map(row => (
                    <div key={row.label}>
                      {row.divider && <div className="border-t border-[rgba(15,15,15,0.08)] my-1" />}
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-[#6b6560]">{row.label}</span>
                        <span
                          className={`font-mono text-xs ${row.highlight ? 'font-semibold text-[#27ae60]' : row.negative ? 'text-[#e74c3c]' : 'text-[#0f0f0f]'}`}
                        >
                          {row.value < 0 ? `-${fmt(Math.abs(row.value))}` : fmt(row.value)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}

          {/* Add a city */}
          {pinned.length < 3 && (
            <div>
              <label htmlFor="compare-add" className="block text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-2">
                Add a city
              </label>
              <select
                id="compare-add"
                value=""
                onChange={e => {
                  if (e.target.value) dispatch({ type: 'PIN_CITY', payload: e.target.value })
                }}
                className="w-full border border-[rgba(15,15,15,0.15)] bg-white px-3 py-2 text-sm text-[#0f0f0f] font-body"
                aria-label="Add a city to compare"
              >
                <option value="">Select a city…</option>
                {available.sort((a, b) => a.name.localeCompare(b.name)).map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Best value summary */}
        {bestCity && pinned.length > 1 && (
          <div className="px-5 py-4 border-t border-[rgba(15,15,15,0.08)] bg-[#fafaf7]">
            <p className="text-xs text-[#6b6560] font-mono">
              Best value among these:
              <span className="block font-semibold text-[#0f0f0f] text-sm mt-0.5">{bestCity.name}</span>
            </p>
          </div>
        )}
      </aside>
    </>
  )
}
