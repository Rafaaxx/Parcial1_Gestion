/**
 * Ingrediente entity types and interfaces
 * Aligned with backend API responses from CHANGE-04
 */

export interface IngredienteRead {
  id: number;
  nombre: string;
  es_alergeno: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  deleted_at: string | null; // Soft delete field (null if active)
}

export interface IngredienteCreate {
  nombre: string;
  es_alergeno?: boolean;
}

export interface IngredienteUpdate {
  nombre?: string;
  es_alergeno?: boolean;
}

export interface IngredienteListResponse {
  items: IngredienteRead[];
  total: number;
  skip: number;
  limit: number;
}
