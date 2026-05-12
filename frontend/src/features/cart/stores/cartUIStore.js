/**
 * Cart UI store — lightweight Zustand store for drawer open/close state
 *
 * This is separated from the cartStore because the drawer state is transient UI state,
 * not persisted cart data. Using a dedicated store lets CartBadge and AppLayout
 * share the same state without prop drilling.
 */
import { create } from 'zustand';
export const useCartUIStore = create()((set) => ({
    isDrawerOpen: false,
    openCart: () => set({ isDrawerOpen: true }),
    closeCart: () => set({ isDrawerOpen: false }),
    toggleCart: () => set((state) => ({ isDrawerOpen: !state.isDrawerOpen })),
}));
//# sourceMappingURL=cartUIStore.js.map