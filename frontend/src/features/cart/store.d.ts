/**
 * Cart store for managing shopping cart state
 */
export interface CartItem {
    productoId: string;
    producto: {
        id: string;
        nombre: string;
        precio: number;
        imagen?: string;
    };
    cantidad: number;
    personalizacion?: {
        ingredienteId: string;
        removido: boolean;
    }[];
}
export interface CartState {
    items: CartItem[];
    addItem: (item: CartItem) => void;
    removeItem: (productoId: string) => void;
    updateQuantity: (productoId: string, cantidad: number) => void;
    clearCart: () => void;
    totalItems: () => number;
    subtotal: () => number;
    total: () => number;
}
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