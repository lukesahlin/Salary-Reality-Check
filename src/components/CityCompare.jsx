import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { cityBreakdown, purchasingPower, fmt, fmtCompact, annualHousingCost } from '../lib/calculations.js'

const ROWS = (housingLabel) => [
  { key: 'gross',    label: 'Gross Salary',     color: null,      divAfter: false },
  { key: 'fedTax',   label: 'Federal Tax',       color: '#e74c3c', negative: true  },
  { key: 'stTax',    label: 'State Tax',         color: '#e67e22', negative: true  },
  { key: 'locTax',   label: 'Local Tax',         color: '#e67e22', negative: true  },
  { key: 'fica',     label: 'FICA',              color: '#f39c12', negative: true, divAfter: true },
  { key: 'aTax',     label: 'After-Tax Income',  color: null,      bold: true      },
  { key: 'rent',     label: housingLabel,        color: '#8e44ad', negative: true, divAfter: true },
  { key: 'pp',       label: 'Purchasing Power',  color: '#27ae60', bold: true, highlight: true },
]

export default function CityCompare({ cities, salaryFor }) {
  const [state, dispatch] = useUserProfile()
  const { pinnedCities, compareOpen, housingMode } = state

  const pinned = pinnedCities.map(id => cities.find(c => c.id === id)).filter(Boolean)
  const available = cities.filter(c => !pinnedCities.includes(c.id))

  const breakdowns = pinned.map(city => ({
    city,
    bd: cityBreakdown(salaryFor(city), city, housingMode),
  }))

  const bestCity = breakdowns.length > 1
    ? breakdowns.reduce((best, cur) => cur.bd.pp > best.bd.pp ? cur : best).city
    : null

  const housingLabel = housingMode === 'buy' ? 'Mortgage + Tax' : 'Rent (1BR)'
  const rows = ROWS(housingLabel)

  if (!compareOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-40"
        onClick={() => dispatch({ type: 'TOGGLE_COMPARE' })}
        aria-hidden
      />

      {/* Drawer — wider to fit table */}
      <aside
        className="fixed right-0 top-0 h-full bg-white border-l border-[rgba(15,15,15,0.1)] z-50 flex flex-col shadow-2xl overflow-hidden"
        style={{ width: 'min(660px, 100vw)' }}
        role="complementary"
        aria-label="City comparison panel"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(15,15,15,0.08)] flex-shrink-0">
          <h2 className="font-bold text-[#0f0f0f] text-sm font-mono uppercase tracking-widest">
            Compare Cities
            <span className="ml-2 text-[#aaa] font-normal normal-case">(up to 3)</span>
          </h2>
          <button
            onClick={() => dispatch({ type: 'TOGGLE_COMPARE' })}
            className="text-[#aaa] hover:text-[#0f0f0f] text-xl transition-colors w-8 h-8 flex items-center justify-center"
            aria-label="Close comparison panel"
          >
            ×
          </button>
        </div>

        {/* City selector row */}
        <div className="px-6 py-3 border-b border-[rgba(15,15,15,0.06)] bg-[#fafaf7] flex-shrink-0 flex items-center gap-3 flex-wrap">
          {pinned.map(city => (
            <div key={city.id} className="flex items-center gap-1.5 bg-white border border-[rgba(15,15,15,0.15)] px-2.5 py-1">
              <span className="text-xs font-semibold text-[#0f0f0f]">{city.short}</span>
              <button
                onClick={() => dispatch({ type: 'UNPIN_CITY', payload: city.id })}
                className="text-[#aaa] hover:text-[#c0392b] text-xs transition-colors"
                aria-label={`Remove ${city.name}`}
              >×</button>
            </div>
          ))}
          {pinned.length < 3 && (
            <select
              value=""
              onChange={e => { if (e.target.value) dispatch({ type: 'PIN_CITY', payload: e.target.value }) }}
              className="border border-dashed border-[rgba(15,15,15,0.2)] bg-white px-2.5 py-1 text-xs text-[#6b6560] font-mono cursor-pointer focus:outline-none focus:border-[#0f0f0f]"
              aria-label="Add a city"
            >
              <option value="">+ Add city…</option>
              {available.sort((a, b) => a.name.localeCompare(b.name)).map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          )}
        </div>

        {/* Table */}
        <div className="flex-1 overflow-y-auto">
          {pinned.length === 0 ? (
            <p className="text-sm text-[#aaa] font-mono text-center mt-16 px-6">
              No cities added yet.<br />
              <span className="text-xs">Click Compare on any city card, or add one above.</span>
            </p>
          ) : (
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-[rgba(15,15,15,0.08)] bg-[#fafaf7]">
                  <th className="text-left px-6 py-2.5 text-xs font-mono uppercase tracking-widest text-[#aaa] w-36">
                    Category
                  </th>
                  {breakdowns.map(({ city }) => (
                    <th key={city.id} className="text-right px-4 py-2.5 font-display font-bold text-[#0f0f0f] text-sm">
                      <div className="flex flex-col items-end gap-0.5">
                        <span>{city.short}</span>
                        {bestCity?.id === city.id && (
                          <span className="text-[10px] font-mono font-normal text-[#b8922a]">★ best value</span>
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
                {/* City name row */}
                <tr className="border-b border-[rgba(15,15,15,0.04)] bg-[#fafaf7]">
                  <td className="px-6 py-1" />
                  {breakdowns.map(({ city }) => (
                    <td key={city.id} className="text-right px-4 py-1 text-[10px] text-[#aaa] font-mono">
                      {city.name}
                    </td>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map(row => {
                  const vals = breakdowns.map(({ bd }) => bd[row.key] ?? 0)
                  const maxVal = Math.max(...vals.map(Math.abs))

                  return (
                    <tr
                      key={row.key}
                      className={`border-b ${row.highlight ? 'bg-[#f0fdf4]' : row.divAfter ? 'border-b-[rgba(15,15,15,0.12)]' : 'border-[rgba(15,15,15,0.04)]'}`}
                    >
                      <td className="px-6 py-2.5 text-xs text-[#6b6560] font-mono whitespace-nowrap">
                        {row.color && (
                          <span
                            className="inline-block w-2 h-2 rounded-sm mr-1.5 align-middle"
                            style={{ background: row.color }}
                          />
                        )}
                        {row.label}
                      </td>
                      {breakdowns.map(({ city, bd }) => {
                        const raw = bd[row.key] ?? 0
                        const pct = maxVal > 0 ? Math.abs(raw) / maxVal : 0

                        return (
                          <td
                            key={city.id}
                            className="text-right px-4 py-2.5 align-middle"
                          >
                            <div className="flex flex-col items-end gap-1">
                              <span
                                className={`font-mono text-xs tabular-nums ${
                                  row.highlight
                                    ? 'font-bold text-[#27ae60] text-sm'
                                    : row.bold
                                    ? 'font-semibold text-[#0f0f0f]'
                                    : row.negative
                                    ? 'text-[#e74c3c]'
                                    : 'text-[#0f0f0f]'
                                }`}
                              >
                                {row.negative ? `−${fmt(Math.abs(raw))}` : fmt(raw)}
                              </span>
                              {/* Proportion bar */}
                              {!row.bold && maxVal > 0 && (
                                <div className="w-full h-0.5 bg-[rgba(15,15,15,0.06)] rounded-full overflow-hidden">
                                  <div
                                    className="h-full rounded-full transition-all duration-300"
                                    style={{
                                      width: `${pct * 100}%`,
                                      background: row.color || (raw >= 0 ? '#0f0f0f' : '#e74c3c'),
                                    }}
                                  />
                                </div>
                              )}
                            </div>
                          </td>
                        )
                      })}
                    </tr>
                  )
                })}

                {/* % of gross row */}
                <tr className="bg-[#fafaf7] border-t border-[rgba(15,15,15,0.08)]">
                  <td className="px-6 py-2.5 text-xs text-[#aaa] font-mono">PP as % of gross</td>
                  {breakdowns.map(({ city, bd }) => (
                    <td key={city.id} className="text-right px-4 py-2.5">
                      <span className="font-mono text-xs text-[#6b6560]">
                        {bd.gross > 0 ? `${Math.round((bd.pp / bd.gross) * 100)}%` : '—'}
                      </span>
                    </td>
                  ))}
                </tr>

                {/* Delta vs best row */}
                {bestCity && breakdowns.length > 1 && (
                  <tr className="bg-[#fafaf7]">
                    <td className="px-6 py-2.5 text-xs text-[#aaa] font-mono">vs. best</td>
                    {breakdowns.map(({ city, bd }) => {
                      const bestPP = breakdowns.find(b => b.city.id === bestCity.id)?.bd.pp ?? 0
                      const diff = bd.pp - bestPP
                      return (
                        <td key={city.id} className="text-right px-4 py-2.5">
                          <span className={`font-mono text-xs ${diff === 0 ? 'text-[#b8922a]' : 'text-[#e74c3c]'}`}>
                            {diff === 0 ? '—' : `−${fmtCompact(Math.abs(diff))}`}
                          </span>
                        </td>
                      )
                    })}
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer note */}
        <div className="px-6 py-3 border-t border-[rgba(15,15,15,0.08)] bg-[#fafaf7] flex-shrink-0">
          <p className="text-[10px] text-[#aaa] font-mono">
            {housingMode === 'buy'
              ? `Buy mode: 20% down, 7.0% 30yr fixed + 1.1% property tax`
              : 'Rent mode: median 1BR (Zillow ZORI 2026)'}
            {' · '}BLS OEWS 2024 · Tax Foundation 2024
          </p>
        </div>
      </aside>
    </>
  )
}
