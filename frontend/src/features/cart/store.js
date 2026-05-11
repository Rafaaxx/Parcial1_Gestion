/**
 * Cart store for managing shopping cart state
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
export const useCartStore = create()(persist((set, get) => ({
    items: [],
    addItem: (item) => {
        const { items } = get();
        const existingIndex = items.findIndex((i) => i.productoId === item.productoId);
        if (existingIndex >= 0) {
            const updated = [...items];
            updated[existingIndex] = {
                ...updated[existingIndex],
                cantidad: updated[existingIndex].cantidad + item.cantidad,
            };
            set({ items: updated });
        }
        else {
            set({ items: [...items, item] });
        }
    },
    removeItem: (productoId) => {
        const { items } = get();
        set({ items: items.filter((i) => i.productoId !== productoId) });
    },
    updateQuantity: (productoId, cantidad) => {
        const { items } = get();
        if (cantidad <= 0) {
            set({ items: items.filter((i) => i.productoId !== productoId) });
            return;
        }
        set({
            items: items.map((i) => i.productoId === productoId ? { ...i, cantidad } : i),
        });
    },
    clearCart: () => {
        set({ items: [] });
    },
    totalItems: () => {
        return get().items.reduce((sum, item) => sum + item.cantidad, 0);
    },
    subtotal: () => {
        return get().items.reduce((sum, item) => sum + item.producto.precio * item.cantidad, 0);
    },
    total: () => {
        return get().subtotal();
    },
}), {
    name: 'food-store-cart',
    partialize: (state) => ({
        items: state.items,
    }),
}));
//# sourceMappingURL=store.js.map