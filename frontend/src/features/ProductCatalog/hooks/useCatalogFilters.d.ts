/**
 * Custom hook for TanStack Query integration with catalog filters
 * Manages server state, caching, and refetching based on filters
 */
import { ProductListItem, ProductDetail } from '../types/catalog';
interface UseCatalogProductsResult {
    products: ProductListItem[];
    total: number;
    isLoading: boolean;
    error: Error | null;
    refetch: () => Promise<any>;
}
/**
 * Hook to fetch and manage catalog products
 * Uses TanStack Query with filter-aware cache invalidation
 */
export declare function useProducts(): UseCatalogProductsResult;
/**
 * Hook to invalidate products query after mutations
 * Call this when products are updated elsewhere (admin panel, etc.)
 */
export declare function useInvalidateProducts(): {
    invalidateAll: () => void;
    invalidateDetail: (id: number) => void;
};
/**
 * Hook to fetch product detail with caching
 */
export declare function useProductDetail(id: number): {
    product: ProductDetail | null;
    isLoading: boolean;
    error: Error | null;
    refetch: (options?: import("@tanstack/react-query").RefetchOptions) => Promise<import("@tanstack/react-query").QueryObserverResult<ProductDetail, Error>>;
};
export {};
//# sourceMappingURL=useCatalogFilters.d.ts.map