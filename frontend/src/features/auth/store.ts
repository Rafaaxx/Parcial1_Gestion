/**
 * Auth store for managing user identity and authentication state
 */

import { create } from 'zustand';

export interface User {
  id: string;
  email: string;
  name: string;
  roles: Array<'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'>;
}

/**
 * Check if user has any of the required roles
 */
export function userHasRole(user: User | null, requiredRoles: string[]): boolean {
  if (!user) return false;
  return requiredRoles.some((role) => user.roles.includes(role as any));
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setTokens: (token: string, refreshToken: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,

  setUser: (user: User | null) => {
    set({
      user,
      isAuthenticated: user !== null,
    });
  },

  setTokens: (token: string, refreshToken: string) => {
    set({
      token,
      refreshToken,
      isAuthenticated: true,
    });
  },

  logout: () => {
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },
}));
