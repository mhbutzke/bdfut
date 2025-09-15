import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryConfigs } from '@/lib/query-client'

// Tipos para dados de usuário
export interface UserProfile {
  id: string
  email: string
  name: string
  avatar_url: string | null
  role: 'admin' | 'user' | 'viewer'
  created_at: string
  last_login: string | null
  preferences: {
    theme: 'light' | 'dark' | 'auto'
    notifications: boolean
    language: string
  }
}

export interface UserActivity {
  id: number
  user_id: string
  action: string
  resource: string
  timestamp: string
  ip_address: string
  user_agent: string
}

// Hook para buscar perfil do usuário
export function useUserProfile(userId?: string) {
  return useQuery({
    queryKey: ['user', 'profile', userId],
    queryFn: async (): Promise<UserProfile | null> => {
      if (!userId) return null
      
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', userId)
        .single()
      
      if (error) throw error
      return data
    },
    enabled: !!userId,
    ...queryConfigs.user,
  })
}

// Hook para buscar atividades do usuário
export function useUserActivity(userId?: string) {
  return useQuery({
    queryKey: ['user', 'activity', userId],
    queryFn: async (): Promise<UserActivity[]> => {
      if (!userId) return []
      
      const { data, error } = await supabase
        .from('user_activities')
        .select('*')
        .eq('user_id', userId)
        .order('timestamp', { ascending: false })
        .limit(50)
      
      if (error) throw error
      return data || []
    },
    enabled: !!userId,
    ...queryConfigs.user,
  })
}

// Hook para atualizar perfil do usuário
export function useUpdateUserProfile() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ userId, updates }: { userId: string; updates: Partial<UserProfile> }) => {
      const { data, error } = await supabase
        .from('user_profiles')
        .update(updates)
        .eq('id', userId)
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile', data.id] })
    },
  })
}

// Hook para buscar todos os usuários (admin only)
export function useAllUsers() {
  return useQuery({
    queryKey: ['users', 'all'],
    queryFn: async (): Promise<UserProfile[]> => {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data || []
    },
    ...queryConfigs.static,
  })
}
