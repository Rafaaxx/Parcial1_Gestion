/**
 * Development helper to mock authentication without login
 * Use this in the browser console during development:
 * 
 * import { mockAuthAsStockUser } from '@/shared/dev/mockAuth'
 * mockAuthAsStockUser()
 * 
 * Then navigate to /admin/ingredientes
 */

import { useAuthStore, type User } from '@/features/auth/store'

/**
 * Mock authentication as a STOCK user for testing inventory management
 */
export function mockAuthAsStockUser() {
  const mockUser: User = {
    id: 'dev-stock-001',
    email: 'stock@foodstore.dev',
    name: 'Stock Manager',
    roles: ['STOCK'],
  }

  useAuthStore.getState().setUser(mockUser)
  useAuthStore.getState().setTokens(
    'dev-token-stock-' + Date.now(),
    'dev-refresh-token-stock-' + Date.now()
  )

  console.log('✅ Mocked auth as STOCK user:', mockUser)
}

/**
 * Mock authentication as an ADMIN user for testing all features
 */
export function mockAuthAsAdminUser() {
  const mockUser: User = {
    id: 'dev-admin-001',
    email: 'admin@foodstore.dev',
    name: 'Admin',
    roles: ['ADMIN', 'STOCK', 'PEDIDOS'],
  }

  useAuthStore.getState().setUser(mockUser)
  useAuthStore.getState().setTokens(
    'dev-token-admin-' + Date.now(),
    'dev-refresh-token-admin-' + Date.now()
  )

  console.log('✅ Mocked auth as ADMIN user:', mockUser)
}

/**
 * Mock authentication as a CLIENT (no privileged access)
 */
export function mockAuthAsClientUser() {
  const mockUser: User = {
    id: 'dev-client-001',
    email: 'client@foodstore.dev',
    name: 'Regular Client',
    roles: ['CLIENT'],
  }

  useAuthStore.getState().setUser(mockUser)
  useAuthStore.getState().setTokens(
    'dev-token-client-' + Date.now(),
    'dev-refresh-token-client-' + Date.now()
  )

  console.log('✅ Mocked auth as CLIENT user:', mockUser)
}

/**
 * Clear auth state (logout)
 */
export function clearMockAuth() {
  useAuthStore.getState().logout()
  console.log('✅ Cleared auth state')
}
