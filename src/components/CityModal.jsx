import { useEffect } from 'react'
import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { cityBreakdown, fmt, fmtCompact, homePriceToIncomeRatio, effectiveTaxRate, stateEffectiveRate } from '../lib/calculations.js'

export default function CityModal({ city, salaryFor, ppRank, onClose }) {
  const [state] = useUserProfile()
  const housingMode = state.housingMode

  // Close on Escape — hook must come before any early return
  useEffect(() => {
    if (!city) return
    const onKey = e => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [city, onClose])

  if (!city) return null

  const gross = salaryFor(city)
  const bd    = cityBreakdown(gross, city, housingMode)
  const hpRatio = homePriceToIncomeRatio(gross, city)
  const effRate = Math.round(effectiveTaxRate(gross, city) * 100)
  const housingLabel = housingMode === 'buy' ? 'Mortgage+Tax' : 'Rent'

  // Stacked bar segments (% of gross)
  const segs = [
    { label: 'Federal Tax',    value: bd.fedTax,             color: '#e74c3c' },
    { label: 'State + Local',  value: bd.stTax + (bd.locTax||0), color: '#e67e22' },
    { label: 'FICA',           value: bd.fica,               color: '#f39c12' },
    { label: housingLabel,     value: bd.rent,               color: '#8e44ad' },
    { label: 'Purchasing Power', value: Math.max(0, bd.pp),  color: '#27ae60' },
  ]
  const barTotal = segs.reduce((s, x) => s + x.value, 0)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(15,15,15,0.55)', backdropFilter: 'blur(2px)' }}
      onClick={onClose}
    >
      <div
        className="bg-[#fafaf7] w-full max-w-2xl max-h-[92vh] overflow-y-auto"
        style={{ border: '1px solid rgba(15,15,15,0.14)', boxShadow: '0 20px 60px rgba(15,15,15,0.25)' }}
        onClick={e => e.stopPropagation()}
      >

        {/* ── Header ───────────────────────────────────────────────────────── */}
        <div className="px-6 pt-6 pb-4 border-b border-[rgba(15,15,15,0.08)] flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span
                className="font-mono text-xs text-[#b8922a] tracking-widest uppercase"
              >#{ppRank} Purchasing Power</span>
            </div>
            <h2
              className="text-[#0f0f0f] font-bold leading-tight"
              style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(22px,4vw,30px)', fontWeight: 900 }}
            >
              {city.name}
            </h2>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
              {[city.region, city.state, city.populationM ? `Pop. ${city.populationM}M` : null]
                .filter(Boolean)
                .map((item, i, arr) => (
                  <span key={i} className="font-mono text-xs text-[#6b6560]">
                    {item}{i < arr.length - 1 ? ' ·' : ''}
                  </span>
                ))}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#6b6560] hover:text-[#0f0f0f] transition-colors font-mono text-base leading-none mt-1 flex-shrink-0"
            aria-label="Close"
          >✕</button>
        </div>

        {/* ── Salary breakdown ─────────────────────────────────────────────── */}
        <div className="px-6 py-5 border-b border-[rgba(15,15,15,0.08)]">
          <p className="font-mono text-xs uppercase tracking-widest text-[#6b6560] mb-3">
            Where {fmt(gross)} goes
          </p>

          {/* Stacked bar */}
          <div className="flex h-7 w-full overflow-hidden mb-3" style={{ borderRadius: 2 }}>
            {segs.map(s => (
              <div
                key={s.label}
                style={{ width: `${(s.value / barTotal) * 100}%`, background: s.color }}
                title={`${s.label}: ${fmt(s.value)}`}
              />
            ))}
          </div>

          {/* Segment legend */}
          <div className="grid grid-cols-2 gap-x-8 gap-y-2">
            {segs.map(s => (
              <div key={s.label} className="flex items-center justify-between">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: s.color }} />
                  <span className="text-xs text-[#6b6560] truncate">{s.label}</span>
                </div>
                <span className="font-mono text-xs text-[#0f0f0f] ml-2 flex-shrink-0">{fmt(s.value)}</span>
              </div>
            ))}
            <div className="col-span-2 flex justify-between pt-2 border-t border-[rgba(15,15,15,0.08)] mt-1">
              <span className="text-xs text-[#6b6560]">Effective total tax rate</span>
              <span className="font-mono text-xs font-semibold text-[#0f0f0f]">{effRate}%</span>
            </div>
          </div>
        </div>

        {/* ── Housing ──────────────────────────────────────────────────────── */}
        <div className="px-6 py-5 border-b border-[rgba(15,15,15,0.08)]">
          <p className="font-mono text-xs uppercase tracking-widest text-[#6b6560] mb-4">Housing</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Metric label="1BR Rent / mo." value={fmt(city.medianRent1BR / 12)} />
            {city.medianHomePrice &&
              <Metric label="Median Home" value={fmtCompact(city.medianHomePrice)} />}
            {hpRatio &&
              <Metric
                label="Price-to-Income"
                value={`${hpRatio}×`}
                note="yrs of gross salary"
                accent={hpRatio > 10 ? '#e74c3c' : hpRatio < 5 ? '#27ae60' : undefined}
              />}
            <Metric
              label="Cost of Living"
              value={city.colIndex}
              note="100 = national avg"
              accent={city.colIndex > 130 ? '#e74c3c' : city.colIndex < 92 ? '#27ae60' : undefined}
            />
          </div>
        </div>

        {/* ── Livability ───────────────────────────────────────────────────── */}
        <div className="px-6 py-5 border-b border-[rgba(15,15,15,0.08)]">
          <p className="font-mono text-xs uppercase tracking-widest text-[#6b6560] mb-4">Livability</p>
          <div className="space-y-3 mb-5">
            <ScoreBar label="Walk Score"    value={city.walkScore}             color="#2c6fad" />
            <ScoreBar label="Transit Score" value={city.transitScore}          color="#8e44ad" />
            <ScoreBar
              label="Safety Score"
              value={city.crimeIndex != null ? 100 - city.crimeIndex : null}
              color="#27ae60"
              note={city.crimeIndex != null ? `Crime index ${city.crimeIndex}` : null}
            />
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {city.sunDaysPerYear != null &&
              <Metric label="Sunny Days / Year" value={city.sunDaysPerYear} />}
            {city.avgBenefitsValue != null &&
              <Metric label="Avg. Benefits Value" value={fmt(city.avgBenefitsValue)} />}
            <Metric label="State Tax Rate (eff.)" value={`${(stateEffectiveRate(gross, city.state) * 100).toFixed(1)}%`} />
          </div>
        </div>

        {/* ── Job Market & Growth ───────────────────────────────────────────── */}
        <div className="px-6 py-5">
          <p className="font-mono text-xs uppercase tracking-widest text-[#6b6560] mb-4">Job Market & Growth</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {city.unemploymentRate != null &&
              <Metric
                label="Unemployment"
                value={`${city.unemploymentRate}%`}
                accent={city.unemploymentRate > 5 ? '#e74c3c' : city.unemploymentRate < 3.5 ? '#27ae60' : undefined}
              />}
            {city.jobGrowthRate != null &&
              <Metric
                label="Job Growth YoY"
                value={`${city.jobGrowthRate >= 0 ? '+' : ''}${city.jobGrowthRate}%`}
                accent={city.jobGrowthRate >= 2.5 ? '#27ae60' : city.jobGrowthRate < 1 ? '#e74c3c' : undefined}
              />}
            {city.populationM != null &&
              <Metric label="Metro Pop." value={`${city.populationM}M`} />}
            {city.popGrowthRate != null &&
              <Metric
                label="Pop. Growth (5yr)"
                value={`${city.popGrowthRate >= 0 ? '+' : ''}${city.popGrowthRate}%`}
                accent={city.popGrowthRate >= 10 ? '#27ae60' : city.popGrowthRate < 0 ? '#e74c3c' : undefined}
              />}
          </div>
        </div>

      </div>
    </div>
  )
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function Metric({ label, value, note, accent }) {
  return (
    <div>
      <p className="text-xs text-[#6b6560] mb-0.5 leading-tight">{label}</p>
      <p
        className="font-mono text-sm font-semibold leading-tight"
        style={{ color: accent || '#0f0f0f' }}
      >{value}</p>
      {note && <p className="text-xs text-[#aaa] mt-0.5">{note}</p>}
    </div>
  )
}

function ScoreBar({ label, value, color, note }) {
  if (value == null) return null
  const pct = Math.max(0, Math.min(100, value))
  return (
    <div>
      <div className="flex justify-between items-baseline mb-1">
        <span className="text-xs text-[#6b6560]">{label}</span>
        <div className="flex items-baseline gap-2">
          <span className="font-mono text-xs font-semibold" style={{ color }}>
            {Math.round(value)}
            <span className="text-[#aaa] font-normal"> / 100</span>
          </span>
          {note && <span className="text-xs text-[#aaa]">{note}</span>}
        </div>
      </div>
      <div className="h-1.5 bg-[rgba(15,15,15,0.08)] overflow-hidden" style={{ borderRadius: 2 }}>
        <div
          className="h-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color, borderRadius: 2 }}
        />
      </div>
    </div>
  )
}
