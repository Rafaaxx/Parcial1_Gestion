/**
 * ProductDetailPage — Single product details
 * Integrates the ProductDetailPage component from ProductCatalog feature
 */

import React from 'react'
import { ProductDetailPage as ProductDetailView } from '@/features/ProductCatalog/pages/ProductDetailPage'

export const ProductDetailPage: React.FC = () => {
  return <ProductDetailView />
}

export default ProductDetailPage
