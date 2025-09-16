'use client'

import Layout from '@/components/layout/Layout'
import { UserProfile, ProtectedRoute } from '@/components/auth'

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <Layout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Perfil do Usuário</h1>
            <p className="mt-2 text-gray-600">
              Gerencie suas informações pessoais e configurações de conta
            </p>
          </div>

          <div className="max-w-2xl">
            <UserProfile />
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  )
}
