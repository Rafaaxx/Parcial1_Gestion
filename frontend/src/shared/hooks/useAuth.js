/**
 * useAuth hook for accessing auth store
 */
import { useAuthStore } from '@/features/auth/store';
export function useAuth() {
    const user = useAuthStore((state) => state.user);
    const token = useAuthStore((state) => state.token);
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    const logout = useAuthStore((state) => state.logout);
    const setTokens = useAuthStore((state) => state.setTokens);
    const setUser = useAuthStore((state) => state.setUser);
    return {
        user,
        token,
        isAuthenticated,
        logout,
        setTokens,
        setUser,
    };
}
//# sourceMappingURL=useAuth.js.map