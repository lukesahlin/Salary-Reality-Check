import { useEffect, useRef } from 'react'
import ReactDOM from 'react-dom'
import { fmt } from '../lib/calculations.js'

export default function Tooltip({ visible, x, y, content }) {
  const ref = useRef(null)

  useEffect(() => {
    if (!ref.current || !visible) return
    const el = ref.current
    const vw = window.innerWidth
    const rect = el.getBoundingClientRect()
    // Auto-flip if within 200px of right edge
    if (x + rect.width + 20 > vw - 200) {
      el.style.left = `${x - rect.width - 12}px`
    } else {
      el.style.left = `${x + 12}px`
    }
    el.style.top = `${y - rect.height / 2}px`
  }, [visible, x, y])

  if (!visible || !content) return null

  return ReactDOM.createPortal(
    <div
      ref={ref}
      role="tooltip"
      style={{
        position: 'fixed',
        left: x + 12,
        top: y,
        zIndex: 9999,
        pointerEvents: 'none',
      }}
      className="bg-[#0f0f0f] text-[#fafaf7] rounded-sm shadow-xl px-4 py-3 text-sm min-w-[200px]"
    >
      {content.city && (
        <div className="font-semibold mb-2 font-mono text-xs tracking-widest uppercase text-[#b8922a]">
          {content.city}
        </div>
      )}
      {content.rows?.map((row, i) => (
        <div key={i} className="flex justify-between gap-6 py-0.5">
          <span className="text-[#aaa] text-xs">{row.label}</span>
          <span className={`font-mono text-xs font-medium ${row.negative ? 'text-[#e74c3c]' : 'text-[#fafaf7]'}`}>
            {row.negative ? '-' : ''}{fmt(Math.abs(row.value))}
          </span>
        </div>
      ))}
      {content.note && (
        <div className="mt-2 pt-2 border-t border-white/10 text-xs text-[#888]">{content.note}</div>
      )}
      {/* Screen-reader duplicate */}
      <span className="sr-only">
        {content.city}: {content.rows?.map(r => `${r.label} ${fmt(r.value)}`).join(', ')}
      </span>
    </div>,
    document.body
  )
}
