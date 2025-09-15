import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  title?: string
  subtitle?: string
  actions?: ReactNode
  padding?: 'sm' | 'md' | 'lg'
  shadow?: 'sm' | 'md' | 'lg'
}

export default function Card({ 
  children, 
  className = '', 
  title, 
  subtitle, 
  actions,
  padding = 'md',
  shadow = 'md'
}: CardProps) {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }
  
  const shadowClasses = {
    sm: 'shadow-sm',
    md: 'shadow',
    lg: 'shadow-lg',
  }
  
  const classes = `bg-white rounded-lg border border-gray-200 ${paddingClasses[padding]} ${shadowClasses[shadow]} ${className}`
  
  return (
    <div className={classes}>
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-gray-900">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">
                {subtitle}
              </p>
            )}
          </div>
          {actions && (
            <div className="flex items-center space-x-2">
              {actions}
            </div>
          )}
        </div>
      )}
      {children}
    </div>
  )
}
