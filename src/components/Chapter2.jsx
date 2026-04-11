import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useScrollama } from '../hooks/useScrollama.js'
import { useUserProfile } from '../hooks/useUserProfile.jsx'
import { cityBreakdown, fmt } from '../lib/calculations.js'
import Tooltip from './Tooltip.jsx'

const SEG_COLORS = {
  fedTax: '#e74c3c',
  stTax:  '#e67e22',
  fica:   '#f39c12',
  rent:   '#8e44ad',
  residual: '#27ae60',
}

const SEG_LABELS_RENT = {
  fedTax: 'Federal Tax',
  stTax:  'State Tax',
  fica:   'FICA',
  rent:   'Rent',
  residual: 'Take-Home',
}
const SEG_LABELS_BUY = {
  fedTax: 'Federal Tax',
  stTax:  'State Tax',
  fica:   'FICA',
  rent:   'Mortgage+Tax',
  residual: 'Take-Home',
}

// Which segments are visible at each step
const STEP_SEGMENTS = [
  [],                                    // step 0: only gross bar
  ['fedTax'],                            // step 1: + federal
  ['fedTax', 'stTax', 'fica'],           // step 2: + state + FICA
  ['fedTax', 'stTax', 'fica', 'rent'],   // step 3: + rent
  ['fedTax', 'stTax', 'fica', 'rent', 'residual'], // step 4: full stacked
]

const STEP_TEXT = [
  { headline: 'Every dollar accounted for.', body: 'Here\'s what your salary looks like across 50 cities. Now let\'s see what actually happens to it.' },
  { headline: 'First, the federal government takes its share.', body: 'Federal income tax alone claims 22–35% for most professionals. That\'s before your state gets involved.' },
  { headline: 'Then your state adds its own tax. Plus FICA.', body: 'State rates range from zero (Texas, Florida, Washington) to nearly 10% (California, New York). FICA takes another 7.65% on top.' },
  { headline: 'Then there\'s rent. In high-cost cities, this is the killer.', body: 'Median 1BR rent in San Francisco runs $3,000+/month. That\'s $36,000 a year — gone before groceries.' },
  { headline: 'This is what you actually have left.', body: 'The green bar is your real purchasing power after taxes and rent. Notice which cities have flipped.' },
]

const MARGIN = { top: 10, right: 20, bottom: 30, left: 48 }

