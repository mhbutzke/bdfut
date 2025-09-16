'use client'

import Layout from '@/components/layout/Layout'
import Card from '@/components/ui/Card'
import StatusBadge from '@/components/ui/StatusBadge'
import { AlertTriangle, Clock, CheckCircle, XCircle } from 'lucide-react'

export default function AlertsPage() {
  const alerts = [
    {
      id: 1,
      type: 'error',
      title: 'ETL Job Failed',
      message: 'Data sync job for Premier League failed after 3 retries',
      timestamp: '2025-01-13 14:30:00',
      severity: 'high'
    },
    {
      id: 2,
      type: 'warning',
      title: 'High Memory Usage',
      message: 'Database memory usage is above 85%',
      timestamp: '2025-01-13 14:25:00',
      severity: 'medium'
    },
    {
      id: 3,
      type: 'info',
      title: 'Data Quality Check',
      message: 'New data quality rules have been applied',
      timestamp: '2025-01-13 14:20:00',
      severity: 'low'
    },
    {
      id: 4,
      type: 'success',
      title: 'Backup Completed',
      message: 'Daily backup completed successfully',
      timestamp: '2025-01-13 14:15:00',
      severity: 'low'
    }
  ]

  const getIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      default:
        return <Clock className="h-5 w-5 text-blue-500" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return <StatusBadge status="error" label="High" />
      case 'medium':
        return <StatusBadge status="warning" label="Medium" />
      default:
        return <StatusBadge status="pending" label="Low" />
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">System Alerts</h1>
          <p className="mt-2 text-gray-600">
            Monitor system alerts and notifications
          </p>
        </div>

        <div className="grid gap-6">
          {alerts.map((alert) => (
            <Card key={alert.id} className="border-l-4 border-l-red-500">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {getIcon(alert.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">
                      {alert.title}
                    </h3>
                    {getSeverityBadge(alert.severity)}
                  </div>
                  <p className="mt-1 text-sm text-gray-600">
                    {alert.message}
                  </p>
                  <div className="mt-2 flex items-center text-xs text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    {new Date(alert.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <button className="text-gray-400 hover:text-gray-600">
                    <XCircle className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {alerts.length === 0 && (
          <Card className="text-center py-12">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Active Alerts
            </h3>
            <p className="text-gray-600">
              All systems are running normally
            </p>
          </Card>
        )}
      </div>
    </Layout>
  )
}
