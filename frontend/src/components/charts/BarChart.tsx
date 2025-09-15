'use client'

import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import Card from '@/components/ui/Card'

interface BarData {
  name: string
  value: number
  [key: string]: string | number
}

interface BarChartProps {
  data: BarData[]
  title: string
  dataKey: string
  color?: string
  height?: number
  showLegend?: boolean
  showGrid?: boolean
  formatValue?: (value: number) => string
  formatLabel?: (label: string) => string
}

export default function BarChart({
  data,
  title,
  dataKey,
  color = '#10B981',
  height = 300,
  showLegend = false,
  showGrid = true,
  formatValue = (value) => value.toString(),
  formatLabel = (label) => label
}: BarChartProps) {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsBarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />}
            <XAxis 
              dataKey="name" 
              tickFormatter={formatLabel}
              stroke="#6B7280"
              fontSize={12}
            />
            <YAxis 
              tickFormatter={formatValue}
              stroke="#6B7280"
              fontSize={12}
            />
            <Tooltip 
              labelFormatter={(value) => formatLabel(value as string)}
              formatter={(value) => [formatValue(value as number), dataKey]}
              contentStyle={{
                backgroundColor: '#F9FAFB',
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            {showLegend && <Legend />}
            <Bar 
              dataKey={dataKey} 
              fill={color}
              radius={[4, 4, 0, 0]}
            />
          </RechartsBarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
