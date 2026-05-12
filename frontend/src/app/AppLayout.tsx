/**
 * AppLayout — Main layout shell with header, breadcrumbs, content, and footer
 */

import React, { useState, useEffect } from 'react'
import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import { useAuthStore } from '@/features/auth/store'
import { useTheme } from '@/shared/hooks/useTheme'
import { NavMenu } from '@/shared/ui/NavMenu'
import { Breadcrumbs } from '@/shared/ui/Breadcrumbs'
import { Footer } from '@/shared/ui/Footer'
import { UserDropdown } from '@/shared/ui/UserDropdown'
import { CartBadge } from '@/shared/ui/CartBadge'
import { CartDrawer } from '@/features/cart/components/CartDrawer'
import { useCartUIStore } from '@/features/cart/stores/cartUIStore'
import { ToastNotifierProvider } from '@/features/cart/components/ToastNotifier'
import { Skeleton } from '@/shared/ui/Skeleton'

export const AppLayout: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const rehydrated = useAuthStore((s) => s.rehydrated)
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const restoreSession = useAuthStore((s) => s.restoreSession)
  const { theme, toggleTheme, applyTheme } = useTheme()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const isCartDrawerOpen = useCartUIStore((s) => s.isDrawerOpen)
  const closeCartDrawer = useCartUIStore((s) => s.closeCart)

  // Apply theme on mount
  useEffect(() => {
    applyTheme(theme)
  }, [theme, applyTheme])

  // Restore user session after rehydration (if token exists but user is null)
  useEffect(() => {
    if (rehydrated && token && !user) {
      restoreSession()
    }
  }, [rehydrated, token, user, restoreSession])

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
                Food Store
              </span>
            </Link>

            {/* Desktop Navigation */}
            <NavMenu />

            {/* Right section */}
            <div className="flex items-center gap-2">
              <CartBadge />

              {isAuthenticated ? (
                <UserDropdown />
              ) : (
                <Link
                  to="/auth/login"
                  className="hidden md:inline-flex px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
                >
                  Iniciar Sesión
                </Link>
              )}

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Cambiar tema"
              >
                {theme === 'dark' ? (
                  <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>

              {/* Mobile hamburger */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Menú de navegación"
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? (
                  <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <>
            {/* Overlay */}
            <div
              className="fixed inset-0 bg-black/20 z-30 md:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            {/* Slide-in panel */}
            <div className="fixed top-16 right-0 bottom-0 w-72 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 shadow-xl z-40 md:hidden overflow-y-auto">
              {!isAuthenticated && (
                <div className="px-4 pt-4 pb-2 border-b border-gray-100 dark:border-gray-800">
                  <Link
                    to="/auth/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block w-full text-center px-4 py-2.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
                  >
                    Iniciar Sesión
                  </Link>
                  <Link
                    to="/auth/register"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block w-full text-center px-4 py-2.5 mt-2 text-sm font-medium text-primary-600 dark:text-primary-400 border border-primary-600 dark:border-primary-400 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                  >
                    Registrarse
                  </Link>
                </div>
              )}
              <NavMenu isMobile onItemClick={() => setMobileMenuOpen(false)} />
            </div>
          </>
        )}
      </header>

      {/* Breadcrumbs */}
      <Breadcrumbs />

      {/* Main content */}
      <ToastNotifierProvider>
        <main className="flex-1 container mx-auto px-4 py-6">
          <React.Suspense
            fallback={
              <div className="space-y-4">
                <Skeleton height="2rem" width="60%" />
                <Skeleton height="1rem" count={3} />
                <Skeleton height="12rem" />
              </div>
            }
          >
            <Outlet />
          </React.Suspense>
        </main>
      </ToastNotifierProvider>

      {/* Cart Drawer */}
      <CartDrawer isOpen={isCartDrawerOpen} onClose={closeCartDrawer} />

      {/* Footer */}
      <Footer />
    </div>
  )
}

export default AppLayout
