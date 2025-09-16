import Header from './Header'
import Sidebar from './Sidebar'
import Breadcrumb from '../navigation/Breadcrumb'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1">
          <div className="p-6">
            <div className="mb-6">
              <Breadcrumb />
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
