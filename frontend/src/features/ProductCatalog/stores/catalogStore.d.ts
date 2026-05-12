/**
 * Zustand store for catalog filters and UI state
 * Manages: searchText, selectedCategory, priceRange, allergenExclusions, pagination
 */
import { CatalogFilters, ProductsQueryParams } from '../types/catalog';
interface CatalogStore extends CatalogFilters {
    setSearch: (text: string) => void;
    setCategory: (id: number | null) => void;
    setPriceRange: (from: number | null, to: number | null) => void;
    setAllergenExclusions: (allergens: number[]) => void;
    setPage: (page: number) => void;
    setLimit: (limit: number) => void;
    resetFilters: () => void;
    getQueryParams: () => ProductsQueryParams;
    isFilterActive: () => boolean;
}
export declare const useCatalogStore: import("zustand").UseBoundStore<import("zustand").StoreApi<CatalogStore>>;
export {};
//# sourceMappingURL=catalogStore.d.ts.map