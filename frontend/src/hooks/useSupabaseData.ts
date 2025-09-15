import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'

// Hook para buscar países
export function useCountries() {
  return useQuery({
    queryKey: ['countries'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('countries')
        .select('*')
        .order('name')
      
      if (error) throw error
      return data
    },
  })
}

// Hook para buscar ligas
export function useLeagues() {
  return useQuery({
    queryKey: ['leagues'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('leagues')
        .select('*')
        .order('name')
      
      if (error) throw error
      return data
    },
  })
}

// Hook para buscar temporadas
export function useSeasons() {
  return useQuery({
    queryKey: ['seasons'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('seasons')
        .select('*')
        .order('name')
      
      if (error) throw error
      return data
    },
  })
}

// Hook para buscar fixtures recentes
export function useRecentFixtures(limit = 10) {
  return useQuery({
    queryKey: ['fixtures', 'recent', limit],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('fixtures')
        .select('*')
        .order('starting_at', { ascending: false })
        .limit(limit)
      
      if (error) throw error
      return data
    },
  })
}

// Hook para estatísticas gerais
export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const [countriesResult, leaguesResult, seasonsResult, fixturesResult] = await Promise.all([
        supabase.from('countries').select('id', { count: 'exact', head: true }),
        supabase.from('leagues').select('id', { count: 'exact', head: true }),
        supabase.from('seasons').select('id', { count: 'exact', head: true }),
        supabase.from('fixtures').select('id', { count: 'exact', head: true }),
      ])

      return {
        countries: countriesResult.count || 0,
        leagues: leaguesResult.count || 0,
        seasons: seasonsResult.count || 0,
        fixtures: fixturesResult.count || 0,
      }
    },
  })
}
