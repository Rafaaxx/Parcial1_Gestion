/**
 * Custom hook for TanStack Query integration with catalog filters
 * Manages server state, caching, and refetching based on filters
 */

import { useQuery, useQueryClient, UseQueryResult } from '@tanstack/react-query'
import { getProducts, getProductDetail } from '../api/catalogApi'
import { useCatalogStore } from '../stores/catalogStore'
import { ProductListItem, ProductsResponse, ProductDetail } from '../types/catalog'

interface UseCatalogProductsResult {
  products: ProductListItem[]
  total: number
  isLoading: boolean
  error: Error | null
  refetch: () => Promise<any>
}

/**
 * Hook to fetch and manage catalog products
 * Uses TanStack Query with filter-aware cache invalidation
 */
export function useProducts(): UseCatalogProductsResult {
  const queryClient = useQueryClient()
  const queryParams = useCatalogStore((state) => state.getQueryParams())

  // Create a stable query key that includes all filter params
  const queryKey = ['productos', queryParams]

  const query: UseQueryResult<ProductsResponse> = useQuery({
    queryKey,
    queryFn: () => getProducts(queryParams),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (was cacheTime in v4)
  })

  return {
    products: query.data?.items || [],
    total: query.data?.total || 0,
    isLoading: query.isLoading,
    error: query.error as Error | null,
    refetch: query.refetch,
  }
}

/**
 * Hook to invalidate products query after mutations
 * Call this when products are updated elsewhere (admin panel, etc.)
 */
export function useInvalidateProducts() {
  const queryClient = useQueryClient()

  return {
    invalidateAll: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] })
    },
    invalidateDetail: (id: number) => {
      queryClient.invalidateQueries({ queryKey: ['producto-detail', id] })
    },
  }
}

/**
 * Hook to fetch product detail with caching
 */
export function useProductDetail(id: number) {
  const query = useQuery({
    queryKey: ['producto-detail', id],
    queryFn: () => getProductDetail(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  })

  return {
    product: query.data || null,
    isLoading: query.isLoading,
    error: query.error as Error | null,
    refetch: query.refetch,
  }
}
