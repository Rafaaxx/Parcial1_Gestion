/**
 * API integration for Product Catalog
 * Handles all HTTP calls to the backend catalog endpoints
 */
import { ProductsResponse, ProductDetail, ProductsQueryParams } from '../types/catalog';
/**
 * Get list of products with filters and pagination
 * GET /api/v1/productos
 */
export declare function getProducts(filters: ProductsQueryParams): Promise<ProductsResponse>;
/**
 * Get product detail by ID
 * GET /api/v1/productos/{id}
 */
export declare function getProductDetail(id: number): Promise<ProductDetail>;
/**
 * Get list of allergens/ingredients
 * GET /api/v1/ingredientes?es_alergeno=true
 */
export declare function getAllergens(): Promise<any>;
/**
 * Get list of categories
 * GET /api/v1/categorias
 */
export declare function getCategories(): Promise<any>;
//# sourceMappingURL=catalogApi.d.ts.map