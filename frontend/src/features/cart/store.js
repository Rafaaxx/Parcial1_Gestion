/**
 * Cart store for managing shopping cart state
 *
 * State: client-side only (Zustand + persist middleware → localStorage)
 * Persists only the `items` array (selectors are computed, not stored).
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { COSTO_ENVIO_FLAT, CART_STORAGE_KEY, CART_MAX_ITEMS } from './types';
function buildItemKey(productoId, personalizacion) {
    const sorted = [...personalizacion].sort();
    return `${productoId}_${JSON.stringify(sorted)}`;
}
export const useCartStore = create()(persist((set, get) => ({
    items: [],
    addItem: (producto, cantidad = 1, personalizacion = []) => {
        if (cantidad <= 0)
            return;
        const { items } = get();
        const productoId = producto.id;
        const newKey = buildItemKey(productoId, personalizacion);
        const existingIndex = items.findIndex((item) => buildItemKey(item.productoId, item.personalizacion) === newKey);
        if (existingIndex >= 0) {
            // Same product + same personalization → increment quantity
            const updated = [...items];
            const current = updated[existingIndex];
            const newCantidad = Math.min(current.cantidad + cantidad, CART_MAX_ITEMS);
            updated[existingIndex] = { ...current, cantidad: newCantidad };
            set({ items: updated });
        }
        else {
            // New entry
            const precio = typeof producto.precio_base === 'string'
                ? parseFloat(producto.precio_base)
                : producto.precio_base;
            const newItem = {
                productoId,
                nombre: producto.nombre,
                precio,
                imagenUrl: producto.imagen ?? '',
                cantidad: Math.min(cantidad, CART_MAX_ITEMS),
                personalizacion,
                ingredientes: producto.ingredientes ?? [],
            };
            set({ items: [...items, newItem] });
        }
    },
    removeItem: (productoId, personalizacion) => {
        const { items } = get();
        if (personalizacion !== undefined) {
            const key = buildItemKey(productoId, personalizacion);
            set({ items: items.filter((i) => buildItemKey(i.productoId, i.personalizacion) !== key) });
        }
        else {
            set({ items: items.filter((i) => i.productoId !== productoId) });
        }
    },
    updateQuantity: (productoId, cantidad, personalizacion) => {
        const { items } = get();
        if (cantidad <= 0) {
            // Remove the item
            if (personalizacion !== undefined) {
                const key = buildItemKey(productoId, personalizacion);
                set({ items: items.filter((i) => buildItemKey(i.productoId, i.personalizacion) !== key) });
            }
            else {
                set({ items: items.filter((i) => i.productoId !== productoId) });
            }
            return;
        }
        const clamped = Math.min(cantidad, CART_MAX_ITEMS);
        if (personalizacion !== undefined) {
            const key = buildItemKey(productoId, personalizacion);
            set({
                items: items.map((i) => buildItemKey(i.productoId, i.personalizacion) === key ? { ...i, cantidad: clamped } : i),
            });
        }
        else {
            set({
                items: items.map((i) => i.productoId === productoId ? { ...i, cantidad: clamped } : i),
            });
        }
    },
    clearCart: () => {
        set({ items: [] });
    },
    totalItems: () => {
        return get().items.reduce((sum, item) => sum + item.cantidad, 0);
    },
    subtotal: () => {
        return get().items.reduce((sum, item) => sum + item.precio * item.cantidad, 0);
    },
    costoEnvio: () => {
        return get().items.length > 0 ? COSTO_ENVIO_FLAT : 0;
    },
    total: () => {
        const state = get();
        return state.subtotal() + state.costoEnvio();
    },
}), {
    name: CART_STORAGE_KEY,
    partialize: (state) => ({
        items: state.items,
    }),
}));
//# sourceMappingURL=store.js.map