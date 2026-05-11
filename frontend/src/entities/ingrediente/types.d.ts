/**
 * Ingrediente entity types and interfaces
 * Aligned with backend API responses from CHANGE-04
 */
export interface IngredienteRead {
    id: number;
    nombre: string;
    es_alergeno: boolean;
    created_at: string;
    updated_at: string;
    deleted_at: string | null;
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
//# sourceMappingURL=types.d.ts.map