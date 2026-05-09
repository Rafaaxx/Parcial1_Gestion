/**
 * Auth store for managing user identity and authentication state
 */
export interface User {
    id: string;
    email: string;
    name: string;
    role: 'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT';
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
export declare const useAuthStore: import("zustand").UseBoundStore<import("zustand").StoreApi<AuthState>>;
//# sourceMappingURL=store.d.ts.map