export default function Chapter2({ cities, salaryFor }) {
  const svgRef = useRef(null)
  const containerRef = useRef(null)
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: null })
  const { currentStep } = useScrollama('.ch2-step', 0.5)
  const [state] = useUserProfile()
  const housingMode = state.housingMode

  const SEG_LABELS = housingMode === 'buy' ? SEG_LABELS_BUY : SEG_LABELS_RENT

  const step = Math.max(0, Math.min(currentStep, 4))

  // Prepare data
  const occData = cities.map(c => {
    const bd = cityBreakdown(salaryFor(c), c, housingMode)
    return { ...c, ...bd }
  }).sort((a, b) => b.gross - a.gross)

  useEffect(() => {
    if (!svgRef.current || !occData.length) return

    const el = svgRef.current
    const width  = el.clientWidth  || 600
    const height = el.clientHeight || 500
    const innerW = width  - MARGIN.left - MARGIN.right
    const innerH = height - MARGIN.top  - MARGIN.bottom

    const activeSegs = STEP_SEGMENTS[step] || []
    const showFull = step === 0

    // Sort: step 4 → sort by residual, else by gross
    const sorted = step >= 4
      ? [...occData].sort((a, b) => b.residual - a.residual)
      : occData

    const maxVal = d3.max(sorted, d => d.gross) * 1.05
    const xScale = d3.scaleLinear().domain([0, maxVal]).range([0, innerW])
    const yScale = d3.scaleBand()
      .domain(sorted.map(d => d.short))
      .range([0, innerH])
      .padding(0.18)

    const svg = d3.select(svgRef.current)
    const hasG = svg.select('g.main').size() > 0

    let g
    if (!hasG) {
      svg.selectAll('*').remove()
      g = svg.append('g').attr('class', 'main').attr('transform', `translate(${MARGIN.left},${MARGIN.top})`)

      // X axis
      g.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${innerH})`)
      // Y axis
      g.append('g').attr('class', 'y-axis')
      // Grid
      g.append('g').attr('class', 'grid').attr('transform', `translate(0,${innerH})`)
    } else {
      g = svg.select('g.main')
    }

    // Update axes
    g.select('.x-axis')
      .call(d3.axisBottom(xScale).ticks(4).tickFormat(d => `$${d3.format('~s')(d)}`))
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('line').attr('stroke', 'rgba(15,15,15,0.1)')
        ax.selectAll('text').attr('fill', '#6b6560').attr('font-size', 11).attr('font-family', 'DM Sans, sans-serif')
      })

    g.select('.y-axis')
      .call(d3.axisLeft(yScale).tickSize(0))
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('text').attr('fill', '#0f0f0f').attr('font-size', 9).attr('font-family', 'DM Sans, sans-serif').attr('dx', -4)
      })

    g.select('.grid')
      .call(d3.axisBottom(xScale).ticks(4).tickSize(-innerH).tickFormat(''))
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('line').attr('stroke', 'rgba(15,15,15,0.06)')
      })

    // For each city, draw stacked segments
    const cityGroups = g.selectAll('.city-group')
      .data(sorted, d => d.id)
      .join(
        enter => enter.append('g').attr('class', 'city-group'),
        update => update,
        exit => exit.remove()
      )

    cityGroups.transition().duration(600).ease(d3.easeCubicInOut)
      .attr('transform', d => `translate(0, ${yScale(d.short)})`)

    const bh = yScale.bandwidth()

    // Step 0: single gross bar
    cityGroups.selectAll('.bar-gross')
      .data(d => [d])
      .join('rect')
      .attr('class', 'bar-gross')
      .attr('role', 'img')
      .attr('aria-label', d => `${d.name}: gross salary ${fmt(d.gross)}`)
      .attr('y', 0).attr('height', bh)
      .attr('fill', '#b8b0a5')
      .style('opacity', showFull ? 1 : 0)
      .transition().duration(400)
      .attr('x', 0)
      .attr('width', d => xScale(d.gross))

    // Stacked deduction segments
    const segDefs = ['fedTax', 'stTax', 'fica', 'rent', 'residual']

    segDefs.forEach(seg => {
      cityGroups.selectAll(`.bar-${seg}`)
        .data(d => [d])
        .join('rect')
        .attr('class', `bar-${seg}`)
        .attr('role', 'img')
        .attr('aria-label', d => `${d.name} ${SEG_LABELS[seg]}: ${fmt(d[seg])}`)
        .attr('y', 0).attr('height', bh)
        .attr('fill', SEG_COLORS[seg])
        .attr('x', d => {
          // Compute start offset
          const order = segDefs.slice(0, segDefs.indexOf(seg))
          return xScale(order.reduce((acc, s) => acc + d[s], 0))
        })
        .style('opacity', activeSegs.includes(seg) ? 1 : 0)
        .transition().duration(600).ease(d3.easeQuadInOut)
        .attr('width', d => activeSegs.includes(seg) ? xScale(d[seg]) : 0)
        .style('opacity', activeSegs.includes(seg) ? 1 : 0)
    })

    // Tooltip
    cityGroups
      .on('mousemove', (event, d) => {
        setTooltip({
          visible: true,
          x: event.clientX,
          y: event.clientY,
          content: {
            city: d.name,
            rows: [
              { label: 'Gross', value: d.gross },
              { label: 'Federal Tax', value: d.fedTax, negative: true },
              { label: 'State Tax', value: d.stTax, negative: true },
              { label: 'FICA', value: d.fica, negative: true },
              { label: 'After-Tax', value: d.aTax },
              { label: 'Rent', value: d.rent, negative: true },
              { label: 'Take-Home', value: d.residual },
            ],
          },
        })
      })
      .on('mouseleave', () => setTooltip(t => ({ ...t, visible: false })))

  }, [occData, step, SEG_LABELS])

  const stepInfo = STEP_TEXT[step] || STEP_TEXT[0]

  return (
    <section id="chapter2" style={{ position: 'relative' }}>
      <div className="chapter-container">
        {/* Sticky chart */}
        <div className="chapter-sticky bg-white flex flex-col justify-center px-4 py-4">
          {/* Legend */}
          <div className="flex flex-wrap gap-3 mb-2 px-2">
            {Object.entries(SEG_COLORS).map(([key, color]) => (
              <div
                key={key}
                className="flex items-center gap-1.5"
                style={{ opacity: step === 0 ? 0.3 : (STEP_SEGMENTS[step]?.includes(key) ? 1 : 0.25) }}
              >
                <span className="w-3 h-3 inline-block rounded-sm" style={{ background: color }} />
                <span className="text-xs text-[#6b6560] font-mono">{SEG_LABELS[key]}</span>
              </div>
            ))}
          </div>
          <div ref={containerRef} className="flex-1 w-full">
            <svg ref={svgRef} className="chart-svg w-full h-full" />
          </div>
        </div>

        {/* Scrolling steps */}
        <div className="steps-container">
          <div className="ch2-step scroll-step">
            <div className="text-panel">
              <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-3">Chapter 2</p>
              <h2>{STEP_TEXT[0].headline}</h2>
              <p>{STEP_TEXT[0].body}</p>
            </div>
          </div>
          {STEP_TEXT.slice(1).map((st, i) => (
            <div key={i} className="ch2-step scroll-step">
              <div className="text-panel">
                <h2>{st.headline}</h2>
                <p>{st.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Tooltip {...tooltip} />
    </section>
  )
}
