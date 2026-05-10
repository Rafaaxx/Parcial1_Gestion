/**
 * useCategories hook for fetching product categories
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/shared/http/client'

export interface Category {
  id: string
  nombre: string
  subcategorias?: Category[]
}

interface CategoriesResponse {
  data: Category[]
}

export function useCategories() {
  const { data, isLoading, error } = useQuery<CategoriesResponse>({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await apiClient.get<CategoriesResponse>('/categorias')
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 min
  })

  return {
    data: data?.data ?? [],
    isLoading,
    error,
  }
}
