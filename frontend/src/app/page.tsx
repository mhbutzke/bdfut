'use client'

import Layout from '@/components/layout/Layout'
import MetricCard from '@/components/ui/MetricCard'
import DataTable from '@/components/ui/DataTable'
import StatusBadge from '@/components/ui/StatusBadge'
import { useETLStats, useETLJobs } from '@/hooks/useETLData'
import { useDataQualitySummary } from '@/hooks/useDataQuality'
import { useSystemHealth } from '@/hooks/useSystemMetrics'
import { useAlertSummary } from '@/hooks/useAlerts'
import { Database, Activity, AlertTriangle, Server } from 'lucide-react'

export default function HomePage() {
  const { data: etlStats, isLoading: etlStatsLoading } = useETLStats()
  const { data: etlJobs } = useETLJobs()
  const { data: qualitySummary, isLoading: qualityLoading } = useDataQualitySummary()
  const { data: systemHealth, isLoading: systemLoading } = useSystemHealth()
  const { data: alertSummary, isLoading: alertLoading } = useAlertSummary()

  const jobColumns = [
    { key: 'name' as const, label: 'Job Name' },
    { key: 'status' as const, label: 'Status' },
    { key: 'started_at' as const, label: 'Started' },
    { key: 'duration' as const, label: 'Duration' },
    { key: 'records_processed' as const, label: 'Records' }
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitoramento do sistema ETL BDFut
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="ETL Jobs"
            value={etlStatsLoading ? '...' : etlStats?.total_jobs || 0}
            icon={Database}
            trend={{ 
              value: etlStats ? (etlStats.successful_jobs / etlStats.total_jobs) * 100 : 0, 
              isPositive: true 
            }}
            description={`${etlStats?.successful_jobs || 0} successful`}
          />
          <MetricCard
            title="Data Quality"
            value={qualityLoading ? '...' : `${qualitySummary?.overall_score.toFixed(1) || 0}%`}
            icon={Activity}
            trend={{ 
              value: qualitySummary?.overall_score || 0, 
              isPositive: (qualitySummary?.overall_score || 0) > 80 
            }}
            description={`${qualitySummary?.passing_metrics || 0} metrics passing`}
          />
          <MetricCard
            title="System Health"
            value={systemLoading ? '...' : systemHealth?.overall_status || 'Unknown'}
            icon={Server}
            trend={{ 
              value: systemHealth?.cpu_usage || 0, 
              isPositive: systemHealth?.overall_status === 'healthy' 
            }}
            description={`CPU: ${systemHealth?.cpu_usage.toFixed(1) || 0}%`}
          />
          <MetricCard
            title="Active Alerts"
            value={alertLoading ? '...' : alertSummary?.active_alerts || 0}
            icon={AlertTriangle}
            trend={{ 
              value: alertSummary?.critical_alerts || 0, 
              isPositive: alertSummary?.active_alerts === 0 
            }}
            description={`${alertSummary?.critical_alerts || 0} critical`}
          />
        </div>

        {/* Recent ETL Jobs */}
        <DataTable
          data={etlJobs?.slice(0, 10) || []}
          columns={jobColumns}
          title="Recent ETL Jobs"
          emptyMessage="No ETL jobs available"
        />

        {/* System Status */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex items-center">
              <StatusBadge status="success" label="ETL Pipeline" />
              <span className="ml-2 text-sm text-gray-500">Running</span>
            </div>
            <div className="flex items-center">
              <StatusBadge status="success" label="Database" />
              <span className="ml-2 text-sm text-gray-500">Connected</span>
            </div>
            <div className="flex items-center">
              <StatusBadge status="warning" label="API Rate Limit" />
              <span className="ml-2 text-sm text-gray-500">85% used</span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}