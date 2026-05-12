/**
 * Zustand store for catalog filters and UI state
 * Manages: searchText, selectedCategory, priceRange, allergenExclusions, pagination
 */

import { create } from 'zustand'
import { CatalogFilters, ProductsQueryParams } from '../types/catalog'

interface CatalogStore extends CatalogFilters {
  // Actions
  setSearch: (text: string) => void
  setCategory: (id: number | null) => void
  setPriceRange: (from: number | null, to: number | null) => void
  setAllergenExclusions: (allergens: number[]) => void
  setPage: (page: number) => void
  setLimit: (limit: number) => void
  resetFilters: () => void

  // Selectors
  getQueryParams: () => ProductsQueryParams
  isFilterActive: () => boolean
}

const defaultFilters: CatalogFilters = {
  searchText: '',
  selectedCategory: null,
  priceFrom: null,
  priceTo: null,
  excludedAllergens: [],
  currentPage: 1,
  limit: 20,
}

export const useCatalogStore = create<CatalogStore>((set, get) => ({
  // Initial state
  ...defaultFilters,

  // Actions
  setSearch: (text: string) => set({ searchText: text, currentPage: 1 }),

  setCategory: (id: number | null) => set({ selectedCategory: id, currentPage: 1 }),

  setPriceRange: (from: number | null, to: number | null) =>
    set({ priceFrom: from, priceTo: to, currentPage: 1 }),

  setAllergenExclusions: (allergens: number[]) =>
    set({ excludedAllergens: allergens, currentPage: 1 }),

  setPage: (page: number) => set({ currentPage: Math.max(1, page) }),

  setLimit: (limit: number) => set({ limit: Math.max(1, limit), currentPage: 1 }),

  resetFilters: () => set(defaultFilters),

  // Selectors
  getQueryParams: (): ProductsQueryParams => {
    const state = get()
    const skip = (state.currentPage - 1) * state.limit

    const params: ProductsQueryParams = {
      skip,
      limit: state.limit,
    }

    if (state.searchText.trim()) {
      params.busqueda = state.searchText.trim()
    }

    if (state.selectedCategory) {
      params.categoria = state.selectedCategory
    }

    if (state.priceFrom !== null) {
      params.precio_desde = state.priceFrom
    }

    if (state.priceTo !== null) {
      params.precio_hasta = state.priceTo
    }

    if (state.excludedAllergens.length > 0) {
      params.excluirAlergenos = state.excludedAllergens.join(',')
    }

    return params
  },

  isFilterActive: (): boolean => {
    const state = get()

    return (
      state.searchText.trim() !== '' ||
      state.selectedCategory !== null ||
      state.priceFrom !== null ||
      state.priceTo !== null ||
      state.excludedAllergens.length > 0
    )
  },
}))
