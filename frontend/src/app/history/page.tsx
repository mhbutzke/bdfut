'use client'

import Layout from '@/components/layout/Layout'
import DataTable from '@/components/ui/DataTable'
import { Calendar, Clock, Database } from 'lucide-react'

type HistoryItem = {
  id: number
  job: string
  status: string
  started: string
  completed: string
  duration: string
  records: number
}

export default function HistoryPage() {
  const historyData: HistoryItem[] = [
    {
      id: 1,
      job: 'Premier League Sync',
      status: 'completed',
      started: '2025-01-13 14:00:00',
      completed: '2025-01-13 14:05:00',
      duration: '5m 23s',
      records: 1250
    },
    {
      id: 2,
      job: 'La Liga Sync',
      status: 'completed',
      started: '2025-01-13 13:30:00',
      completed: '2025-01-13 13:35:00',
      duration: '4m 45s',
      records: 980
    },
    {
      id: 3,
      job: 'Bundesliga Sync',
      status: 'failed',
      started: '2025-01-13 13:00:00',
      completed: '2025-01-13 13:02:00',
      duration: '2m 15s',
      records: 0
    },
    {
      id: 4,
      job: 'Serie A Sync',
      status: 'completed',
      started: '2025-01-13 12:30:00',
      completed: '2025-01-13 12:35:00',
      duration: '5m 10s',
      records: 1100
    },
    {
      id: 5,
      job: 'Ligue 1 Sync',
      status: 'running',
      started: '2025-01-13 12:00:00',
      completed: '',
      duration: 'Running...',
      records: 0
    }
  ]

  const columns = [
    { key: 'job' as keyof HistoryItem, label: 'Job Name' },
    { key: 'status' as keyof HistoryItem, label: 'Status' },
    { key: 'started' as keyof HistoryItem, label: 'Started' },
    { key: 'completed' as keyof HistoryItem, label: 'Completed' },
    { key: 'duration' as keyof HistoryItem, label: 'Duration' },
    { key: 'records' as keyof HistoryItem, label: 'Records' }
  ]

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Job History</h1>
          <p className="mt-2 text-gray-600">
            View the execution history of all ETL jobs
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-md p-3 text-white">
                <Database className="h-6 w-6" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Jobs
                </dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {historyData.length}
                </dd>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-md p-3 text-white">
                <Clock className="h-6 w-6" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Success Rate
                </dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {Math.round((historyData.filter(item => item.status === 'completed').length / historyData.length) * 100)}%
                </dd>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-500 rounded-md p-3 text-white">
                <Calendar className="h-6 w-6" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Records Today
                </dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {historyData.reduce((sum, item) => sum + item.records, 0).toLocaleString()}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <DataTable
          data={historyData}
          columns={columns}
          title="Recent Job Executions"
          emptyMessage="No job history available"
        />
      </div>
    </Layout>
  )
}
