import { useEffect, useRef } from 'react'
import { BarChart, GraphChart, LineChart, RadarChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from 'echarts/components'
import { init, use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

use([
  BarChart,
  GraphChart,
  LineChart,
  RadarChart,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer,
])

function EChart({ option, height = 280, onChartClick, className = '' }) {
  const containerRef = useRef(null)

  useEffect(() => {
    const chart = init(containerRef.current)
    chart.setOption(option)

    if (onChartClick) {
      chart.on('click', onChartClick)
    }

    const resizeObserver = new ResizeObserver(() => chart.resize())
    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
      chart.dispose()
    }
  }, [onChartClick, option])

  return <div ref={containerRef} className={className} style={{ height }} />
}

export default EChart
