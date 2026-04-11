import { useState, useMemo, useCallback } from 'react'
import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { purchasingPower, breakEvenSalary, fmt, fmtCompact } from '../lib/calculations.js'

export default function BreakEven({ cities }) {
  const [state] = useUserProfile()
  const housingMode = state.housingMode

  const sorted = useMemo(() => [...cities].sort((a, b) => a.name.localeCompare(b.name)), [cities])

  const [srcId,     setSrcId]    = useState('')
  const [destId,    setDestId]   = useState('')
  const [srcSalary, setSrcSalary] = useState('')
  const [rawInput,  setRawInput]  = useState('')

  const srcCity  = useMemo(() => sorted.find(c => c.id === srcId),  [sorted, srcId])
  const destCity = useMemo(() => sorted.find(c => c.id === destId), [sorted, destId])

  const handleSalaryChange = useCallback((e) => {
    const raw = e.target.value.replace(/[^0-9]/g, '')
    setRawInput(raw)
    const val = parseInt(raw, 10)
    if (val >= 20_000 && val <= 2_000_000) setSrcSalary(val)
    else if (!raw) setSrcSalary('')
  }, [])

  const result = useMemo(() => {
    if (!srcCity || !destCity || !srcSalary) return null

    const sourcePP  = purchasingPower(srcSalary, srcCity, housingMode)
    const required  = breakEvenSalary(sourcePP, destCity, housingMode)

    if (required === null) return { unreachable: true }

    const diff    = required - srcSalary
    const pctDiff = srcSalary > 0 ? (diff / srcSalary) * 100 : 0

    // Also compute what $srcSalary buys in destCity vs srcCity
    const destPP = purchasingPower(srcSalary, destCity, housingMode)
    const ppDiff = destPP - sourcePP

    return { sourcePP, destPP, required, diff, pctDiff, ppDiff }
  }, [srcCity, destCity, srcSalary, housingMode])

  return (
    <section id="breakeven" className="py-20 px-6 bg-white border-t border-[rgba(15,15,15,0.08)]">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="mb-10">
          <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-4 flex items-center gap-3">
            <span className="w-7 h-px bg-[#c0392b] inline-block" />
            Break-Even Calculator
          </p>
          <h2
            className="font-bold text-[#0f0f0f] mb-3"
            style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(26px, 3.5vw, 38px)', fontWeight: 900 }}
          >
            What would you need to earn?
          </h2>
          <p className="text-[#6b6560] text-base max-w-xl leading-relaxed">
            Enter your current salary and city. We'll calculate the exact salary you'd need
            in another city to maintain the same purchasing power after taxes and housing.
          </p>
        </div>

        {/* Input panel */}
        <div className="bg-[#fafaf7] border border-[rgba(15,15,15,0.1)] p-6 mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-end">

            {/* Source city */}
            <div>
              <label className="block text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-2">
                I currently live in
              </label>
              <select
                value={srcId}
                onChange={e => setSrcId(e.target.value)}
                className="w-full border border-[rgba(15,15,15,0.15)] bg-white px-3 py-2 text-sm text-[#0f0f0f] focus:outline-none focus:border-[#0f0f0f]"
                aria-label="Select current city"
              >
                <option value="">Select city…</option>
                {sorted.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>

            {/* Salary */}
            <div>
              <label className="block text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-2">
                And I earn
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[#aaa] font-mono">$</span>
                <input
                  type="text"
                  inputMode="numeric"
                  value={rawInput}
                  onChange={handleSalaryChange}
                  placeholder="120,000"
                  className="w-full border border-[rgba(15,15,15,0.15)] bg-white pl-7 pr-3 py-2 text-sm font-mono text-[#0f0f0f] placeholder:text-[#bbb] focus:outline-none focus:border-[#0f0f0f]"
                  aria-label="Enter your salary"
                />
              </div>
            </div>

            {/* Destination city */}
            <div>
              <label className="block text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-2">
                I'm considering moving to
              </label>
              <select
                value={destId}
                onChange={e => setDestId(e.target.value)}
                className="w-full border border-[rgba(15,15,15,0.15)] bg-white px-3 py-2 text-sm text-[#0f0f0f] focus:outline-none focus:border-[#0f0f0f]"
                aria-label="Select destination city"
              >
                <option value="">Select city…</option>
                {sorted.filter(c => c.id !== srcId).map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Result */}
        {result && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">

            {/* Main answer */}
            <div className="border border-[rgba(15,15,15,0.1)] p-6 bg-[#fafaf7]">
              <p className="text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-3">
                To match your lifestyle in {destCity.name}
              </p>
              {result.unreachable ? (
                <p className="text-sm text-[#c0392b] font-mono">
                  Purchasing power is unachievable in {destCity.name} below $2M — costs exceed income.
                </p>
              ) : (
                <>
                  <div
                    className="font-bold text-[#0f0f0f] mb-2"
                    style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(28px, 4vw, 44px)' }}
                  >
                    {fmt(result.required)}
                  </div>
                  <div className={`text-sm font-mono font-semibold mb-4 ${result.diff > 0 ? 'text-[#c0392b]' : 'text-[#27ae60]'}`}>
                    {result.diff > 0
                      ? `+${fmtCompact(result.diff)} more (+${Math.round(result.pctDiff)}%)`
                      : `${fmtCompact(result.diff)} less (${Math.round(result.pctDiff)}%)`}
                    {' '}than your current salary
                  </div>
                  <p className="text-xs text-[#6b6560] leading-relaxed">
                    {fmt(srcSalary)} in {srcCity.name} gives you <strong>{fmtCompact(result.sourcePP)}</strong> in purchasing power.
                    You need <strong>{fmt(result.required)}</strong> in {destCity.name} to match that.
                  </p>
                </>
              )}
            </div>

            {/* Same salary comparison */}
            {!result.unreachable && (
              <div className="border border-[rgba(15,15,15,0.1)] p-6">
                <p className="text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-3">
                  If you moved at your current salary
                </p>
                <div
                  className={`font-bold mb-2 ${result.ppDiff >= 0 ? 'text-[#27ae60]' : 'text-[#c0392b]'}`}
                  style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(24px, 3vw, 36px)' }}
                >
                  {result.ppDiff >= 0 ? '+' : ''}{fmtCompact(result.ppDiff)}
                </div>
                <div className="text-xs font-mono text-[#6b6560] mb-4">
                  {result.ppDiff >= 0 ? 'more' : 'less'} purchasing power per year
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-[#6b6560] font-mono">{srcCity.short} purchasing power</span>
                    <span className="font-mono font-semibold text-[#0f0f0f]">{fmtCompact(result.sourcePP)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-[#6b6560] font-mono">{destCity.short} purchasing power</span>
                    <span className={`font-mono font-semibold ${result.destPP >= result.sourcePP ? 'text-[#27ae60]' : 'text-[#c0392b]'}`}>
                      {fmtCompact(result.destPP)}
                    </span>
                  </div>
                  {/* Bar comparison */}
                  <div className="pt-2 space-y-1.5">
                    {[
                      { label: srcCity.short, val: result.sourcePP },
                      { label: destCity.short, val: result.destPP },
                    ].map(({ label, val }) => {
                      const maxPP = Math.max(result.sourcePP, result.destPP, 1)
                      return (
                        <div key={label} className="flex items-center gap-2">
                          <span className="text-[10px] font-mono text-[#aaa] w-6 text-right">{label}</span>
                          <div className="flex-1 h-2 bg-[rgba(15,15,15,0.06)] rounded-sm overflow-hidden">
                            <div
                              className="h-full rounded-sm transition-all duration-500"
                              style={{
                                width: `${Math.max(0, (val / maxPP)) * 100}%`,
                                background: val >= result.sourcePP && label !== srcCity.short
                                  ? '#27ae60'
                                  : val < result.sourcePP && label !== srcCity.short
                                  ? '#c0392b'
                                  : '#0f0f0f',
                              }}
                            />
                          </div>
                          <span className="text-[10px] font-mono text-[#6b6560] w-14 text-right">
                            {fmtCompact(val)}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
                <p className="text-[10px] text-[#aaa] font-mono mt-4">
                  {housingMode === 'buy'
                    ? 'Buy mode: 20% down, 7.0% 30yr fixed + property tax'
                    : 'Rent mode: median 1BR'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Prompt state */}
        {!result && (
          <div className="border border-dashed border-[rgba(15,15,15,0.15)] p-10 text-center">
            <p className="text-sm text-[#aaa] font-mono">
              Fill in all three fields above to see your break-even salary.
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
