import { InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  icon?: React.ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', label, error, helperText, icon, ...props }, ref) => {
    const inputClasses = `
      flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm 
      placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 
      focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50
      ${error ? 'border-red-500 focus:ring-red-500' : ''}
      ${icon ? 'pl-10' : ''}
      ${className}
    `.trim()

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{icon}</span>
            </div>
          )}
          <input
            className={inputClasses}
            ref={ref}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
