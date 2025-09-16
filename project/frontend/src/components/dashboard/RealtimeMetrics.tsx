'use client'

import { useEffect, useState } from 'react'
import StatusBadge from '@/components/ui/StatusBadge'
import { Activity, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react'

interface RealtimeMetric {
  id: string
  name: string
  value: number
  unit: string
  status: 'healthy' | 'warning' | 'critical'
  trend: 'up' | 'down' | 'stable'
  lastUpdated: Date
}

interface RealtimeMetricsProps {
  metrics: RealtimeMetric[]
  refreshInterval?: number
}

export default function RealtimeMetrics({ metrics, refreshInterval = 5000 }: RealtimeMetricsProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [refreshInterval])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <Activity className="h-5 w-5 text-green-500" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <StatusBadge status="success" label="Healthy" />
      case 'warning':
        return <StatusBadge status="warning" label="Warning" />
      case 'critical':
        return <StatusBadge status="error" label="Critical" />
      default:
        return <StatusBadge status="pending" label="Unknown" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Real-time Metrics</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Live</span>
          <span>•</span>
          <span>Last updated: {currentTime.toLocaleTimeString()}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {metrics.map((metric) => (
          <div key={metric.id} className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {getStatusIcon(metric.status)}
                <span className="text-sm font-medium text-gray-900">{metric.name}</span>
              </div>
              {getStatusBadge(metric.status)}
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl font-bold text-gray-900">
                  {metric.value.toLocaleString()}
                </span>
                <span className="text-sm text-gray-500">{metric.unit}</span>
              </div>
              {getTrendIcon(metric.trend)}
            </div>

            <div className="mt-2 text-xs text-gray-500">
              Updated: {metric.lastUpdated.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
