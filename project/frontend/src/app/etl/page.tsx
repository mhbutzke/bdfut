'use client'

import Layout from '@/components/layout/Layout'
import DataTable from '@/components/ui/DataTable'
import StatusBadge from '@/components/ui/StatusBadge'
import { useLeagues, useSeasons } from '@/hooks/useSupabaseData'
// Icons removed as they're not used in this component

export default function ETLPage() {
  const { data: leagues } = useLeagues()
  const { data: seasons } = useSeasons()

  const leagueColumns = [
    { key: 'name' as const, label: 'League Name' },
    { key: 'country_id' as const, label: 'Country ID' },
    { key: 'updated_at' as const, label: 'Last Updated', render: (value: string) => new Date(value).toLocaleDateString() },
  ]

  const seasonColumns = [
    { key: 'name' as const, label: 'Season Name' },
    { key: 'league_id' as const, label: 'League ID' },
    { key: 'is_current_season' as const, label: 'Current', render: (value: boolean) => (
      <StatusBadge status={value ? 'success' : 'pending'} label={value ? 'Yes' : 'No'} />
    ) },
    { key: 'updated_at' as const, label: 'Last Updated', render: (value: string) => new Date(value).toLocaleDateString() },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ETL Jobs</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitoramento dos jobs de extração, transformação e carregamento
          </p>
        </div>

        {/* ETL Status */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">ETL Pipeline Status</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">✓</div>
              <div className="text-sm text-gray-500">Countries</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">✓</div>
              <div className="text-sm text-gray-500">Leagues</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">✓</div>
              <div className="text-sm text-gray-500">Seasons</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">⏳</div>
              <div className="text-sm text-gray-500">Fixtures</div>
            </div>
          </div>
        </div>

        {/* Leagues Table */}
        <DataTable
          data={leagues || []}
          columns={leagueColumns}
          title="Leagues Data"
          emptyMessage="No leagues data available"
        />

        {/* Seasons Table */}
        <DataTable
          data={seasons || []}
          columns={seasonColumns}
          title="Seasons Data"
          emptyMessage="No seasons data available"
        />
      </div>
    </Layout>
  )
}
