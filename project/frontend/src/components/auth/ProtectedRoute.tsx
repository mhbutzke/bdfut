'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { PageLoading } from '@/components/ui/Loading'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: 'admin' | 'manager' | 'user'
  fallback?: React.ReactNode
}

export default function ProtectedRoute({ 
  children, 
  requiredRole, 
  fallback 
}: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  // Show loading while checking authentication
  if (loading) {
    return fallback || <PageLoading />
  }

  // Redirect to login if not authenticated
  if (!user) {
    return null
  }

  // Check role-based access if required
  if (requiredRole) {
    const userRole = getUserRole(user)
    if (!hasRequiredRole(userRole, requiredRole)) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Acesso Negado</h2>
            <p className="text-gray-600 mb-4">
              Você não tem permissão para acessar esta página.
            </p>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Voltar ao Dashboard
            </button>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}

function getUserRole(user: { email?: string }): string {
  // Mock role logic - in real app, this would come from user metadata or database
  if (user.email?.includes('admin')) return 'admin'
  if (user.email?.includes('manager')) return 'manager'
  return 'user'
}

function hasRequiredRole(userRole: string, requiredRole: string): boolean {
  const roleHierarchy = {
    'user': 1,
    'manager': 2,
    'admin': 3
  }

  const userLevel = roleHierarchy[userRole as keyof typeof roleHierarchy] || 1
  const requiredLevel = roleHierarchy[requiredRole as keyof typeof roleHierarchy] || 1

  return userLevel >= requiredLevel
}
