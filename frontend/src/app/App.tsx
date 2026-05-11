/**
 * Root App component with providers, theme support, and routing
 */

import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import { useTheme } from '@/shared/hooks'
import { ProtectedRoute } from '@/shared/routing'
import { AdminLayout } from '@/shared/layout/AdminLayout'
import { AdminDashboardPage } from '@/pages/admin/DashboardPage'
import { IngredientsAdminPage } from '@/pages/admin/IngredientsPage'

// Create QueryClient for React Query
const queryClient = new QueryClient()

const HomePage: React.FC = () => (
  <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-50">
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Food Store - Welcome ✅</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Welcome Card */}
        <div className="bg-gradient-to-br from-sky-50 to-sky-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 border border-sky-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold mb-3">Welcome to Food Store</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            Frontend is now ready with routing, layout, and role-based access control.
          </p>
          <div className="flex gap-2 flex-wrap">
            <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">React 19</span>
            <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">React Router v6</span>
            <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">React Query</span>
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 border border-green-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold mb-3">Next Steps</h2>
          <ul className="space-y-2 text-gray-700 dark:text-gray-300 text-sm">
            <li>✓ Auth store with role-based access</li>
            <li>✓ Protected routes with RBAC</li>
            <li>✓ Admin layout with sidebar</li>
            <li>✓ Ingredientes page (CHANGE-04)</li>
            <li>→ Login/Register flow (CHANGE-01)</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
)

export const App: React.FC = () => {
  const { theme, applyTheme } = useTheme()

  // Apply theme on mount and when it changes
  useEffect(() => {
    applyTheme(theme)
  }, [theme, applyTheme])

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />

            {/* Admin routes - require STOCK or ADMIN role */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRoles={['ADMIN', 'STOCK', 'PEDIDOS']}>
                  <AdminLayout>
                    <AdminDashboardPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/admin/ingredientes"
              element={
                <ProtectedRoute requiredRoles={['STOCK', 'ADMIN']}>
                  <AdminLayout>
                    <IngredientsAdminPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </QueryClientProvider>
    </div>
  )
}
