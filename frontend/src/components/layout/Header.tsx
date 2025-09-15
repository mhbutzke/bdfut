'use client'

import { useState } from 'react'
import { BarChart3, Database, Home, Menu, Bell, Search, User } from 'lucide-react'
import NavLink from '../navigation/NavLink'
import MobileNav from '../navigation/MobileNav'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <>
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 mr-2"
              >
                <Menu className="h-5 w-5" />
              </button>
              <Database className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                BDFut Dashboard
              </span>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex space-x-1">
              <NavLink href="/" icon={<Home className="h-4 w-4" />}>
                Overview
              </NavLink>
              <NavLink href="/etl" icon={<BarChart3 className="h-4 w-4" />}>
                ETL Jobs
              </NavLink>
              <NavLink href="/data-quality" icon={<Database className="h-4 w-4" />}>
                Data Quality
              </NavLink>
              <NavLink href="/metrics" icon={<BarChart3 className="h-4 w-4" />}>
                Metrics
              </NavLink>
            </nav>

            {/* Actions */}
            <div className="flex items-center space-x-2">
              <button className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100">
                <Search className="h-5 w-5" />
              </button>
              <button className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100">
                <Bell className="h-5 w-5" />
              </button>
              <button className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100">
                <User className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <MobileNav 
        isOpen={mobileMenuOpen} 
        onClose={() => setMobileMenuOpen(false)} 
      />
    </>
  )
}
