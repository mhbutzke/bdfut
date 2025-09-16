'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, 
  BarChart3, 
  Database, 
  Activity,
  TrendingUp,
  AlertTriangle,
  Clock
} from 'lucide-react'

const navigation = [
  { name: 'Overview', href: '/', icon: Home },
  { name: 'ETL Jobs', href: '/etl', icon: BarChart3 },
  { name: 'Data Quality', href: '/data-quality', icon: Database },
  { name: 'Metrics', href: '/metrics', icon: TrendingUp },
  { name: 'Health Check', href: '/health', icon: Activity },
  { name: 'Alerts', href: '/alerts', icon: AlertTriangle },
  { name: 'Recent Activity', href: '/activity', icon: Clock },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow pt-5 bg-gray-50 overflow-y-auto">
        <div className="flex items-center flex-shrink-0 px-4">
          <Database className="h-8 w-8 text-blue-600" />
          <span className="ml-2 text-lg font-semibold text-gray-900">
            BDFut
          </span>
        </div>
        
        <div className="mt-5 flex-grow flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`${
                    isActive
                      ? 'bg-blue-100 text-blue-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
                >
                  <item.icon
                    className={`${
                      isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    } mr-3 h-5 w-5`}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </div>
  )
}
