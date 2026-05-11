/**
 * TanStack Query hooks for ingredient queries and mutations
 * Manages server state, caching, and automatic refetching
 */
import type { IngredienteRead, IngredienteCreate, IngredienteUpdate, IngredienteListResponse } from './types';
/**
 * Query hook: Fetch paginated list of ingredients
 */
export declare function useIngredientes(skip?: number, limit?: number, esAlergeno?: boolean): import("@tanstack/react-query").UseQueryResult<IngredienteListResponse, Error>;
/**
 * Query hook: Fetch a single ingredient by ID
 */
export declare function useIngredienteDetail(id: number): import("@tanstack/react-query").UseQueryResult<IngredienteRead, Error>;
/**
 * Mutation hook: Create a new ingredient
 */
export declare function useCreateIngrediente(): import("@tanstack/react-query").UseMutationResult<IngredienteRead, Error, IngredienteCreate, unknown>;
/**
 * Mutation hook: Update an ingredient
 */
export declare function useUpdateIngrediente(id: number): import("@tanstack/react-query").UseMutationResult<IngredienteRead, Error, IngredienteUpdate, unknown>;
/**
 * Mutation hook: Delete (soft delete) an ingredient
 */
export declare function useDeleteIngrediente(id: number): import("@tanstack/react-query").UseMutationResult<void, Error, void, unknown>;
//# sourceMappingURL=hooks.d.ts.map