/**
 * UI store for managing global UI state: theme, toasts, modals
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

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

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'light',
      toast: null,
      sidebarOpen: true,

      toggleTheme: () => {
        set((state: UIState) => ({
          theme: state.theme === 'light' ? 'dark' : 'light',
        }));
      },

      showToast: (toast: Toast) => {
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

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },
    }),
    {
      name: 'food-store-ui',
      partialize: (state: UIState) => ({
        theme: state.theme,
      }),
    }
  )
);
