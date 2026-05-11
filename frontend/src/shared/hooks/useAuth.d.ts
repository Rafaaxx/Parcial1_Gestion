/**
 * useAuth hook for accessing auth store
 */
import { type Role } from '@/features/auth/store';
export declare function useAuth(): {
    user: import("@/features/auth/store").User | null;
    token: string | null;
    isAuthenticated: boolean;
    rehydrated: boolean;
    logout: () => void;
    setTokens: (token: string, refreshToken: string) => void;
    setUser: (user: import("@/features/auth/store").User | null) => void;
    hasRole: (role: Role) => boolean;
};
export type { Role };
//# sourceMappingURL=useAuth.d.ts.map