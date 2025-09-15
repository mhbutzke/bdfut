'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ReactNode } from 'react'

interface NavLinkProps {
  href: string
  children: ReactNode
  icon?: ReactNode
  exact?: boolean
  className?: string
}

export default function NavLink({ 
  href, 
  children, 
  icon, 
  exact = false, 
  className = '' 
}: NavLinkProps) {
  const pathname = usePathname()
  
  const isActive = exact 
    ? pathname === href 
    : pathname.startsWith(href)
  
  const baseClasses = 'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200'
  const activeClasses = 'bg-blue-100 text-blue-900'
  const inactiveClasses = 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
  
  const classes = `${baseClasses} ${isActive ? activeClasses : inactiveClasses} ${className}`
  
  return (
    <Link href={href} className={classes}>
      {icon && (
        <span className={`mr-3 flex-shrink-0 ${isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'}`}>
          {icon}
        </span>
      )}
      {children}
    </Link>
  )
}
