/**
 * Auth store for managing user identity and authentication state
 */
export type Role = 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT';
export interface User {
    id: string;
    email: string;
    name: string;
    roles: Role[];
}
export interface AuthState {
    user: User | null;
    token: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    rehydrated: boolean;
    setUser: (user: User | null) => void;
    setTokens: (token: string, refreshToken: string) => void;
    logout: () => void;
    hasRole: (role: Role) => boolean;
    setRehydrated: () => void;
    restoreSession: () => Promise<void>;
}
export declare const useAuthStore: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<AuthState>, "persist"> & {
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<AuthState, {
            token: string | null;
            refreshToken: string | null;
        }>>) => void;
        clearStorage: () => void;
        rehydrate: () => Promise<void> | void;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: AuthState) => void) => () => void;
        onFinishHydration: (fn: (state: AuthState) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<AuthState, {
            token: string | null;
            refreshToken: string | null;
        }>>;
    };
}>;
//# sourceMappingURL=store.d.ts.map