'use client'

import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Card from '@/components/ui/Card'
import Modal from '@/components/ui/Modal'
import { User, Shield, LogOut, Edit, Save, X, AlertCircle, CheckCircle } from 'lucide-react'

interface UserProfileProps {
  className?: string
}

export default function UserProfile({ className }: UserProfileProps) {
  const { user, signOut, updateProfile } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: user?.user_metadata?.name || '',
    email: user?.email || ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleEdit = () => {
    setFormData({
      name: user?.user_metadata?.name || '',
      email: user?.email || ''
    })
    setIsEditing(true)
    setError('')
    setSuccess('')
  }

  const handleCancel = () => {
    setIsEditing(false)
    setError('')
    setSuccess('')
  }

  const handleSave = async () => {
    setIsLoading(true)
    setError('')
    setSuccess('')

    try {
      await updateProfile({
        data: {
          name: formData.name
        }
      })
      setSuccess('Perfil atualizado com sucesso!')
      setIsEditing(false)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Erro ao atualizar perfil')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignOut = async () => {
    setIsLoading(true)
    try {
      await signOut()
    } catch {
      setError('Erro ao fazer logout')
    } finally {
      setIsLoading(false)
    }
  }

  const getUserRole = () => {
    // Mock role based on email domain or other logic
    if (user?.email?.includes('admin')) return 'Administrador'
    if (user?.email?.includes('manager')) return 'Gerente'
    return 'Usuário'
  }

  const getRoleColor = () => {
    const role = getUserRole()
    switch (role) {
      case 'Administrador':
        return 'text-red-600 bg-red-50'
      case 'Gerente':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (!user) return null

  return (
    <div className={className}>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Perfil do Usuário</h2>
          {!isEditing && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleEdit}
              disabled={isLoading}
            >
              <Edit className="h-4 w-4 mr-2" />
              Editar
            </Button>
          )}
        </div>

        {error && (
          <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md mb-4">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
        )}

        {success && (
          <div className="flex items-center space-x-2 p-3 bg-green-50 border border-green-200 rounded-md mb-4">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-green-700">{success}</span>
          </div>
        )}

        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900">
                {isEditing ? (
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Nome completo"
                    disabled={isLoading}
                  />
                ) : (
                  user.user_metadata?.name || 'Usuário'
                )}
              </h3>
              <p className="text-sm text-gray-500">
                {isEditing ? (
                  <Input
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="Email"
                    disabled={true} // Email não pode ser alterado
                    className="mt-1"
                  />
                ) : (
                  user.email
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-600">Função:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor()}`}>
              {getUserRole()}
            </span>
          </div>

          <div className="text-sm text-gray-500">
            <p>Membro desde: {user.created_at ? new Date(user.created_at).toLocaleDateString('pt-BR') : 'N/A'}</p>
            <p>Último acesso: {user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleDateString('pt-BR') : 'N/A'}</p>
          </div>
        </div>

        {isEditing && (
          <div className="flex items-center space-x-2 mt-6 pt-4 border-t">
            <Button
              onClick={handleSave}
              disabled={isLoading || !formData.name.trim()}
              size="sm"
            >
              <Save className="h-4 w-4 mr-2" />
              Salvar
            </Button>
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
              size="sm"
            >
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
          </div>
        )}

        <div className="mt-6 pt-4 border-t">
          <Button
            variant="outline"
            onClick={() => setIsModalOpen(true)}
            disabled={isLoading}
            className="w-full"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sair da conta
          </Button>
        </div>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Confirmar logout"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Tem certeza que deseja sair da sua conta?
          </p>
          <div className="flex items-center space-x-2">
            <Button
              onClick={handleSignOut}
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? 'Saindo...' : 'Sim, sair'}
            </Button>
            <Button
              variant="outline"
              onClick={() => setIsModalOpen(false)}
              disabled={isLoading}
              className="flex-1"
            >
              Cancelar
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
