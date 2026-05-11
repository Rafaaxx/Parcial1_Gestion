/**
 * API layer for ingredientes endpoints
 * Provides functions for communicating with backend API
 */
import type { IngredienteRead, IngredienteCreate, IngredienteUpdate, IngredienteListResponse } from './types';
/**
 * Fetch all active ingredients with optional pagination and filtering
 */
export declare function fetchIngredientes(skip?: number, limit?: number, esAlergeno?: boolean): Promise<IngredienteListResponse>;
/**
 * Fetch a single ingredient by ID
 */
export declare function fetchIngredienteById(id: number): Promise<IngredienteRead>;
/**
 * Create a new ingredient
 * Requires STOCK or ADMIN role
 */
export declare function createIngrediente(data: IngredienteCreate): Promise<IngredienteRead>;
/**
 * Update an existing ingredient
 * Requires STOCK or ADMIN role
 */
export declare function updateIngrediente(id: number, data: IngredienteUpdate): Promise<IngredienteRead>;
/**
 * Delete (soft delete) an ingredient
 * Requires STOCK or ADMIN role
 */
export declare function deleteIngrediente(id: number): Promise<void>;
//# sourceMappingURL=api.d.ts.map