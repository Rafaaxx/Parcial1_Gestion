/**
 * Root App component with providers, theme support, and routing
 */

import React, { useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { useTheme } from '@/shared/hooks';
import { ProtectedRoute } from '@/shared/routing';
import { Layout } from '@/shared/components/Navigation';
import { Skeleton, Spinner } from '@/shared/ui';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { UnauthorizedPage } from '@/pages/UnauthorizedPage';
import { AdminDashboardPage } from '@/pages/admin/DashboardPage';
import { IngredientsAdminPage } from '@/pages/admin/IngredientsPage';

// Create QueryClient for React Query
const queryClient = new QueryClient();

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
            <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">
              React Router v6
            </span>
            <span className="px-3 py-1 bg-sky-500 text-white rounded-full text-sm">
              React Query
            </span>
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
);

const PageSkeleton: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen">
    <Spinner size="lg" color="primary" label="Cargando página..." />
  </div>
);

interface PlaceholderPageProps {
  title: string;
}

const PlaceholderPage: React.FC<PlaceholderPageProps> = ({ title }) => (
  <div className="p-8">
    <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">{title}</h1>
    <p className="text-gray-600 dark:text-gray-400">Coming soon...</p>
  </div>
);

export const App: React.FC = () => {
  const { theme, applyTheme } = useTheme();

  // Apply theme on mount and when it changes
  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            {/* Protected routes - require authentication and specific roles */}
            <Route
              path="/app"
              element={
                <ProtectedRoute requiredRoles={['ADMIN', 'STOCK', 'PEDIDOS', 'CLIENT']}>
                  <Layout />
                </ProtectedRoute>
              }
            >
              {/* Dashboard - accessible to ADMIN, STOCK, PEDIDOS */}
              <Route
                path="dashboard"
                element={
                  <ProtectedRoute requiredRoles={['ADMIN', 'STOCK', 'PEDIDOS']}>
                    <AdminDashboardPage />
                  </ProtectedRoute>
                }
              />

              {/* Ingredients - accessible to STOCK, ADMIN */}
              <Route
                path="ingredients"
                element={
                  <ProtectedRoute requiredRoles={['STOCK', 'ADMIN']}>
                    <Suspense fallback={<PageSkeleton />}>
                      <IngredientsAdminPage />
                    </Suspense>
                  </ProtectedRoute>
                }
              />

              {/* Placeholder routes for other features */}
              <Route path="catalog" element={<PlaceholderPage title="Catálogo" />} />
              <Route path="cart" element={<PlaceholderPage title="Carrito" />} />
              <Route path="orders" element={<PlaceholderPage title="Mis Pedidos" />} />
              <Route path="profile" element={<PlaceholderPage title="Mi Perfil" />} />
              <Route path="products" element={<PlaceholderPage title="Productos" />} />
              <Route path="categories" element={<PlaceholderPage title="Categorías" />} />
              <Route path="stock" element={<PlaceholderPage title="Stock" />} />
              <Route path="orders-panel" element={<PlaceholderPage title="Panel de Pedidos" />} />
              <Route path="users" element={<PlaceholderPage title="Usuarios" />} />
              <Route path="metrics" element={<PlaceholderPage title="Métricas" />} />
              <Route path="settings" element={<PlaceholderPage title="Configuración" />} />
            </Route>

            {/* Catch-all for unmatched routes */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Router>
      </QueryClientProvider>
    </div>
  );
};
