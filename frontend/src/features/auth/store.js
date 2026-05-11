/**
 * Auth store for managing user identity and authentication state
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/shared/http/client';
export const useAuthStore = create()(persist((set, get) => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    rehydrated: false,
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
    hasRole: (role) => {
        const { user } = get();
        if (!user)
            return false;
        return user.roles.includes(role);
    },
    setRehydrated: () => {
        const { token } = get();
        set({
            rehydrated: true,
            isAuthenticated: token !== null && token !== undefined,
        });
    },
    restoreSession: async () => {
        const { token } = get();
        if (!token)
            return;
        try {
            const meResp = await apiClient.get('/auth/me');
            const userData = meResp.data;
            set({
                user: {
                    id: String(userData.id),
                    email: userData.email,
                    name: `${userData.nombre} ${userData.apellido}`,
                    roles: userData.roles,
                },
            });
        }
        catch {
            // /auth/me failed (network, expired token, etc.) — DON'T call logout()
            // The user keeps their tokens, subsequent API calls will still work.
            // restoreSession will retry on next page navigation via SessionRestorer.
        }
    },
}), {
    name: 'food-store-auth',
    partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
    }),
    onRehydrateStorage: () => (state) => {
        if (state) {
            state.setRehydrated();
            // restoreSession() moved to React useEffect (SessionRestorer)
            // to avoid race conditions with async HTTP client initialization
        }
    },
}));
//# sourceMappingURL=store.js.map