/**
 * TanStack Query hooks for ingredient queries and mutations
 * Manages server state, caching, and automatic refetching
 */

import { useQuery, useMutation, useQueryClient, QueryKey } from '@tanstack/react-query';
import type {
  IngredienteRead,
  IngredienteCreate,
  IngredienteUpdate,
  IngredienteListResponse,
} from './types';
import {
  fetchIngredientes,
  fetchIngredienteById,
  createIngrediente,
  updateIngrediente,
  deleteIngrediente,
} from './api';

// Query key factory for better cache management
const ingredientesQueryKeys = {
  all: ['ingredientes'] as const,
  lists: () => [...ingredientesQueryKeys.all, 'list'] as const,
  list: (skip: number, limit: number, esAlergeno?: boolean) =>
    [...ingredientesQueryKeys.lists(), { skip, limit, esAlergeno }] as const,
  details: () => [...ingredientesQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...ingredientesQueryKeys.details(), id] as const,
};

/**
 * Query hook: Fetch paginated list of ingredients
 */
export function useIngredientes(skip: number = 0, limit: number = 100, esAlergeno?: boolean) {
  return useQuery<IngredienteListResponse>({
    queryKey: ingredientesQueryKeys.list(skip, limit, esAlergeno),
    queryFn: () => fetchIngredientes(skip, limit, esAlergeno),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
}

/**
 * Query hook: Fetch a single ingredient by ID
 */
export function useIngredienteDetail(id: number) {
  return useQuery<IngredienteRead>({
    queryKey: ingredientesQueryKeys.detail(id),
    queryFn: () => fetchIngredienteById(id),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Mutation hook: Create a new ingredient
 */
export function useCreateIngrediente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: IngredienteCreate) => createIngrediente(data),
    onSuccess: () => {
      // Invalidate list queries to force refetch
      queryClient.invalidateQueries({
        queryKey: ingredientesQueryKeys.lists(),
      });
    },
  });
}

/**
 * Mutation hook: Update an ingredient
 */
export function useUpdateIngrediente(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: IngredienteUpdate) => updateIngrediente(id, data),
    onSuccess: (updatedIngrediente) => {
      // Update the specific ingredient in cache
      queryClient.setQueryData(ingredientesQueryKeys.detail(id), updatedIngrediente);
      // Also invalidate list queries to show updates
      queryClient.invalidateQueries({
        queryKey: ingredientesQueryKeys.lists(),
      });
    },
  });
}

/**
 * Mutation hook: Delete (soft delete) an ingredient
 */
export function useDeleteIngrediente(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => deleteIngrediente(id),
    onSuccess: () => {
      // Remove from cache
      queryClient.removeQueries({
        queryKey: ingredientesQueryKeys.detail(id),
      });
      // Invalidate lists to force refetch
      queryClient.invalidateQueries({
        queryKey: ingredientesQueryKeys.lists(),
      });
    },
  });
}
