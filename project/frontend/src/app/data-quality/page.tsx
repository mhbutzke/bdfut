import Layout from '@/components/layout/Layout'
import MetricCard from '@/components/ui/MetricCard'
import StatusBadge from '@/components/ui/StatusBadge'
import { CheckCircle, XCircle, AlertTriangle, Database } from 'lucide-react'

export default function DataQualityPage() {
  // Mock data - em produção viria do Supabase
  const qualityMetrics = {
    completeness: 95.2,
    accuracy: 98.7,
    consistency: 92.1,
    timeliness: 89.3,
  }

  const qualityChecks = [
    { name: 'Countries Data', status: 'success' as const, score: 98 },
    { name: 'Leagues Data', status: 'success' as const, score: 96 },
    { name: 'Seasons Data', status: 'warning' as const, score: 87 },
    { name: 'Fixtures Data', status: 'error' as const, score: 72 },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Quality</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitoramento da qualidade dos dados coletados
          </p>
        </div>

        {/* Quality Metrics */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Completeness"
            value={`${qualityMetrics.completeness}%`}
            icon={CheckCircle}
            trend={{ value: 2.1, isPositive: true }}
            description="Dados completos vs esperados"
          />
          <MetricCard
            title="Accuracy"
            value={`${qualityMetrics.accuracy}%`}
            icon={Database}
            trend={{ value: 0.8, isPositive: true }}
            description="Precisão dos dados"
          />
          <MetricCard
            title="Consistency"
            value={`${qualityMetrics.consistency}%`}
            icon={AlertTriangle}
            trend={{ value: -1.2, isPositive: false }}
            description="Consistência entre fontes"
          />
          <MetricCard
            title="Timeliness"
            value={`${qualityMetrics.timeliness}%`}
            icon={XCircle}
            trend={{ value: -3.1, isPositive: false }}
            description="Atualização em tempo"
          />
        </div>

        {/* Quality Checks */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Checks</h3>
          <div className="space-y-4">
            {qualityChecks.map((check) => (
              <div key={check.name} className="flex items-center justify-between">
                <div className="flex items-center">
                  <StatusBadge status={check.status} />
                  <span className="ml-3 text-sm font-medium text-gray-900">
                    {check.name}
                  </span>
                </div>
                <div className="flex items-center">
                  <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                    <div
                      className={`h-2 rounded-full ${
                        check.score >= 90 ? 'bg-green-500' :
                        check.score >= 80 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${check.score}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-500">{check.score}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Quality Rules */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Rules</h3>
          <div className="space-y-3">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
              <span className="text-sm text-gray-700">Countries must have valid ISO codes</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
              <span className="text-sm text-gray-700">Leagues must be associated with valid countries</span>
            </div>
            <div className="flex items-center">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mr-3" />
              <span className="text-sm text-gray-700">Seasons must have valid date ranges</span>
            </div>
            <div className="flex items-center">
              <XCircle className="h-5 w-5 text-red-500 mr-3" />
              <span className="text-sm text-gray-700">Fixtures must have valid team references</span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
