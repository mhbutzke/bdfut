import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryConfigs } from '@/lib/query-client'

// Tipos para alertas
export interface Alert {
  id: number
  title: string
  message: string
  type: 'error' | 'warning' | 'info' | 'success'
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'active' | 'acknowledged' | 'resolved'
  source: string
  created_at: string
  acknowledged_at: string | null
  resolved_at: string | null
  acknowledged_by: string | null
  resolved_by: string | null
}

export interface AlertSummary {
  total_alerts: number
  active_alerts: number
  acknowledged_alerts: number
  resolved_alerts: number
  critical_alerts: number
  high_alerts: number
  medium_alerts: number
  low_alerts: number
}

// Hook para buscar alertas
export function useAlerts(status?: string) {
  return useQuery({
    queryKey: ['alerts', status],
    queryFn: async (): Promise<Alert[]> => {
      let query = supabase
        .from('alerts')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100)
      
      if (status) {
        query = query.eq('status', status)
      }
      
      const { data, error } = await query
      if (error) throw error
      return data || []
    },
    ...queryConfigs.realtime,
  })
}

// Hook para buscar resumo de alertas
export function useAlertSummary() {
  return useQuery({
    queryKey: ['alerts', 'summary'],
    queryFn: async (): Promise<AlertSummary> => {
      const { data, error } = await supabase
        .from('alerts')
        .select('status, severity')
      
      if (error) throw error
      
      const alerts = data || []
      const totalAlerts = alerts.length
      const activeAlerts = alerts.filter(a => a.status === 'active').length
      const acknowledgedAlerts = alerts.filter(a => a.status === 'acknowledged').length
      const resolvedAlerts = alerts.filter(a => a.status === 'resolved').length
      const criticalAlerts = alerts.filter(a => a.severity === 'critical').length
      const highAlerts = alerts.filter(a => a.severity === 'high').length
      const mediumAlerts = alerts.filter(a => a.severity === 'medium').length
      const lowAlerts = alerts.filter(a => a.severity === 'low').length
      
      return {
        total_alerts: totalAlerts,
        active_alerts: activeAlerts,
        acknowledged_alerts: acknowledgedAlerts,
        resolved_alerts: resolvedAlerts,
        critical_alerts: criticalAlerts,
        high_alerts: highAlerts,
        medium_alerts: mediumAlerts,
        low_alerts: lowAlerts,
      }
    },
    ...queryConfigs.realtime,
  })
}

// Hook para buscar alerta específico
export function useAlert(alertId: number) {
  return useQuery({
    queryKey: ['alerts', 'detail', alertId],
    queryFn: async (): Promise<Alert | null> => {
      const { data, error } = await supabase
        .from('alerts')
        .select('*')
        .eq('id', alertId)
        .single()
      
      if (error) throw error
      return data
    },
    enabled: !!alertId,
    ...queryConfigs.realtime,
  })
}

// Hook para reconhecer alerta
export function useAcknowledgeAlert() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ alertId, userId }: { alertId: number; userId: string }) => {
      const { data, error } = await supabase
        .from('alerts')
        .update({
          status: 'acknowledged',
          acknowledged_at: new Date().toISOString(),
          acknowledged_by: userId,
        })
        .eq('id', alertId)
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}

// Hook para resolver alerta
export function useResolveAlert() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ alertId, userId }: { alertId: number; userId: string }) => {
      const { data, error } = await supabase
        .from('alerts')
        .update({
          status: 'resolved',
          resolved_at: new Date().toISOString(),
          resolved_by: userId,
        })
        .eq('id', alertId)
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}
