import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryConfigs } from '@/lib/query-client'

// Tipos para dados ETL
export interface ETLJob {
  id: number
  name: string
  status: 'running' | 'completed' | 'failed' | 'pending'
  started_at: string
  completed_at: string | null
  duration: number | null
  records_processed: number
  error_message: string | null
}

export interface ETLStats {
  total_jobs: number
  successful_jobs: number
  failed_jobs: number
  running_jobs: number
  avg_duration: number
  total_records: number
}

// Hook para buscar jobs ETL
export function useETLJobs() {
  return useQuery({
    queryKey: ['etl', 'jobs'],
    queryFn: async (): Promise<ETLJob[]> => {
      const { data, error } = await supabase
        .from('etl_jobs')
        .select('*')
        .order('started_at', { ascending: false })
        .limit(50)
      
      if (error) throw error
      return data || []
    },
    ...queryConfigs.etl,
  })
}

// Hook para buscar estatísticas ETL
export function useETLStats() {
  return useQuery({
    queryKey: ['etl', 'stats'],
    queryFn: async (): Promise<ETLStats> => {
      const { data, error } = await supabase
        .from('etl_jobs')
        .select('status, duration, records_processed')
      
      if (error) throw error
      
      const jobs = data || []
      const totalJobs = jobs.length
      const successfulJobs = jobs.filter(job => job.status === 'completed').length
      const failedJobs = jobs.filter(job => job.status === 'failed').length
      const runningJobs = jobs.filter(job => job.status === 'running').length
      const avgDuration = jobs.reduce((sum, job) => sum + (job.duration || 0), 0) / totalJobs
      const totalRecords = jobs.reduce((sum, job) => sum + (job.records_processed || 0), 0)
      
      return {
        total_jobs: totalJobs,
        successful_jobs: successfulJobs,
        failed_jobs: failedJobs,
        running_jobs: runningJobs,
        avg_duration: avgDuration,
        total_records: totalRecords,
      }
    },
    ...queryConfigs.etl,
  })
}

// Hook para buscar job específico
export function useETLJob(jobId: number) {
  return useQuery({
    queryKey: ['etl', 'job', jobId],
    queryFn: async (): Promise<ETLJob | null> => {
      const { data, error } = await supabase
        .from('etl_jobs')
        .select('*')
        .eq('id', jobId)
        .single()
      
      if (error) throw error
      return data
    },
    enabled: !!jobId,
    ...queryConfigs.etl,
  })
}

// Hook para executar job ETL
export function useRunETLJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (jobName: string) => {
      const { data, error } = await supabase
        .from('etl_jobs')
        .insert({
          name: jobName,
          status: 'running',
          started_at: new Date().toISOString(),
        })
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: () => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['etl'] })
    },
  })
}

// Hook para cancelar job ETL
export function useCancelETLJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (jobId: number) => {
      const { error } = await supabase
        .from('etl_jobs')
        .update({
          status: 'failed',
          completed_at: new Date().toISOString(),
          error_message: 'Job cancelled by user',
        })
        .eq('id', jobId)
      
      if (error) throw error
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['etl'] })
    },
  })
}
