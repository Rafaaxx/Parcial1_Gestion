/**
 * useCategories hook for fetching product categories
 */
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/shared/http/client';
export function useCategories() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['categories'],
        queryFn: async () => {
            const response = await apiClient.get('/categorias');
            return response.data;
        },
        staleTime: 10 * 60 * 1000, // 10 min
    });
    return {
        data: data?.data ?? [],
        isLoading,
        error,
    };
}
//# sourceMappingURL=useCategories.js.map