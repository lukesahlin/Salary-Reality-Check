import { useEffect, useRef, useState } from 'react'
import scrollama from 'scrollama'

export function useScrollama(stepSelector = '.scroll-step', offset = 0.5) {
  const containerRef = useRef(null)
  const [currentStep, setCurrentStep] = useState(-1)

  useEffect(() => {
    const scroller = scrollama()
    scroller
      .setup({ step: stepSelector, offset, debug: false })
      .onStepEnter(({ index }) => setCurrentStep(index))
      .onStepExit(({ index, direction }) => {
        if (direction === 'up' && index === 0) setCurrentStep(-1)
      })

    const handleResize = () => scroller.resize()
    window.addEventListener('resize', handleResize)

    return () => {
      scroller.destroy()
      window.removeEventListener('resize', handleResize)
    }
  }, [stepSelector, offset])

  return { currentStep, containerRef }
}
