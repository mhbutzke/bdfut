/**
 * Configuração de variáveis de ambiente
 * Para desenvolvimento, criar arquivo .env.local na raiz do projeto frontend
 */

export const env = {
  supabase: {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
  },
  app: {
    env: process.env.NEXT_PUBLIC_APP_ENV || 'development',
  },
} as const

// Validação das variáveis obrigatórias
export function validateEnv() {
  const requiredVars = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
  ]

  const missing = requiredVars.filter(varName => !process.env[varName])
  
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
      'Please create a .env.local file in the frontend directory with the required variables.'
    )
  }
}
