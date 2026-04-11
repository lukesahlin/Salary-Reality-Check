import { useRef, useCallback } from 'react'
import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { OCCUPATIONS } from '../data/occupations.js'
import { fmt } from '../lib/calculations.js'

export default function Nav() {
  const [state, dispatch] = useUserProfile()
  const debounceRef = useRef(null)

  const handleOccChange = useCallback((e) => {
    const occ = OCCUPATIONS.find(o => o.code === e.target.value)
    if (occ) dispatch({ type: 'SET_OCCUPATION', payload: occ })
  }, [dispatch])

  const handleSalaryInput = useCallback((e) => {
    clearTimeout(debounceRef.current)
    const raw = e.target.value.replace(/[^0-9]/g, '')
    debounceRef.current = setTimeout(() => {
      const val = parseInt(raw, 10)
      if (val >= 20000 && val <= 500000) {
        dispatch({ type: 'SET_SALARY', payload: val })
      } else if (!raw) {
        dispatch({ type: 'CLEAR_SALARY' })
      }
    }, 400)
  }, [dispatch])

  return (
    <nav
      className="sticky top-0 z-50 border-b border-[rgba(15,15,15,0.1)] bg-[#fafaf7]/95 backdrop-blur-sm"
      style={{ height: 64 }}
    >
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between gap-4">
        {/* Title */}
        <span
          className="text-[#0f0f0f] font-display font-bold text-lg whitespace-nowrap hidden sm:block"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          Salary Reality Check
        </span>

        {/* Occupation picker */}
        <div className="flex items-center gap-3 flex-1 max-w-sm">
          <label htmlFor="nav-occ" className="text-xs text-[#6b6560] font-mono uppercase tracking-widest whitespace-nowrap hidden md:block">
            Career
          </label>
          <select
            id="nav-occ"
            value={state.occupation?.code || ''}
            onChange={handleOccChange}
            className="flex-1 border border-[rgba(15,15,15,0.15)] rounded-none bg-white px-3 py-1.5 text-sm font-body text-[#0f0f0f] focus:border-[#c0392b] focus:ring-0 cursor-pointer"
            aria-label="Select occupation"
          >
            {OCCUPATIONS.map(o => (
              <option key={o.code} value={o.code}>{o.label}</option>
            ))}
          </select>
        </div>

        {/* Salary input */}
        <div className="flex flex-col items-end gap-0.5">
          <div className="flex items-center gap-2">
            <label htmlFor="nav-salary" className="text-xs text-[#6b6560] font-mono hidden md:block">
              Salary
            </label>
            <input
              id="nav-salary"
              type="text"
              inputMode="numeric"
              defaultValue=""
              placeholder="or enter yours"
              onChange={handleSalaryInput}
              className="w-36 border border-[rgba(15,15,15,0.15)] rounded-none bg-white px-3 py-1.5 text-sm font-body text-[#0f0f0f] placeholder:text-[#aaa] focus:border-[#c0392b] focus:ring-0"
              aria-label="Enter your salary (optional)"
            />
          </div>
          {state.usingCustomSalary && (
            <button
              onClick={() => dispatch({ type: 'CLEAR_SALARY' })}
              className="text-xs text-[#c0392b] font-mono flex items-center gap-1 hover:underline"
              aria-label="Clear custom salary, revert to BLS median"
            >
              Using {fmt(state.salary)} · ✕
            </button>
          )}
        </div>

        {/* Rent / Buy toggle */}
        <div className="hidden sm:flex items-center border border-[rgba(15,15,15,0.15)] overflow-hidden flex-shrink-0">
          {['rent', 'buy'].map(mode => (
            <button
              key={mode}
              onClick={() => dispatch({ type: 'SET_HOUSING_MODE', payload: mode })}
              className={`px-3 py-1.5 text-xs font-mono uppercase tracking-widest transition-colors ${
                state.housingMode === mode
                  ? 'bg-[#0f0f0f] text-white'
                  : 'text-[#6b6560] hover:text-[#0f0f0f] bg-white'
              }`}
              aria-label={`Switch to ${mode} mode`}
              aria-pressed={state.housingMode === mode}
            >
              {mode === 'rent' ? 'Rent' : 'Buy'}
            </button>
          ))}
        </div>

        {/* Compare toggle */}
        <button
          onClick={() => dispatch({ type: 'TOGGLE_COMPARE' })}
          className="text-xs font-mono uppercase tracking-widest text-[#6b6560] hover:text-[#c0392b] transition-colors whitespace-nowrap border border-[rgba(15,15,15,0.15)] px-3 py-1.5 hidden sm:block"
          aria-label="Toggle city compare sidebar"
        >
          Compare {state.pinnedCities.length > 0 ? `(${state.pinnedCities.length})` : ''}
        </button>
      </div>
    </nav>
  )
}
