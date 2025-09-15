'use client'

import { X } from 'lucide-react'
import NavLink from './NavLink'
import { 
  BarChart3, 
  Database, 
  Activity, 
  TrendingUp, 
  AlertTriangle, 
  Clock 
} from 'lucide-react'

interface MobileNavProps {
  isOpen: boolean
  onClose: () => void
}

export default function MobileNav({ isOpen, onClose }: MobileNavProps) {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'ETL Jobs', href: '/etl', icon: Database },
    { name: 'Data Quality', href: '/data-quality', icon: Activity },
    { name: 'Metrics', href: '/metrics', icon: TrendingUp },
    { name: 'Alerts', href: '/alerts', icon: AlertTriangle },
    { name: 'History', href: '/history', icon: Clock },
  ]

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
      
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-xl">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">BDFut</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <nav className="mt-4 px-4">
          <div className="space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                href={item.href}
                icon={<item.icon className="h-5 w-5" />}
                className="block"
              >
                {item.name}
              </NavLink>
            ))}
          </div>
        </nav>
      </div>
    </div>
  )
}
