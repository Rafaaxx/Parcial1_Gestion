/**
 * ProductCatalog feature barrel export
 */
export { ProductCard, ProductList, PaginationControls, CatalogFilters, } from './components/index';
export { CatalogPage, ProductDetailPage, } from './pages/index';
export { useProducts, useProductDetail, useInvalidateProducts, } from './hooks/index';
export { useCatalogStore, } from './stores/index';
export { getProducts, getProductDetail, getAllergens, getCategories, } from './api/index';
export type { AllergenInfo, IngredientInfo, CategoryInfo, ProductCard as ProductCardType, ProductListItem, ProductDetail, ProductsResponse, CatalogFilters as CatalogFiltersType, ProductsQueryParams, } from './types/index';
//# sourceMappingURL=index.d.ts.map