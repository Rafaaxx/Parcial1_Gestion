/**
 * Zustand store for catalog filters and UI state
 * Manages: searchText, selectedCategory, priceRange, allergenExclusions, pagination
 */
import { create } from 'zustand';
const defaultFilters = {
    searchText: '',
    selectedCategory: null,
    priceFrom: null,
    priceTo: null,
    excludedAllergens: [],
    currentPage: 1,
    limit: 20,
};
export const useCatalogStore = create((set, get) => ({
    // Initial state
    ...defaultFilters,
    // Actions
    setSearch: (text) => set({ searchText: text, currentPage: 1 }),
    setCategory: (id) => set({ selectedCategory: id, currentPage: 1 }),
    setPriceRange: (from, to) => set({ priceFrom: from, priceTo: to, currentPage: 1 }),
    setAllergenExclusions: (allergens) => set({ excludedAllergens: allergens, currentPage: 1 }),
    setPage: (page) => set({ currentPage: Math.max(1, page) }),
    setLimit: (limit) => set({ limit: Math.max(1, limit), currentPage: 1 }),
    resetFilters: () => set(defaultFilters),
    // Selectors
    getQueryParams: () => {
        const state = get();
        const skip = (state.currentPage - 1) * state.limit;
        const params = {
            skip,
            limit: state.limit,
        };
        if (state.searchText.trim()) {
            params.busqueda = state.searchText.trim();
        }
        if (state.selectedCategory) {
            params.categoria = state.selectedCategory;
        }
        if (state.priceFrom !== null) {
            params.precio_desde = state.priceFrom;
        }
        if (state.priceTo !== null) {
            params.precio_hasta = state.priceTo;
        }
        if (state.excludedAllergens.length > 0) {
            params.excluirAlergenos = state.excludedAllergens.join(',');
        }
        return params;
    },
    isFilterActive: () => {
        const state = get();
        return (state.searchText.trim() !== '' ||
            state.selectedCategory !== null ||
            state.priceFrom !== null ||
            state.priceTo !== null ||
            state.excludedAllergens.length > 0);
    },
}));
//# sourceMappingURL=catalogStore.js.map