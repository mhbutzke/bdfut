import { Loader2 } from 'lucide-react'

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  className?: string
}

export default function Loading({ size = 'md', text, className = '' }: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  }
  
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Loader2 className={`animate-spin ${sizeClasses[size]}`} />
      {text && (
        <span className="ml-2 text-sm text-gray-600">{text}</span>
      )}
    </div>
  )
}

// Componente para loading de página inteira
export function PageLoading({ text = 'Carregando...' }: { text?: string }) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Loading size="lg" />
        <p className="mt-4 text-lg text-gray-600">{text}</p>
      </div>
    </div>
  )
}

// Componente para loading de componente
export function ComponentLoading({ text = 'Carregando...' }: { text?: string }) {
  return (
    <div className="flex items-center justify-center p-8">
      <Loading text={text} />
    </div>
  )
}
