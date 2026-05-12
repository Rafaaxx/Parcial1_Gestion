/**
 * API integration for Product Catalog
 * Handles all HTTP calls to the backend catalog endpoints
 */

import axios from 'axios'
import { ProductsResponse, ProductDetail, ProductsQueryParams } from '../types/catalog'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_VERSION = '/api/v1'

/**
 * Get list of products with filters and pagination
 * GET /api/v1/productos
 */
export async function getProducts(filters: ProductsQueryParams): Promise<ProductsResponse> {
  try {
    const params = new URLSearchParams()

    params.append('skip', String(filters.skip))
    params.append('limit', String(filters.limit))

    if (filters.busqueda) {
      params.append('busqueda', filters.busqueda)
    }

    if (filters.categoria) {
      params.append('categoria', String(filters.categoria))
    }

    if (filters.precio_desde !== undefined && filters.precio_desde !== null) {
      params.append('precio_desde', String(filters.precio_desde))
    }

    if (filters.precio_hasta !== undefined && filters.precio_hasta !== null) {
      params.append('precio_hasta', String(filters.precio_hasta))
    }

    if (filters.excluirAlergenos) {
      params.append('excluirAlergenos', filters.excluirAlergenos)
    }

    const response = await axios.get<ProductsResponse>(
      `${API_BASE}${API_VERSION}/productos`,
      { params }
    )

    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const message = error.response?.data?.detail || error.message

      if (status === 400) {
        throw new Error(`Invalid filter parameters: ${message}`)
      }
      if (status === 500) {
        throw new Error('Server error while fetching products')
      }

      throw new Error(message || 'Failed to fetch products')
    }

    throw error
  }
}

/**
 * Get product detail by ID
 * GET /api/v1/productos/{id}
 */
export async function getProductDetail(id: number): Promise<ProductDetail> {
  try {
    const response = await axios.get<ProductDetail>(
      `${API_BASE}${API_VERSION}/productos/${id}`
    )

    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status

      if (status === 404) {
        throw new Error('Product not found or unavailable')
      }

      if (status === 500) {
        throw new Error('Server error while fetching product')
      }

      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch product')
    }

    throw error
  }
}

/**
 * Get list of allergens/ingredients
 * GET /api/v1/ingredientes?es_alergeno=true
 */
export async function getAllergens() {
  try {
    const response = await axios.get(`${API_BASE}${API_VERSION}/ingredientes`, {
      params: { es_alergeno: true },
    })

    return response.data.items || []
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch allergens')
    }

    throw error
  }
}

/**
 * Get list of categories
 * GET /api/v1/categorias
 */
export async function getCategories() {
  try {
    const response = await axios.get(`${API_BASE}${API_VERSION}/categorias`)

    return response.data.items || response.data || []
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch categories')
    }

    throw error
  }
}
