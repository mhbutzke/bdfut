import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryConfigs } from '@/lib/query-client'

// Tipos para dados de qualidade
export interface DataQualityMetric {
  id: number
  table_name: string
  metric_name: string
  value: number
  threshold: number
  status: 'pass' | 'fail' | 'warning'
  last_checked: string
  description: string
}

export interface DataQualitySummary {
  total_metrics: number
  passing_metrics: number
  failing_metrics: number
  warning_metrics: number
  overall_score: number
}

// Hook para buscar métricas de qualidade
export function useDataQualityMetrics() {
  return useQuery({
    queryKey: ['data-quality', 'metrics'],
    queryFn: async (): Promise<DataQualityMetric[]> => {
      const { data, error } = await supabase
        .from('data_quality_metrics')
        .select('*')
        .order('table_name', { ascending: true })
      
      if (error) throw error
      return data || []
    },
    ...queryConfigs.realtime,
  })
}

// Hook para buscar resumo de qualidade
export function useDataQualitySummary() {
  return useQuery({
    queryKey: ['data-quality', 'summary'],
    queryFn: async (): Promise<DataQualitySummary> => {
      const { data, error } = await supabase
        .from('data_quality_metrics')
        .select('status')
      
      if (error) throw error
      
      const metrics = data || []
      const totalMetrics = metrics.length
      const passingMetrics = metrics.filter(m => m.status === 'pass').length
      const failingMetrics = metrics.filter(m => m.status === 'fail').length
      const warningMetrics = metrics.filter(m => m.status === 'warning').length
      const overallScore = totalMetrics > 0 ? (passingMetrics / totalMetrics) * 100 : 0
      
      return {
        total_metrics: totalMetrics,
        passing_metrics: passingMetrics,
        failing_metrics: failingMetrics,
        warning_metrics: warningMetrics,
        overall_score: overallScore,
      }
    },
    ...queryConfigs.realtime,
  })
}

// Hook para buscar métricas por tabela
export function useDataQualityByTable(tableName: string) {
  return useQuery({
    queryKey: ['data-quality', 'table', tableName],
    queryFn: async (): Promise<DataQualityMetric[]> => {
      const { data, error } = await supabase
        .from('data_quality_metrics')
        .select('*')
        .eq('table_name', tableName)
        .order('metric_name', { ascending: true })
      
      if (error) throw error
      return data || []
    },
    enabled: !!tableName,
    ...queryConfigs.realtime,
  })
}
