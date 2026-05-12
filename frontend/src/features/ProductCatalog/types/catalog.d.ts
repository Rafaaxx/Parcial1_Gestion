/**
 * TypeScript types for the Product Catalog feature
 */
/** Allergen information for ingredients */
export interface AllergenInfo {
    id: number;
    nombre: string;
    es_alergeno: boolean;
}
/** Ingredient information with allergen and removable flags */
export interface IngredientInfo {
    id: number;
    nombre: string;
    es_alergeno: boolean;
    es_removible?: boolean;
}
/** Category information */
export interface CategoryInfo {
    id: number;
    nombre: string;
    descripcion?: string;
}
/** Product card display format (for listing) */
export interface ProductCard {
    id: number;
    nombre: string;
    descripcion?: string;
    precio_base: number | string;
    imagen: string | null;
    disponible: boolean;
    categorias: CategoryInfo[];
    ingredientes?: IngredientInfo[];
}
/** Product list item returned from API */
export interface ProductListItem {
    id: number;
    nombre: string;
    descripcion?: string;
    precio_base: number | string;
    imagen: string | null;
    disponible: boolean;
    categorias: CategoryInfo[];
    ingredientes?: IngredientInfo[];
}
/** Product detail with full information */
export interface ProductDetail {
    id: number;
    nombre: string;
    descripcion?: string;
    precio_base: number | string;
    imagen: string | null;
    disponible: boolean;
    categorias: CategoryInfo[];
    ingredientes: IngredientInfo[];
}
/** API response for product listing */
export interface ProductsResponse {
    items: ProductListItem[];
    total: number;
    skip: number;
    limit: number;
}
/** Catalog filter state */
export interface CatalogFilters {
    searchText: string;
    selectedCategory: number | null;
    priceFrom: number | null;
    priceTo: number | null;
    excludedAllergens: number[];
    currentPage: number;
    limit: number;
}
/** Query parameters for the API */
export interface ProductsQueryParams {
    skip: number;
    limit: number;
    busqueda?: string;
    categoria?: number;
    precio_desde?: number;
    precio_hasta?: number;
    excluirAlergenos?: string;
}
//# sourceMappingURL=catalog.d.ts.map