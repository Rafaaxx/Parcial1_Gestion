/**
 * Auth store for managing user identity and authentication state
 */
import { create } from 'zustand';
/**
 * Check if user has any of the required roles
 */
export function userHasRole(user, requiredRoles) {
    if (!user)
        return false;
    return requiredRoles.some((role) => user.roles.includes(role));
}
export const useAuthStore = create((set) => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    setUser: (user) => {
        set({
            user,
            isAuthenticated: user !== null,
        });
    },
    setTokens: (token, refreshToken) => {
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
//# sourceMappingURL=store.js.map