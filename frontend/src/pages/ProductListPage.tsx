/**
 * ProductListPage — Catalog of products
 * Integrates the CatalogPage component from ProductCatalog feature
 */

import React from 'react'
import { CatalogPage } from '@/features/ProductCatalog/pages/CatalogPage'

export const ProductListPage: React.FC = () => {
  return <CatalogPage />
}

export default ProductListPage
