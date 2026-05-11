/**
 * AdminLayout: Layout component for admin pages with sidebar navigation
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore, userHasRole } from '@/features/auth/store';

interface AdminLayoutProps {
  children: React.ReactNode;
}

interface NavItem {
  label: string;
  href: string;
  requiredRoles: string[];
  icon?: string;
}

const NAV_ITEMS: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/admin',
    requiredRoles: ['ADMIN', 'STOCK', 'PEDIDOS'],
    icon: '📊',
  },
  {
    label: 'Ingredientes',
    href: '/admin/ingredientes',
    requiredRoles: ['STOCK', 'ADMIN'],
    icon: '🥬',
  },
  {
    label: 'Categorías',
    href: '/admin/categorias',
    requiredRoles: ['STOCK', 'ADMIN'],
    icon: '🏷️',
  },
  {
    label: 'Productos',
    href: '/admin/productos',
    requiredRoles: ['STOCK', 'ADMIN'],
    icon: '📦',
  },
  {
    label: 'Usuarios',
    href: '/admin/usuarios',
    requiredRoles: ['ADMIN'],
    icon: '👥',
  },
];

export const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const { user } = useAuthStore();
  const location = useLocation();

  // Filter nav items based on user roles
  const visibleNavItems = NAV_ITEMS.filter((item) => userHasRole(user, item.requiredRoles));

  const isActive = (href: string) => location.pathname === href;

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-gray-200 dark:border-gray-800">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Food Store</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Admin Panel</p>
          </div>

          {/* User Info */}
          {user && (
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
              <div className="mt-2 flex gap-1 flex-wrap">
                {user.roles.map((role) => (
                  <span
                    key={role}
                    className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
                  >
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {visibleNavItems.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                  isActive(item.href)
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 font-medium'
                    : 'text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                {item.icon && <span className="text-lg">{item.icon}</span>}
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-800">
            <button
              onClick={() => {
                // Logout logic here
                window.location.href = '/login';
              }}
              className="w-full px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="bg-white dark:bg-gray-900 min-h-full">{children}</div>
      </main>
    </div>
  );
};
