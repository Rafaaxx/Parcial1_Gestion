/**
 * Auth store for managing user identity and authentication state
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '@/shared/http/client'

export type Role = 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'

export interface User {
  id: string
  email: string
  name: string
  roles: Role[]
}

interface MeResponse {
  id: number
  nombre: string
  apellido: string
  email: string
  roles: string[]
  activo: boolean
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  rehydrated: boolean
  setUser: (user: User | null) => void
  setTokens: (token: string, refreshToken: string) => void
  logout: () => void
  hasRole: (role: Role) => boolean
  setRehydrated: () => void
  restoreSession: () => Promise<void>
}

/**
 * Check if user has any of the required roles (standalone utility for legacy components)
 */
export function userHasRole(user: User | null, requiredRoles: string[]): boolean {
  if (!user) return false;
  return requiredRoles.some((role) => user.roles.includes(role as Role));
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      rehydrated: false,

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: user !== null,
        })
      },

      setTokens: (token: string, refreshToken: string) => {
        set({
          token,
          refreshToken,
          isAuthenticated: true,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      hasRole: (role: Role): boolean => {
        const { user } = get()
        if (!user) return false
        return user.roles.includes(role)
      },

      setRehydrated: () => {
        const { token } = get()
        set({
          rehydrated: true,
          isAuthenticated: token !== null && token !== undefined,
        })
      },

      restoreSession: async () => {
        const { token } = get()
        if (!token) return

        try {
          const meResp = await apiClient.get<MeResponse>('/auth/me')
          const userData = meResp.data
          set({
            user: {
              id: String(userData.id),
              email: userData.email,
              name: `${userData.nombre} ${userData.apellido}`,
              roles: userData.roles as Role[],
            },
          })
        } catch {
          // /auth/me failed (network, expired token, etc.) — DON'T call logout()
          // The user keeps their tokens, subsequent API calls will still work.
          // restoreSession will retry on next page navigation via SessionRestorer.
        }
      },
    }),
    {
      name: 'food-store-auth',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setRehydrated()
          // restoreSession() moved to React useEffect (SessionRestorer)
          // to avoid race conditions with async HTTP client initialization
        }
      },
    }
  )
)
