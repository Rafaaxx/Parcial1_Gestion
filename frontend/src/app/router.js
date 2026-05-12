import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Application router configuration with lazy-loaded routes
 */
import { createBrowserRouter } from 'react-router-dom';
import { lazy } from 'react';
import { AppLayout } from './AppLayout';
import { ProtectedRoute } from '@/shared/ui/ProtectedRoute';
// Lazy-loaded pages
const HomePage = lazy(() => import('@/pages/HomePage'));
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));
const ForbiddenPage = lazy(() => import('@/pages/ForbiddenPage'));
const ProductListPage = lazy(() => import('@/pages/ProductListPage'));
const ProductDetailPage = lazy(() => import('@/pages/ProductDetailPage'));
const CategoryPage = lazy(() => import('@/pages/CategoryPage'));
const CartPage = lazy(() => import('@/pages/CartPage'));
const ProfilePage = lazy(() => import('@/pages/ProfilePage'));
const AdminDashboard = lazy(() => import('@/pages/AdminDashboard'));
const AdminProducts = lazy(() => import('@/pages/AdminProducts'));
const AdminCategories = lazy(() => import('@/pages/AdminCategories'));
const AdminOrders = lazy(() => import('@/pages/AdminOrders'));
const AdminUsers = lazy(() => import('@/pages/AdminUsers'));
const AdminStock = lazy(() => import('@/pages/AdminStock'));
const AdminIngredients = lazy(() => import('@/pages/admin/IngredientsPage'));
export const router = createBrowserRouter([
    {
        path: '/',
        element: _jsx(AppLayout, {}),
        children: [
            { index: true, element: _jsx(HomePage, {}) },
            { path: 'auth/login', element: _jsx(LoginPage, {}) },
            { path: 'auth/register', element: _jsx(RegisterPage, {}) },
            { path: 'productos', element: _jsx(ProductListPage, {}) },
            { path: 'productos/:id', element: _jsx(ProductDetailPage, {}) },
            { path: 'categorias/:id', element: _jsx(CategoryPage, {}) },
            // Protected routes (any authenticated user)
            {
                element: _jsx(ProtectedRoute, {}),
                children: [
                    { path: 'carrito', element: _jsx(CartPage, {}) },
                    { path: 'perfil', element: _jsx(ProfilePage, {}) },
                    // Admin routes
                    {
                        element: _jsx(ProtectedRoute, { requiredRoles: ['ADMIN'] }),
                        children: [
                            { path: 'admin', element: _jsx(AdminDashboard, {}) },
                            { path: 'admin/productos', element: _jsx(AdminProducts, {}) },
                            { path: 'admin/ingredientes', element: _jsx(AdminIngredients, {}) },
                            { path: 'admin/categorias', element: _jsx(AdminCategories, {}) },
                            { path: 'admin/pedidos', element: _jsx(AdminOrders, {}) },
                            { path: 'admin/usuarios', element: _jsx(AdminUsers, {}) },
                            { path: 'admin/stock', element: _jsx(AdminStock, {}) },
                        ],
                    },
                ],
            },
            { path: '403', element: _jsx(ForbiddenPage, {}) },
            { path: '*', element: _jsx(NotFoundPage, {}) },
        ],
    },
]);
export default router;
//# sourceMappingURL=router.js.map