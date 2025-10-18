import { Suspense } from 'react'
import { Dashboard } from '@/components/dashboard/Dashboard'
import { Header } from '@/components/layout/Header'
import { Sidebar } from '@/components/layout/Sidebar'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <Suspense fallback={<LoadingSpinner />}>
            <Dashboard />
          </Suspense>
        </main>
      </div>
    </div>
  )
}