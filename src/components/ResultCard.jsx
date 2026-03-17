import { useState } from 'react'
import { cityBreakdown, fmt } from '../lib/calculations.js'
import { useUserProfile } from '../hooks/useUserProfile.jsx'

export default function ResultCard({ city, rank, ppRank, salaryFor, topCity }) {
  const [state, dispatch] = useUserProfile()
  const [copied, setCopied] = useState(false)
  const bd = cityBreakdown(salaryFor(city), city)
  const topBd = topCity ? cityBreakdown(salaryFor(topCity), topCity) : null
  const delta = topBd ? bd.pp - topBd.pp : 0

  const handleShare = () => {
    const params = new URLSearchParams({
      occ: state.occupation?.code || '15-1252',
      salary: salaryFor(city),
      city: city.id,
    })
    const url = `${window.location.origin}${window.location.pathname}?${params}`
    const snippet = `My salary goes ${delta >= 0 ? '+' : ''}${fmt(Math.abs(delta))} ${delta >= 0 ? 'further' : 'less'} in ${city.name.split(',')[0]} vs ${topCity?.name?.split(',')[0] || 'SF'} — see for yourself: ${url}`

    navigator.clipboard.writeText(url).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
    // Also log snippet to console for debugging
    console.info('Share snippet:', snippet)
  }

  const handlePin = () => {
    dispatch({ type: 'PIN_CITY', payload: city.id })
    dispatch({ type: 'TOGGLE_COMPARE' })
  }

  return (
    <div className="border border-[rgba(15,15,15,0.12)] bg-white p-6 relative overflow-hidden">
      {/* Rank badge */}
      <div className="absolute top-4 right-4 font-mono text-xs text-[#b8922a] tracking-widest uppercase">
        #{ppRank} real value
      </div>

      {/* City name */}
      <div className="mb-4">
        <span className="text-lg mr-2" aria-hidden>🏙</span>
        <span
          className="font-bold text-xl text-[#0f0f0f]"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          {city.name}
        </span>
      </div>

      {/* Breakdown rows */}
      <div className="border-t border-[rgba(15,15,15,0.08)] pt-3 space-y-1.5 mb-4">
        {[
          { label: 'Gross Salary', value: bd.gross, color: '#0f0f0f' },
          { label: 'After-Tax', value: bd.aTax, color: '#0f0f0f' },
          { label: 'Rent (annual)', value: -bd.rent, color: '#e74c3c' },
          { label: 'Purchasing Power', value: bd.pp, color: '#27ae60', bold: true },
        ].map(row => (
          <div key={row.label} className="flex justify-between items-center">
            <span className="text-sm text-[#6b6560]">{row.label}</span>
            <span
              className={`font-mono text-sm ${row.bold ? 'font-semibold' : ''}`}
              style={{ color: row.color }}
            >
              {row.value < 0 ? `-${fmt(Math.abs(row.value))}` : fmt(row.value)}
            </span>
          </div>
        ))}
      </div>

      {/* vs comparison */}
      {topCity && topCity.id !== city.id && (
        <div className="border-t border-[rgba(15,15,15,0.08)] pt-3 mb-4">
          <p className="text-xs text-[#6b6560]">
            vs. {topCity.name.split(',')[0]}:{' '}
            <span
              className="font-mono font-semibold"
              style={{ color: delta >= 0 ? '#27ae60' : '#e74c3c' }}
            >
              {delta >= 0 ? '+' : ''}{fmt(delta)}
            </span>
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          onClick={handlePin}
          className="flex-1 border border-[#0f0f0f] text-[#0f0f0f] text-xs font-mono uppercase tracking-widest py-2 hover:bg-[#0f0f0f] hover:text-white transition-colors"
          aria-label={`Compare ${city.name}`}
        >
          Compare
        </button>
        <button
          onClick={handleShare}
          className="flex-1 bg-[#0f0f0f] text-white text-xs font-mono uppercase tracking-widest py-2 hover:bg-[#c0392b] transition-colors"
          aria-label={`Share ${city.name} result`}
        >
          {copied ? 'Copied! ✓' : 'Share ↗'}
        </button>
      </div>
    </div>
  )
}
