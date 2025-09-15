'use client'

import { Server, Database, Activity, Globe, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'
import StatusBadge from '@/components/ui/StatusBadge'
import Card from '@/components/ui/Card'

interface SystemComponent {
  id: string
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime: string
  responseTime?: number
  lastCheck: Date
  description?: string
}

interface SystemStatusProps {
  components: SystemComponent[]
  overallStatus: 'healthy' | 'degraded' | 'down'
}

export default function SystemStatus({ components, overallStatus }: SystemStatusProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'down':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return <StatusBadge status="success" label="Healthy" />
      case 'degraded':
        return <StatusBadge status="warning" label="Degraded" />
      case 'down':
        return <StatusBadge status="error" label="Down" />
      default:
        return <StatusBadge status="pending" label="Unknown" />
    }
  }

  const getComponentIcon = (name: string) => {
    const lowerName = name.toLowerCase()
    if (lowerName.includes('database') || lowerName.includes('db')) {
      return <Database className="h-5 w-5 text-blue-500" />
    } else if (lowerName.includes('api') || lowerName.includes('server')) {
      return <Server className="h-5 w-5 text-purple-500" />
    } else if (lowerName.includes('network') || lowerName.includes('cdn')) {
      return <Globe className="h-5 w-5 text-green-500" />
    } else {
      return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  const healthyCount = components.filter(c => c.status === 'healthy').length
  const degradedCount = components.filter(c => c.status === 'degraded').length
  const downCount = components.filter(c => c.status === 'down').length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">System Status</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {getStatusIcon(overallStatus)}
            <span className="text-sm font-medium text-gray-900">Overall Status</span>
            {getStatusBadge(overallStatus)}
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card className="p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-500 rounded-md p-3 text-white">
              <CheckCircle className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Healthy</p>
              <p className="text-2xl font-semibold text-gray-900">{healthyCount}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3 text-white">
              <AlertTriangle className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Degraded</p>
              <p className="text-2xl font-semibold text-gray-900">{degradedCount}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-red-500 rounded-md p-3 text-white">
              <XCircle className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Down</p>
              <p className="text-2xl font-semibold text-gray-900">{downCount}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Component Status */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Status</h3>
        <div className="space-y-3">
          {components.map((component) => (
            <div key={component.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getComponentIcon(component.name)}
                <div>
                  <h4 className="text-sm font-medium text-gray-900">{component.name}</h4>
                  {component.description && (
                    <p className="text-xs text-gray-500">{component.description}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-gray-900">Uptime: {component.uptime}</p>
                  {component.responseTime && (
                    <p className="text-xs text-gray-500">
                      Response: {component.responseTime}ms
                    </p>
                  )}
                </div>
                {getStatusBadge(component.status)}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
