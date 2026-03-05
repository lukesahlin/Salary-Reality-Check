import { useState, useEffect } from 'react'
import { useUserProfile, getEffectiveSalary } from './hooks/useUserProfile.jsx'
import { OCCUPATIONS } from './data/occupations.js'
import Nav from './components/Nav.jsx'
import Intro from './components/Intro.jsx'
import Chapter1 from './components/Chapter1.jsx'
import Chapter2 from './components/Chapter2.jsx'
import Chapter3 from './components/Chapter3.jsx'
import Chapter4 from './components/Chapter4.jsx'
import CityCompare from './components/CityCompare.jsx'

export default function App() {
  const [state, dispatch] = useUserProfile()
  const [cities, setCities] = useState([])
  const [loading, setLoading] = useState(true)
  const [introComplete, setIntroComplete] = useState(false)

  // Load cities.json
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/cities.json`)
      .then(r => r.json())
      .then(data => {
        setCities(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  // Parse URL params on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const occ = params.get('occ')
    const salary = params.get('salary')
    if (occ) {
      const found = OCCUPATIONS.find(o => o.code === occ)
      if (found) dispatch({ type: 'SET_OCCUPATION', payload: found })
    }
    if (salary) {
      const val = parseInt(salary, 10)
      if (val >= 20000 && val <= 500000) dispatch({ type: 'SET_SALARY', payload: val })
    }
    if (occ || salary) setIntroComplete(true)
  }, [dispatch])

  const effectiveSalary = getEffectiveSalary(state, cities)

  if (loading) {
    return (
      <div className="min-h-screen bg-[#fafaf7] flex items-center justify-center">
        <div className="text-center">
          <p className="font-mono text-xs tracking-widest uppercase text-[#aaa] mb-4">Loading salary data…</p>
          <div className="w-32 h-px bg-[rgba(15,15,15,0.1)] mx-auto overflow-hidden">
            <div className="h-full bg-[#c0392b] animate-pulse" style={{ width: '60%' }} />
          </div>
        </div>
      </div>
    )
  }

  if (!cities.length) {
    return (
      <div className="min-h-screen bg-[#fafaf7] flex items-center justify-center px-6">
        <div className="max-w-md text-center">
          <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-4">Data Unavailable</p>
          <p className="text-[#6b6560]">
            Could not load city data. Run <code className="font-mono bg-[#f0ede6] px-1">python scripts/download_data.py</code> to generate cities.json, then reload.
          </p>
        </div>
      </div>
    )
  }

  if (!introComplete) {
    return <Intro onComplete={() => setIntroComplete(true)} />
  }

  return (
    <>
      <Nav effectiveSalary={effectiveSalary} />

      <main>
        <Chapter1
          cities={cities}
          effectiveSalary={effectiveSalary}
          occupationLabel={state.occupation?.label || 'Professional'}
        />
        <Chapter2
          cities={cities}
          effectiveSalary={effectiveSalary}
        />
        <Chapter3
          cities={cities}
          effectiveSalary={effectiveSalary}
        />
        <Chapter4
          cities={cities}
          effectiveSalary={effectiveSalary}
          occupation={state.occupation}
        />
      </main>

      <CityCompare cities={cities} effectiveSalary={effectiveSalary} />

      {/* Footer */}
      <footer className="border-t border-[rgba(15,15,15,0.1)] py-8 px-6 mt-0">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="font-mono text-xs text-[#aaa] uppercase tracking-widest">
            Salary Reality Check · Where Does Your Salary Go?
          </p>
          <p className="font-mono text-xs text-[#aaa]">
            Data: BLS OEWS 2024 · Zillow ZORI · Tax Foundation 2024
          </p>
        </div>
      </footer>
    </>
  )
}
