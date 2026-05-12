/**
 * Cart store for managing shopping cart state
 *
 * State: client-side only (Zustand + persist middleware → localStorage)
 * Persists only the `items` array (selectors are computed, not stored).
 */
import type { CartItem, CartState } from './types';
export declare const useCartStore: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<CartState>, "persist"> & {
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<CartState, {
            items: CartItem[];
        }>>) => void;
        clearStorage: () => void;
        rehydrate: () => Promise<void> | void;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: CartState) => void) => () => void;
        onFinishHydration: (fn: (state: CartState) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<CartState, {
            items: CartItem[];
        }>>;
    };
}>;
//# sourceMappingURL=store.d.ts.map