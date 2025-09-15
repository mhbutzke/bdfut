'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, X, CheckCircle, Clock, Bell } from 'lucide-react'
import StatusBadge from '@/components/ui/StatusBadge'
import Card from '@/components/ui/Card'

interface Alert {
  id: string
  title: string
  message: string
  type: 'error' | 'warning' | 'info' | 'success'
  severity: 'low' | 'medium' | 'high' | 'critical'
  timestamp: Date
  source: string
  acknowledged: boolean
}

interface RealtimeAlertsProps {
  alerts: Alert[]
  onAcknowledge?: (alertId: string) => void
  onDismiss?: (alertId: string) => void
  maxAlerts?: number
}

export default function RealtimeAlerts({ 
  alerts, 
  onAcknowledge, 
  onDismiss, 
  maxAlerts = 10 
}: RealtimeAlertsProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      default:
        return <Bell className="h-5 w-5 text-blue-500" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <StatusBadge status="error" label="Critical" />
      case 'high':
        return <StatusBadge status="error" label="High" />
      case 'medium':
        return <StatusBadge status="warning" label="Medium" />
      default:
        return <StatusBadge status="pending" label="Low" />
    }
  }

  const formatTimeAgo = (timestamp: Date) => {
    const diff = currentTime.getTime() - timestamp.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return `${seconds}s ago`
  }

  const recentAlerts = alerts
    .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    .slice(0, maxAlerts)

  const criticalAlerts = alerts.filter(alert => alert.severity === 'critical').length
  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged).length

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bell className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
        </div>
        <div className="flex items-center space-x-4 text-sm">
          {criticalAlerts > 0 && (
            <div className="flex items-center space-x-1 text-red-600">
              <AlertTriangle className="h-4 w-4" />
              <span>{criticalAlerts} Critical</span>
            </div>
          )}
          <div className="flex items-center space-x-1 text-gray-600">
            <Clock className="h-4 w-4" />
            <span>{unacknowledgedAlerts} Unacknowledged</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {recentAlerts.length === 0 ? (
          <Card className="p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">All Clear</h4>
            <p className="text-gray-600">No recent alerts</p>
          </Card>
        ) : (
          recentAlerts.map((alert) => (
            <Card key={alert.id} className={`p-4 border-l-4 ${
              alert.severity === 'critical' ? 'border-l-red-500' :
              alert.severity === 'high' ? 'border-l-red-400' :
              alert.severity === 'medium' ? 'border-l-yellow-500' :
              'border-l-blue-500'
            }`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getAlertIcon(alert.type)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="text-sm font-medium text-gray-900">{alert.title}</h4>
                      {getSeverityBadge(alert.severity)}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>Source: {alert.source}</span>
                      <span>•</span>
                      <span>{formatTimeAgo(alert.timestamp)}</span>
                      {alert.acknowledged && (
                        <>
                          <span>•</span>
                          <span className="text-green-600">Acknowledged</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {!alert.acknowledged && onAcknowledge && (
                    <button
                      onClick={() => onAcknowledge(alert.id)}
                      className="p-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded"
                      title="Acknowledge"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </button>
                  )}
                  {onDismiss && (
                    <button
                      onClick={() => onDismiss(alert.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
                      title="Dismiss"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
