/**
 * useAuth hook for accessing auth store
 */

import { useAuthStore, type Role } from '@/features/auth/store'

export function useAuth() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const rehydrated = useAuthStore((state) => state.rehydrated)
  const logout = useAuthStore((state) => state.logout)
  const setTokens = useAuthStore((state) => state.setTokens)
  const setUser = useAuthStore((state) => state.setUser)
  const hasRole = useAuthStore((state) => state.hasRole)

  return {
    user,
    token,
    isAuthenticated,
    rehydrated,
    logout,
    setTokens,
    setUser,
    hasRole,
  }
}

export type { Role }
