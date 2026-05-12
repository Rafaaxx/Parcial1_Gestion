/**
 * Cart UI store — lightweight Zustand store for drawer open/close state
 *
 * This is separated from the cartStore because the drawer state is transient UI state,
 * not persisted cart data. Using a dedicated store lets CartBadge and AppLayout
 * share the same state without prop drilling.
 */
interface CartUIState {
    isDrawerOpen: boolean;
    openCart: () => void;
    closeCart: () => void;
    toggleCart: () => void;
}
export declare const useCartUIStore: import("zustand").UseBoundStore<import("zustand").StoreApi<CartUIState>>;
export {};
//# sourceMappingURL=cartUIStore.d.ts.map