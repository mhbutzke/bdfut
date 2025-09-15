import Layout from '@/components/layout/Layout'
import MetricCard from '@/components/ui/MetricCard'
import { TrendingUp, Activity, Clock, Zap } from 'lucide-react'

export default function MetricsPage() {
  // Mock data - em produção viria do Supabase
  const metrics = {
    apiCalls: 15420,
    dataProcessed: 892,
    avgResponseTime: 245,
    errorRate: 0.8,
  }

  const hourlyData = [
    { hour: '00:00', calls: 120, errors: 1 },
    { hour: '01:00', calls: 95, errors: 0 },
    { hour: '02:00', calls: 78, errors: 0 },
    { hour: '03:00', calls: 65, errors: 1 },
    { hour: '04:00', calls: 89, errors: 0 },
    { hour: '05:00', calls: 134, errors: 2 },
    { hour: '06:00', calls: 198, errors: 1 },
    { hour: '07:00', calls: 245, errors: 3 },
    { hour: '08:00', calls: 312, errors: 2 },
    { hour: '09:00', calls: 289, errors: 1 },
    { hour: '10:00', calls: 267, errors: 0 },
    { hour: '11:00', calls: 234, errors: 1 },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Metrics</h1>
          <p className="mt-1 text-sm text-gray-500">
            Métricas de performance e uso do sistema
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="API Calls Today"
            value={metrics.apiCalls.toLocaleString()}
            icon={Activity}
            trend={{ value: 12.5, isPositive: true }}
            description="Total de chamadas à API Sportmonks"
          />
          <MetricCard
            title="Data Processed (MB)"
            value={metrics.dataProcessed}
            icon={TrendingUp}
            trend={{ value: 8.2, isPositive: true }}
            description="Dados processados hoje"
          />
          <MetricCard
            title="Avg Response Time (ms)"
            value={metrics.avgResponseTime}
            icon={Clock}
            trend={{ value: -5.3, isPositive: true }}
            description="Tempo médio de resposta"
          />
          <MetricCard
            title="Error Rate"
            value={`${metrics.errorRate}%`}
            icon={Zap}
            trend={{ value: -0.2, isPositive: true }}
            description="Taxa de erro das requisições"
          />
        </div>

        {/* Hourly Activity Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Hourly Activity</h3>
          <div className="space-y-3">
            {hourlyData.map((data) => (
              <div key={data.hour} className="flex items-center">
                <div className="w-16 text-sm text-gray-500">{data.hour}</div>
                <div className="flex-1 mx-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(data.calls / 350) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="w-20 text-sm text-gray-700">{data.calls} calls</div>
                <div className="w-16 text-sm text-red-500">{data.errors} errors</div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Trends */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Trends</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Response Time</span>
                <span className="text-sm font-medium text-green-600">↓ 5.3%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Throughput</span>
                <span className="text-sm font-medium text-green-600">↑ 12.5%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Error Rate</span>
                <span className="text-sm font-medium text-green-600">↓ 0.2%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Data Quality</span>
                <span className="text-sm font-medium text-green-600">↑ 2.1%</span>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">CPU Usage</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '45%' }} />
                  </div>
                  <span className="text-sm text-gray-700">45%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Memory Usage</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '72%' }} />
                  </div>
                  <span className="text-sm text-gray-700">72%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Disk Usage</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '38%' }} />
                  </div>
                  <span className="text-sm text-gray-700">38%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Network I/O</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '56%' }} />
                  </div>
                  <span className="text-sm text-gray-700">56%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
