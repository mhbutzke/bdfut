'use client'

import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import Card from '@/components/ui/Card'

interface PieData {
  name: string
  value: number
  color?: string
}

interface PieChartProps {
  data: PieData[]
  title: string
  height?: number
  showLegend?: boolean
  formatValue?: (value: number) => string
  formatLabel?: (label: string) => string
}

const DEFAULT_COLORS = [
  '#3B82F6', // Blue
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#EF4444', // Red
  '#8B5CF6', // Purple
  '#06B6D4', // Cyan
  '#84CC16', // Lime
  '#F97316', // Orange
]

export default function PieChart({
  data,
  title,
  height = 300,
  showLegend = true,
  formatValue = (value) => value.toString(),
  formatLabel = (label) => label
}: PieChartProps) {
  const dataWithColors = data.map((item, index) => ({
    ...item,
    color: item.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]
  }))

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsPieChart>
            <Pie
              data={dataWithColors}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {dataWithColors.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => [formatValue(value as number), 'Value']}
              contentStyle={{
                backgroundColor: '#F9FAFB',
                border: '1px solid #E5E7EB',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            {showLegend && (
              <Legend 
                verticalAlign="bottom" 
                height={36}
                formatter={(value) => formatLabel(value)}
              />
            )}
          </RechartsPieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
