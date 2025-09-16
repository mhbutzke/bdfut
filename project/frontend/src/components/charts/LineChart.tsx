'use client'

import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import Card from '@/components/ui/Card'

interface DataPoint {
  timestamp: string
  value: number
  [key: string]: string | number
}

interface LineChartProps {
  data: DataPoint[]
  title: string
  dataKey: string
  color?: string
  height?: number
  showLegend?: boolean
  showGrid?: boolean
  formatValue?: (value: number) => string
  formatTimestamp?: (timestamp: string) => string
}

export default function LineChart({
  data,
  title,
  dataKey,
  color = '#3B82F6',
  height = 300,
  showLegend = false,
  showGrid = true,
  formatValue = (value) => value.toString(),
  formatTimestamp = (timestamp) => new Date(timestamp).toLocaleTimeString()
}: LineChartProps) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />}
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatTimestamp}
              stroke="#6B7280"
              fontSize={12}
            />
            <YAxis 
              tickFormatter={formatValue}
              stroke="#6B7280"
              fontSize={12}
            />
            <Tooltip 
              labelFormatter={(value) => formatTimestamp(value as string)}
              formatter={(value) => [formatValue(value as number), dataKey]}
              contentStyle={{
                backgroundColor: '#F9FAFB',
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            {showLegend && <Legend />}
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2}
              dot={{ fill: color, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: color, strokeWidth: 2 }}
            />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
