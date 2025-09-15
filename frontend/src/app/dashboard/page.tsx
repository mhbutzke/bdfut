'use client'

import Layout from '@/components/layout/Layout'
import { RealtimeMetrics, RealtimeAlerts, SystemStatus } from '@/components/dashboard'
import { LineChart, BarChart, PieChart } from '@/components/charts'
import { useETLStats } from '@/hooks/useETLData'
import { useDataQualitySummary } from '@/hooks/useDataQuality'
import { useSystemHealth } from '@/hooks/useSystemMetrics'
import { useState, useEffect } from 'react'

export default function DashboardPage() {
  const { data: etlStats } = useETLStats()
  const { data: qualitySummary } = useDataQualitySummary()
  const { data: systemHealth } = useSystemHealth()

  // Mock data for real-time metrics
  const [realtimeMetrics, setRealtimeMetrics] = useState([
    {
      id: 'cpu',
      name: 'CPU Usage',
      value: 45,
      unit: '%',
      status: 'healthy' as const,
      trend: 'stable' as const,
      lastUpdated: new Date()
    },
    {
      id: 'memory',
      name: 'Memory Usage',
      value: 78,
      unit: '%',
      status: 'warning' as const,
      trend: 'up' as const,
      lastUpdated: new Date()
    },
    {
      id: 'disk',
      name: 'Disk Usage',
      value: 32,
      unit: '%',
      status: 'healthy' as const,
      trend: 'down' as const,
      lastUpdated: new Date()
    },
    {
      id: 'network',
      name: 'Network Latency',
      value: 12,
      unit: 'ms',
      status: 'healthy' as const,
      trend: 'stable' as const,
      lastUpdated: new Date()
    }
  ])

  // Mock data for alerts
  const [alerts, setAlerts] = useState([
    {
      id: '1',
      title: 'High Memory Usage',
      message: 'Memory usage is above 80% threshold',
      type: 'warning' as const,
      severity: 'medium' as const,
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      source: 'System Monitor',
      acknowledged: false
    },
    {
      id: '2',
      title: 'ETL Job Failed',
      message: 'Data sync job for Premier League failed after 3 retries',
      type: 'error' as const,
      severity: 'high' as const,
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      source: 'ETL Pipeline',
      acknowledged: true
    }
  ])

  // Mock data for system components
  const systemComponents = [
    {
      id: '1',
      name: 'Database',
      status: 'healthy' as const,
      uptime: '99.9%',
      responseTime: 45,
      lastCheck: new Date(),
      description: 'Primary PostgreSQL database'
    },
    {
      id: '2',
      name: 'API Server',
      status: 'healthy' as const,
      uptime: '99.8%',
      responseTime: 120,
      lastCheck: new Date(),
      description: 'REST API endpoints'
    },
    {
      id: '3',
      name: 'ETL Pipeline',
      status: 'degraded' as const,
      uptime: '98.5%',
      responseTime: 250,
      lastCheck: new Date(),
      description: 'Data extraction and transformation'
    }
  ]

  // Mock data for charts
  const cpuData = Array.from({ length: 24 }, (_, i) => ({
    timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
    value: Math.random() * 100
  }))

  const jobStatusData = [
    { name: 'Completed', value: etlStats?.successful_jobs || 0 },
    { name: 'Failed', value: etlStats?.failed_jobs || 0 },
    { name: 'Running', value: etlStats?.running_jobs || 0 }
  ]

  const qualityData = [
    { name: 'Passing', value: qualitySummary?.passing_metrics || 0 },
    { name: 'Failing', value: qualitySummary?.failing_metrics || 0 },
    { name: 'Warning', value: qualitySummary?.warning_metrics || 0 }
  ]

  // Update real-time metrics every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setRealtimeMetrics(prev => prev.map(metric => ({
        ...metric,
        value: Math.max(0, Math.min(100, metric.value + (Math.random() - 0.5) * 10)),
        lastUpdated: new Date()
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const handleAcknowledgeAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ))
  }

  const handleDismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId))
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Advanced Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Real-time monitoring and analytics for BDFut ETL system
          </p>
        </div>

        {/* Real-time Metrics */}
        <RealtimeMetrics metrics={realtimeMetrics} />

        {/* Charts Row */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <LineChart
            data={cpuData}
            title="CPU Usage (24h)"
            dataKey="value"
            color="#3B82F6"
            formatValue={(value) => `${value.toFixed(1)}%`}
          />
          <BarChart
            data={jobStatusData}
            title="ETL Job Status"
            dataKey="value"
            color="#10B981"
            formatValue={(value) => value.toString()}
          />
        </div>

        {/* Pie Charts Row */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <PieChart
            data={jobStatusData}
            title="Job Distribution"
            formatValue={(value) => value.toString()}
          />
          <PieChart
            data={qualityData}
            title="Data Quality Metrics"
            formatValue={(value) => value.toString()}
          />
        </div>

        {/* System Status and Alerts */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <SystemStatus 
            components={systemComponents}
            overallStatus={systemHealth?.overall_status === 'healthy' ? 'healthy' : 
                          systemHealth?.overall_status === 'warning' ? 'degraded' : 'down'}
          />
          <RealtimeAlerts
            alerts={alerts}
            onAcknowledge={handleAcknowledgeAlert}
            onDismiss={handleDismissAlert}
          />
        </div>
      </div>
    </Layout>
  )
}
