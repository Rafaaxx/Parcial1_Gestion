/**
 * CatalogFilters Component
 * Search, category, price range, and allergen filters with Tailwind styling
 */

import { useState, useEffect } from 'react'
import { useCatalogStore } from '../stores/catalogStore'
import { getCategories, getAllergens } from '../api/catalogApi'
import { CategoryInfo, AllergenInfo } from '../types/catalog'

export function CatalogFilters() {
  const {
    searchText,
    selectedCategory,
    priceFrom,
    priceTo,
    excludedAllergens,
    setSearch,
    setCategory,
    setPriceRange,
    setAllergenExclusions,
    resetFilters,
    isFilterActive,
  } = useCatalogStore()

  const [categories, setCategories] = useState<CategoryInfo[]>([])
  const [allergens, setAllergens] = useState<AllergenInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)

  // Load categories and allergens on mount
  useEffect(() => {
    async function loadData() {
      try {
        const [catsData, allData] = await Promise.all([getCategories(), getAllergens()])
        setCategories(catsData)
        setAllergens(allData)
      } catch (err) {
        console.error('Failed to load filter options:', err)
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [])

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
  }

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value
    setCategory(value ? Number(value) : null)
  }

  const handleAllergenToggle = (allergenId: number) => {
    const updated = excludedAllergens.includes(allergenId)
      ? excludedAllergens.filter((id) => id !== allergenId)
      : [...excludedAllergens, allergenId]
    setAllergenExclusions(updated)
  }

  const handlePriceFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value ? Number(e.target.value) : null
    setPriceRange(value, priceTo)
  }

  const handlePriceToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value ? Number(e.target.value) : null
    setPriceRange(priceFrom, value)
  }

  return (
    <aside className="w-full lg:w-64 bg-white rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 lg:mb-0">
        <h2 className="text-xl font-bold text-gray-900">Filters</h2>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="lg:hidden text-gray-600 hover:text-gray-900"
          aria-label="Toggle filters"
        >
          {isExpanded ? '✕' : '☰'}
        </button>
      </div>

      {/* Filter Content */}
      <div className={`hidden lg:block space-y-6 ${isExpanded ? 'block' : 'hidden'} lg:block`}>
        {/* Search Input */}
        <div>
          <label htmlFor="search" className="block text-sm font-semibold text-gray-900 mb-2">
            Search
          </label>
          <input
            id="search"
            type="text"
            value={searchText}
            onChange={handleSearchChange}
            placeholder="Product name..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Search products"
          />
        </div>

        {/* Category Filter */}
        <div>
          <label htmlFor="category" className="block text-sm font-semibold text-gray-900 mb-2">
            Category
          </label>
          <select
            id="category"
            value={selectedCategory ?? ''}
            onChange={handleCategoryChange}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            aria-label="Filter by category"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.nombre}
              </option>
            ))}
          </select>
        </div>

        {/* Price Range Filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-3">Price Range</label>
          <div className="space-y-2">
            <div>
              <label htmlFor="priceFrom" className="text-xs text-gray-600">
                From
              </label>
              <input
                id="priceFrom"
                type="number"
                value={priceFrom ?? ''}
                onChange={handlePriceFromChange}
                placeholder="0"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Minimum price"
              />
            </div>
            <div>
              <label htmlFor="priceTo" className="text-xs text-gray-600">
                To
              </label>
              <input
                id="priceTo"
                type="number"
                value={priceTo ?? ''}
                onChange={handlePriceToChange}
                placeholder="No limit"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Maximum price"
              />
            </div>
          </div>
        </div>

        {/* Allergen Exclusions */}
        {allergens.length > 0 && (
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-3">
              Exclude Allergens
            </label>
            <div className="space-y-2">
              {allergens.map((allergen) => (
                <label key={allergen.id} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={excludedAllergens.includes(allergen.id)}
                    onChange={() => handleAllergenToggle(allergen.id)}
                    className="w-4 h-4 text-red-600 rounded focus:ring-2 focus:ring-red-500"
                    aria-label={`Exclude ${allergen.nombre}`}
                  />
                  <div className="ml-3 flex items-center">
                    <span className="text-sm text-gray-700">{allergen.nombre}</span>
                    <span className="ml-2 inline-block px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full font-medium">
                      ⚠️
                    </span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Clear Filters Button */}
        {isFilterActive() && (
          <button
            onClick={resetFilters}
            className="w-full px-4 py-2 bg-gray-200 text-gray-900 font-semibold rounded-md hover:bg-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
            aria-label="Clear all filters"
          >
            Clear Filters
          </button>
        )}
      </div>
    </aside>
  )
}
