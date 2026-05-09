/**
 * UI store for managing global UI state: theme, toasts, modals
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
export const useUIStore = create()(persist((set) => ({
    theme: 'light',
    toast: null,
    sidebarOpen: true,
    toggleTheme: () => {
        set((state) => ({
            theme: state.theme === 'light' ? 'dark' : 'light',
        }));
    },
    showToast: (toast) => {
        set({ toast });
        if (toast.duration || toast.duration === undefined) {
            setTimeout(() => {
                set({ toast: null });
            }, toast.duration || 3000);
        }
    },
    dismissToast: () => {
        set({ toast: null });
    },
    setSidebarOpen: (open) => {
        set({ sidebarOpen: open });
    },
}), {
    name: 'food-store-ui',
    partialize: (state) => ({
        theme: state.theme,
    }),
}));
//# sourceMappingURL=store.js.map