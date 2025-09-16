import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryConfigs } from '@/lib/query-client'

// Tipos para métricas do sistema
export interface SystemMetric {
  id: number
  metric_name: string
  value: number
  unit: string
  status: 'healthy' | 'warning' | 'critical'
  timestamp: string
  description: string
}

export interface SystemHealth {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_latency: number
  database_connections: number
  overall_status: 'healthy' | 'warning' | 'critical'
}

// Hook para buscar métricas do sistema
export function useSystemMetrics() {
  return useQuery({
    queryKey: ['system', 'metrics'],
    queryFn: async (): Promise<SystemMetric[]> => {
      const { data, error } = await supabase
        .from('system_metrics')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(100)
      
      if (error) throw error
      return data || []
    },
    ...queryConfigs.realtime,
  })
}

// Hook para buscar saúde do sistema
export function useSystemHealth() {
  return useQuery({
    queryKey: ['system', 'health'],
    queryFn: async (): Promise<SystemHealth> => {
      const { data, error } = await supabase
        .from('system_metrics')
        .select('metric_name, value, status')
        .order('timestamp', { ascending: false })
        .limit(10)
      
      if (error) throw error
      
      const metrics = data || []
      const cpuUsage = metrics.find(m => m.metric_name === 'cpu_usage')?.value || 0
      const memoryUsage = metrics.find(m => m.metric_name === 'memory_usage')?.value || 0
      const diskUsage = metrics.find(m => m.metric_name === 'disk_usage')?.value || 0
      const networkLatency = metrics.find(m => m.metric_name === 'network_latency')?.value || 0
      const dbConnections = metrics.find(m => m.metric_name === 'database_connections')?.value || 0
      
      // Determinar status geral baseado nas métricas
      let overallStatus: 'healthy' | 'warning' | 'critical' = 'healthy'
      if (cpuUsage > 90 || memoryUsage > 90 || diskUsage > 90) {
        overallStatus = 'critical'
      } else if (cpuUsage > 80 || memoryUsage > 80 || diskUsage > 80) {
        overallStatus = 'warning'
      }
      
      return {
        cpu_usage: cpuUsage,
        memory_usage: memoryUsage,
        disk_usage: diskUsage,
        network_latency: networkLatency,
        database_connections: dbConnections,
        overall_status: overallStatus,
      }
    },
    ...queryConfigs.realtime,
  })
}

// Hook para buscar métricas específicas
export function useSystemMetric(metricName: string) {
  return useQuery({
    queryKey: ['system', 'metric', metricName],
    queryFn: async (): Promise<SystemMetric[]> => {
      const { data, error } = await supabase
        .from('system_metrics')
        .select('*')
        .eq('metric_name', metricName)
        .order('timestamp', { ascending: false })
        .limit(50)
      
      if (error) throw error
      return data || []
    },
    enabled: !!metricName,
    ...queryConfigs.realtime,
  })
}
