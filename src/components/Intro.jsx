import { useState, useRef, useCallback } from 'react'
import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { OCCUPATIONS } from '../data/occupations.js'

export default function Intro({ onComplete }) {
  const [state, dispatch] = useUserProfile()
  const [useMedian, setUseMedian] = useState(true)
  const salaryRef = useRef(null)

  const handleSubmit = useCallback((e) => {
    e.preventDefault()
    if (!useMedian && salaryRef.current) {
      const val = parseInt(salaryRef.current.value.replace(/[^0-9]/g, ''), 10)
      if (val >= 20000 && val <= 500000) {
        dispatch({ type: 'SET_SALARY', payload: val })
      }
    }
    onComplete()
  }, [useMedian, dispatch, onComplete])

  const handleSkip = useCallback(() => {
    dispatch({ type: 'SET_OCCUPATION', payload: OCCUPATIONS[0] })
    onComplete()
  }, [dispatch, onComplete])

  return (
    <div className="min-h-screen bg-[#fafaf7] flex items-center justify-center px-6">
      <div className="w-full max-w-lg">
        {/* Kicker */}
        <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-6 flex items-center gap-3">
          <span className="w-7 h-px bg-[#c0392b] inline-block" />
          Interactive Data Story · 2025
        </p>

        {/* Headline */}
        <h1
          className="text-[#0f0f0f] font-bold leading-tight mb-4"
          style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(32px, 5vw, 52px)', fontWeight: 900 }}
        >
          Before we start, tell us<br />
          <em className="italic text-[#c0392b]">about yourself.</em>
        </h1>
        <p className="text-[#6b6560] text-base mb-10 leading-relaxed">
          We'll show you exactly how far your salary goes across 50 U.S. cities — after taxes, rent, and the real cost of living.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Occupation */}
          <div>
            <label htmlFor="intro-occ" className="block text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-2">
              Your career field
            </label>
            <select
              id="intro-occ"
              value={state.occupation?.code || ''}
              onChange={e => {
                const occ = OCCUPATIONS.find(o => o.code === e.target.value)
                if (occ) dispatch({ type: 'SET_OCCUPATION', payload: occ })
              }}
              className="w-full border-2 border-[#0f0f0f] bg-white px-4 py-3 text-base font-body text-[#0f0f0f] focus:border-[#c0392b] focus:ring-0 cursor-pointer"
            >
              {OCCUPATIONS.map(o => (
                <option key={o.code} value={o.code}>{o.label}</option>
              ))}
            </select>
          </div>

          {/* Salary toggle */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <input
                type="checkbox"
                id="use-median"
                checked={useMedian}
                onChange={e => setUseMedian(e.target.checked)}
                className="w-4 h-4 accent-[#c0392b]"
              />
              <label htmlFor="use-median" className="text-sm text-[#6b6560] cursor-pointer">
                Use the national median for my field
              </label>
            </div>

            {!useMedian && (
              <div>
                <label htmlFor="intro-salary" className="block text-xs font-mono uppercase tracking-widest text-[#6b6560] mb-2">
                  Your salary (annual)
                </label>
                <input
                  ref={salaryRef}
                  id="intro-salary"
                  type="text"
                  inputMode="numeric"
                  placeholder="e.g. 95000"
                  className="w-full border-2 border-[#0f0f0f] bg-white px-4 py-3 text-base font-body text-[#0f0f0f] placeholder:text-[#bbb] focus:border-[#c0392b] focus:ring-0"
                />
              </div>
            )}
          </div>

          {/* CTA */}
          <button
            type="submit"
            className="w-full bg-[#0f0f0f] text-[#fafaf7] py-4 text-sm font-mono uppercase tracking-widest hover:bg-[#c0392b] transition-colors duration-200"
          >
            Show me the data →
          </button>
        </form>

        {/* Skip */}
        <button
          onClick={handleSkip}
          className="mt-4 w-full text-center text-xs text-[#aaa] hover:text-[#6b6560] font-mono transition-colors"
        >
          Skip and use Software Developer median
        </button>
      </div>
    </div>
  )
}
