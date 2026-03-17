import { useEffect, useRef, useState, useMemo } from 'react'
import * as d3 from 'd3'
import { useScrollama } from '../hooks/useScrollama.js'
import { useUserProfile } from '../hooks/useUserProfile.jsx'
import Tooltip from './Tooltip.jsx'
import { fmt } from '../lib/calculations.js'

const REGION_COLORS = {
  West: '#2c6fad',
  Northeast: '#c0392b',
  South: '#d4883a',
  Midwest: '#4a9c6d',
}

const MARGIN = { top: 10, right: 80, bottom: 30, left: 52 }

export default function Chapter1({ cities, occupationLabel }) {
  const svgRef = useRef(null)
  const containerRef = useRef(null)
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: null })
  const [animated, setAnimated] = useState(false)
  const { currentStep } = useScrollama('.ch1-step', 0.6)
  const [state] = useUserProfile()

  // Filter cities that have salary data for this occupation
  const occCode = state.occupation?.code
  const chartCities = useMemo(() =>
    cities
      .filter(c => c.salaries?.[occCode])
      .sort((a, b) => b.salaries[occCode] - a.salaries[occCode]),
    [cities, occCode]
  )

  useEffect(() => {
    if (currentStep >= 0 && !animated) setAnimated(true)
  }, [currentStep, animated])

  useEffect(() => {
    if (!svgRef.current || !chartCities.length) return

    const el = svgRef.current
    const width = el.clientWidth || 600
    const height = el.clientHeight || 500
    const innerW = width - MARGIN.left - MARGIN.right
    const innerH = height - MARGIN.top - MARGIN.bottom

    const svg = d3.select(el)
    svg.selectAll('*').remove()

    const g = svg.append('g').attr('transform', `translate(${MARGIN.left},${MARGIN.top})`)

    const maxVal = d3.max(chartCities, d => d.salaries[occCode]) * 1.05

    const xScale = d3.scaleLinear().domain([0, maxVal]).range([0, innerW])
    const yScale = d3.scaleBand()
      .domain(chartCities.map(d => d.short))
      .range([0, innerH])
      .padding(0.22)

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${innerH})`)
      .call(
        d3.axisBottom(xScale)
          .ticks(4)
          .tickFormat(d => `$${d3.format('~s')(d)}`)
      )
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('line').attr('stroke', 'rgba(15,15,15,0.1)')
        ax.selectAll('text').attr('fill', '#6b6560').attr('font-size', 11).attr('font-family', 'DM Sans, sans-serif')
      })

    g.append('g')
      .call(d3.axisLeft(yScale).tickSize(0))
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('text').attr('fill', '#0f0f0f').attr('font-size', 11).attr('font-family', 'DM Sans, sans-serif').attr('dx', -4)
      })

    // Grid lines
    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisBottom(xScale).ticks(4).tickSize(-innerH).tickFormat(''))
      .attr('transform', `translate(0,${innerH})`)
      .call(ax => {
        ax.select('.domain').remove()
        ax.selectAll('line').attr('stroke', 'rgba(15,15,15,0.06)')
      })

    // Bars
    const bars = g.selectAll('.bar')
      .data(chartCities, d => d.id)
      .join('rect')
      .attr('class', 'bar')
      .attr('role', 'img')
      .attr('aria-label', d => `${d.name}: ${fmt(d.salaries[occCode])} median salary for ${occupationLabel}`)
      .attr('x', 0)
      .attr('y', d => yScale(d.short))
      .attr('height', yScale.bandwidth())
      .attr('fill', d => REGION_COLORS[d.region] || '#888')
      .attr('width', 0)
      .style('cursor', 'pointer')

    // Animate on entry
    if (animated) {
      bars.transition()
        .duration(800)
        .delay((_, i) => i * 30)
        .ease(d3.easeQuadOut)
        .attr('width', d => xScale(d.salaries[occCode]))
    }

    // Value labels
    const labels = g.selectAll('.bar-label')
      .data(chartCities, d => d.id)
      .join('text')
      .attr('class', 'bar-label')
      .attr('x', d => xScale(d.salaries[occCode]) + 6)
      .attr('y', d => yScale(d.short) + yScale.bandwidth() / 2 + 4)
      .attr('font-size', 10)
      .attr('fill', '#6b6560')
      .attr('font-family', 'DM Mono, monospace')
      .text(d => `$${Math.round(d.salaries[occCode] / 1000)}k`)
      .style('opacity', animated ? 1 : 0)

    if (animated) {
      labels.transition().delay((_, i) => i * 30 + 600).style('opacity', 1)
    }

    // User salary line — only shown when a custom salary is entered
    if (state.usingCustomSalary && state.salary && state.salary < maxVal) {
      const lx = xScale(state.salary)
      g.append('line')
        .attr('x1', lx).attr('x2', lx)
        .attr('y1', 0).attr('y2', innerH)
        .attr('stroke', '#c0392b')
        .attr('stroke-width', 1.5)
        .attr('stroke-dasharray', '4 3')
        .attr('opacity', 0.8)
      g.append('text')
        .attr('x', lx + 4)
        .attr('y', 14)
        .attr('font-size', 10)
        .attr('fill', '#c0392b')
        .attr('font-family', 'DM Mono, monospace')
        .text('Your salary')
    }

    // Tooltip events
    bars
      .on('mousemove', (event, d) => {
        setTooltip({
          visible: true,
          x: event.clientX,
          y: event.clientY,
          content: {
            city: d.name,
            rows: [
              { label: 'Gross Salary', value: d.salaries[occCode] },
              { label: 'Field', value: occupationLabel, isText: true },
            ],
          },
        })
      })
      .on('mouseleave', () => setTooltip(t => ({ ...t, visible: false })))

  }, [chartCities, occCode, animated, state.usingCustomSalary, state.salary, occupationLabel])

  // Re-render on resize
  useEffect(() => {
    const obs = new ResizeObserver(() => {
      if (svgRef.current) {
        const ev = new Event('rerender')
        svgRef.current.dispatchEvent(ev)
      }
    })
    if (containerRef.current) obs.observe(containerRef.current)
    return () => obs.disconnect()
  }, [])

  return (
    <section id="chapter1" style={{ position: 'relative' }}>
      <div className="chapter-container">
        {/* Sticky chart */}
        <div className="chapter-sticky bg-[#fafaf7] flex flex-col justify-center px-6 py-4">
          <div ref={containerRef} className="w-full h-full">
            <svg ref={svgRef} className="chart-svg w-full h-full" />
          </div>

          {/* Region legend */}
          <div className="flex flex-wrap gap-4 mt-2 px-2">
            {Object.entries(REGION_COLORS).map(([region, color]) => (
              <div key={region} className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm inline-block" style={{ background: color }} />
                <span className="text-xs text-[#6b6560] font-mono">{region}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Scrolling text */}
        <div className="steps-container">
          <div className="ch1-step scroll-step">
            <div className="text-panel">
              <p className="font-mono text-xs tracking-widest uppercase text-[#c0392b] mb-3">Chapter 1</p>
              <h2>On paper, the numbers look great.</h2>
              <p>
                A {occupationLabel.toLowerCase()} in San Francisco earns nearly $168,000 a year.
                In Seattle, $152,000. In New York, $142,000. These numbers are real.
              </p>
              <p>
                But they don't tell the whole story — not even close. Scroll down to see what actually happens to that salary.
              </p>
            </div>
          </div>
        </div>
      </div>

      <Tooltip {...tooltip} />
    </section>
  )
}
