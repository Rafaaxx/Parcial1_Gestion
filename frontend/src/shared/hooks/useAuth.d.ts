/**
 * useAuth hook for accessing auth store
 */
export declare function useAuth(): {
  user: import('@/features/auth/store').User | null;
  token: string | null;
  isAuthenticated: boolean;
  logout: () => void;
  setTokens: (token: string, refreshToken: string) => void;
  setUser: (user: import('@/features/auth/store').User | null) => void;
};
//# sourceMappingURL=useAuth.d.ts.map
