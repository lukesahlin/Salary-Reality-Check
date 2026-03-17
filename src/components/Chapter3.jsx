import { useEffect, useRef, useState, useMemo } from 'react'
import * as d3 from 'd3'
import { useScrollama } from '../hooks/useScrollama.js'
import { purchasingPower, cityBreakdown, fmt } from '../lib/calculations.js'
import Tooltip from './Tooltip.jsx'

const MARGIN = { top: 10, right: 90, bottom: 30, left: 52 }

export default function Chapter3({ cities, salaryFor }) {
  const svgRef = useRef(null)
  const containerRef = useRef(null)
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: null })
  const [entered, setEntered] = useState(false)
  const { currentStep } = useScrollama('.ch3-step', 0.55)

  useEffect(() => {
    if (currentStep >= 0 && !entered) setEntered(true)
  }, [currentStep, entered])

  // Compute salary-ranked order (for rank delta)
  const salaryRanked = useMemo(() => {
    const occCode = cities[0]?.salaries ? Object.keys(cities[0].salaries)[0] : null
    return [...cities]
      .filter(c => purchasingPower(salaryFor(c), c) > 0)
      .sort((a, b) => {
        const aS = occCode ? (a.salaries?.[occCode] || 0) : 0
        const bS = occCode ? (b.salaries?.[occCode] || 0) : 0
        return bS - aS
      })
      .map((c, i) => ({ id: c.id, salaryRank: i + 1 }))
  }, [cities, salaryFor])

  // PP-ranked order
  const ppRanked = useMemo(() => {
    return [...cities]
      .filter(c => purchasingPower(salaryFor(c), c) > 0)
      .sort((a, b) => purchasingPower(salaryFor(b), b) - purchasingPower(salaryFor(a), a))
  }, [cities, salaryFor])

  useEffect(() => {
    if (!svgRef.current || !ppRanked.length) return

    const el = svgRef.current
    const width = el.clientWidth || 600
    const height = el.clientHeight || 500
    const innerW = width - MARGIN.left - MARGIN.right
    const innerH = height - MARGIN.top - MARGIN.bottom

    const maxPP = d3.max(ppRanked, d => purchasingPower(salaryFor(d), d)) * 1.05
    const xScale = d3.scaleLinear().domain([0, maxPP]).range([0, innerW])
    const yScale = d3.scaleBand()
      .domain(ppRanked.map(d => d.short))
      .range([0, innerH])
      .padding(0.22)

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const g = svg.append('g').attr('transform', `translate(${MARGIN.left},${MARGIN.top})`)

    // Grid
    g.append('g')
      .call(d3.axisBottom(xScale).ticks(4).tickSize(-innerH).tickFormat(''))
      .attr('transform', `translate(0,${innerH})`)
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('line').attr('stroke', 'rgba(15,15,15,0.06)')
      })

    // X Axis
    g.append('g').attr('transform', `translate(0,${innerH})`)
      .call(d3.axisBottom(xScale).ticks(4).tickFormat(d => `$${d3.format('~s')(d)}`))
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('text').attr('fill', '#6b6560').attr('font-size', 11).attr('font-family', 'DM Sans, sans-serif')
      })

    // Y axis
    g.append('g')
      .call(d3.axisLeft(yScale).tickSize(0))
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('text').attr('fill', '#0f0f0f').attr('font-size', 11).attr('font-family', 'DM Sans, sans-serif').attr('dx', -4)
      })

    // Rank delta per city
    const salaryRankMap = Object.fromEntries(salaryRanked.map(r => [r.id, r.salaryRank]))
    const ppRankMap = Object.fromEntries(ppRanked.map((d, i) => [d.id, i + 1]))

    // Bars with rank-change color
    const bh = yScale.bandwidth()
    const groups = g.selectAll('.pp-group')
      .data(ppRanked, d => d.id)
      .join('g')
      .attr('class', 'pp-group')
      .attr('transform', d => `translate(0,${yScale(d.short)})`)
      .style('cursor', 'pointer')

    // Gold left border for top 5
    groups.filter((_, i) => i < 5)
      .append('rect')
      .attr('x', -4).attr('y', 0).attr('width', 4).attr('height', bh)
      .attr('fill', '#b8922a')

    // Color by rank change
    groups.append('rect')
      .attr('class', 'pp-bar')
      .attr('role', 'img')
      .attr('aria-label', d => `${d.name}: purchasing power ${fmt(purchasingPower(salaryFor(d), d))}`)
      .attr('x', 0).attr('y', 0).attr('height', bh)
      .attr('fill', d => {
        const sr = salaryRankMap[d.id] || 99
        const pr = ppRankMap[d.id] || 99
        if (pr < sr) return '#27ae60'   // moved up
        if (pr > sr) return '#e74c3c'   // moved down
        return '#888'
      })
      .attr('width', 0)
      .transition().duration(1000).delay((_, i) => i * 50).ease(d3.easeCubicInOut)
      .attr('width', d => entered ? xScale(purchasingPower(salaryFor(d), d)) : 0)

    // Delta badges
    groups.append('text')
      .attr('x', d => xScale(purchasingPower(salaryFor(d), d)) + 6)
      .attr('y', bh / 2 + 4)
      .attr('font-size', 9)
      .attr('font-family', 'DM Mono, monospace')
      .attr('fill', d => {
        const sr = salaryRankMap[d.id] || 99
        const pr = ppRankMap[d.id] || 99
        if (pr < sr) return '#27ae60'
        if (pr > sr) return '#e74c3c'
        return '#999'
      })
      .text(d => {
        const sr = salaryRankMap[d.id] || ppRankMap[d.id]
        const pr = ppRankMap[d.id]
        const delta = sr - pr
        if (delta > 0) return `▲${delta}`
        if (delta < 0) return `▼${Math.abs(delta)}`
        return '–'
      })
      .style('opacity', 0)
      .transition().delay(1200).style('opacity', 1)

    // Tooltip
    groups
      .on('mousemove', (event, d) => {
        const bd = cityBreakdown(salaryFor(d), d)
        setTooltip({
          visible: true,
          x: event.clientX,
          y: event.clientY,
          content: {
            city: d.name,
            rows: [
              { label: 'Purchasing Power', value: bd.pp },
              { label: 'After-Tax Income', value: bd.aTax },
              { label: 'Rent', value: bd.rent, negative: true },
              { label: 'Residual', value: bd.residual },
            ],
            note: `Rank #${ppRankMap[d.id]} in purchasing power`,
          },
        })
      })
      .on('mouseleave', () => setTooltip(t => ({ ...t, visible: false })))

  }, [ppRanked, salaryRanked, salaryFor, entered])

  return (
    <section id="chapter3" style={{ position: 'relative' }}>
      <div className="chapter-container">
        {/* Sticky chart */}
        <div className="chapter-sticky bg-[#fafaf7] flex flex-col justify-center px-4 py-4">
          {/* Legend */}
          <div className="flex gap-4 mb-2 px-2">
            {[['#27ae60', 'Moved up'], ['#e74c3c', 'Moved down'], ['#888', 'No change'], ['#b8922a', 'Top 5']].map(([c, l]) => (
              <div key={l} className="flex items-center gap-1.5">
                <span className="w-3 h-3 inline-block rounded-sm" style={{ background: c }} />
                <span className="text-xs text-[#6b6560] font-mono">{l}</span>
              </div>
            ))}
          </div>
          <div ref={containerRef} className="flex-1 w-full">
            <svg ref={svgRef} className="chart-svg w-full h-full" />
          </div>
        </div>

        {/* Scrolling text */}
        <div className="steps-container">
          <div className="ch3-step scroll-step">
            <div className="text-panel">
              <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-3">Chapter 3</p>
              <h2>The leaderboard just flipped.</h2>
              <p>
                After taxes, rent, and the real cost of living, the cities that looked richest on paper are no longer at the top.
              </p>
              <p>
                Some mid-sized cities you may have never considered are suddenly looking very attractive.
                Green bars moved <em>up</em> in the ranking. Red moved <em>down</em>.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Tooltip {...tooltip} />
    </section>
  )
}
