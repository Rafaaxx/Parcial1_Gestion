/**
 * UI store for managing global UI state: theme, toasts, modals
 */
export interface Toast {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    duration?: number;
}
export interface UIState {
    theme: 'light' | 'dark';
    toast: Toast | null;
    sidebarOpen: boolean;
    toggleTheme: () => void;
    showToast: (toast: Toast) => void;
    dismissToast: () => void;
    setSidebarOpen: (open: boolean) => void;
}
export declare const useUIStore: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<UIState>, "persist"> & {
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<UIState, {
            theme: "light" | "dark";
        }>>) => void;
        clearStorage: () => void;
        rehydrate: () => Promise<void> | void;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: UIState) => void) => () => void;
        onFinishHydration: (fn: (state: UIState) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<UIState, {
            theme: "light" | "dark";
        }>>;
    };
}>;
//# sourceMappingURL=store.d.ts.map