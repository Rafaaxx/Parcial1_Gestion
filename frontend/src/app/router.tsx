/**
 * Application router configuration with lazy-loaded routes
 *
 * TODAS las rutas usan AppLayout. El sidebar se muestra condicionalmente
 * en AppLayout cuando el usuario tiene roles ADMIN/STOCK/PEDIDOS.
 * El AdminLayout se eliminó — el sidebar ahora vive en AppLayout.
 */

import { createBrowserRouter } from 'react-router-dom'
import { lazy } from 'react'
import { AppLayout } from './AppLayout'
import { ProtectedRoute } from '@/shared/ui/ProtectedRoute'

// Lazy-loaded pages
const HomePage = lazy(() => import('@/pages/HomePage'))
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/RegisterPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))
const ForbiddenPage = lazy(() => import('@/pages/ForbiddenPage'))
const ProductListPage = lazy(() => import('@/pages/ProductListPage'))
const ProductDetailPage = lazy(() => import('@/pages/ProductDetailPage'))
const CategoryPage = lazy(() => import('@/pages/CategoryPage'))
const CartPage = lazy(() => import('@/pages/CartPage'))
const ProfilePage = lazy(() => import('@/pages/ProfilePage'))
const AdminDashboard = lazy(() => import('@/pages/AdminDashboard'))
const AdminProducts = lazy(() => import('@/pages/AdminProducts'))
const AdminCategories = lazy(() => import('@/pages/AdminCategories'))
const AdminOrders = lazy(() => import('@/pages/AdminOrders'))
const AdminUsers = lazy(() => import('@/pages/AdminUsers'))
const AdminStock = lazy(() => import('@/pages/AdminStock'))
const AdminIngredients = lazy(() => import('@/pages/admin/IngredientsPage'))

export const router = createBrowserRouter([
  // ── Un único árbol de rutas — AppLayout maneja sidebar condicional ──
  {
    path: '/',
    element: <AppLayout />,
    children: [
      // Públicas
      { index: true, element: <HomePage /> },
      { path: 'auth/login', element: <LoginPage /> },
      { path: 'auth/register', element: <RegisterPage /> },
      { path: 'productos', element: <ProductListPage /> },
      { path: 'productos/:id', element: <ProductDetailPage /> },
      { path: 'categorias/:id', element: <CategoryPage /> },

      // Protegidas de cliente
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'carrito', element: <CartPage /> },
          { path: 'perfil', element: <ProfilePage /> },
        ],
      },

      // Admin (protegidas por rol)
      {
        element: <ProtectedRoute requiredRoles={['ADMIN', 'STOCK', 'PEDIDOS']} />,
        children: [
          { path: 'admin',              element: <AdminDashboard /> },
          { path: 'admin/productos',    element: <AdminProducts /> },
          { path: 'admin/ingredientes', element: <AdminIngredients /> },
          { path: 'admin/categorias',   element: <AdminCategories /> },
          { path: 'admin/pedidos',      element: <AdminOrders /> },
          { path: 'admin/usuarios',     element: <AdminUsers /> },
          { path: 'admin/stock',        element: <AdminStock /> },
        ],
      },

      { path: '403', element: <ForbiddenPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])

export default router
