import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * CatalogFilters Component
 * Search, category, price range, and allergen filters with Tailwind styling
 */
import { useState, useEffect } from 'react';
import { useCatalogStore } from '../stores/catalogStore';
import { getCategories, getAllergens } from '../api/catalogApi';
export function CatalogFilters() {
    const { searchText, selectedCategory, priceFrom, priceTo, excludedAllergens, setSearch, setCategory, setPriceRange, setAllergenExclusions, resetFilters, isFilterActive, } = useCatalogStore();
    const [categories, setCategories] = useState([]);
    const [allergens, setAllergens] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isExpanded, setIsExpanded] = useState(false);
    // Load categories and allergens on mount
    useEffect(() => {
        async function loadData() {
            try {
                const [catsData, allData] = await Promise.all([getCategories(), getAllergens()]);
                setCategories(catsData);
                setAllergens(allData);
            }
            catch (err) {
                console.error('Failed to load filter options:', err);
            }
            finally {
                setIsLoading(false);
            }
        }
        loadData();
    }, []);
    const handleSearchChange = (e) => {
        setSearch(e.target.value);
    };
    const handleCategoryChange = (e) => {
        const value = e.target.value;
        setCategory(value ? Number(value) : null);
    };
    const handleAllergenToggle = (allergenId) => {
        const updated = excludedAllergens.includes(allergenId)
            ? excludedAllergens.filter((id) => id !== allergenId)
            : [...excludedAllergens, allergenId];
        setAllergenExclusions(updated);
    };
    const handlePriceFromChange = (e) => {
        const value = e.target.value ? Number(e.target.value) : null;
        setPriceRange(value, priceTo);
    };
    const handlePriceToChange = (e) => {
        const value = e.target.value ? Number(e.target.value) : null;
        setPriceRange(priceFrom, value);
    };
    return (_jsxs("aside", { className: "w-full lg:w-64 bg-white rounded-lg shadow p-6", children: [_jsxs("div", { className: "flex items-center justify-between mb-6 lg:mb-0", children: [_jsx("h2", { className: "text-xl font-bold text-gray-900", children: "Filters" }), _jsx("button", { onClick: () => setIsExpanded(!isExpanded), className: "lg:hidden text-gray-600 hover:text-gray-900", "aria-label": "Toggle filters", children: isExpanded ? '✕' : '☰' })] }), _jsxs("div", { className: `hidden lg:block space-y-6 ${isExpanded ? 'block' : 'hidden'} lg:block`, children: [_jsxs("div", { children: [_jsx("label", { htmlFor: "search", className: "block text-sm font-semibold text-gray-900 mb-2", children: "Search" }), _jsx("input", { id: "search", type: "text", value: searchText, onChange: handleSearchChange, placeholder: "Product name...", className: "w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Search products" })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "category", className: "block text-sm font-semibold text-gray-900 mb-2", children: "Category" }), _jsxs("select", { id: "category", value: selectedCategory ?? '', onChange: handleCategoryChange, disabled: isLoading, className: "w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50", "aria-label": "Filter by category", children: [_jsx("option", { value: "", children: "All Categories" }), categories.map((cat) => (_jsx("option", { value: cat.id, children: cat.nombre }, cat.id)))] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-semibold text-gray-900 mb-3", children: "Price Range" }), _jsxs("div", { className: "space-y-2", children: [_jsxs("div", { children: [_jsx("label", { htmlFor: "priceFrom", className: "text-xs text-gray-600", children: "From" }), _jsx("input", { id: "priceFrom", type: "number", value: priceFrom ?? '', onChange: handlePriceFromChange, placeholder: "0", min: "0", className: "w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Minimum price" })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "priceTo", className: "text-xs text-gray-600", children: "To" }), _jsx("input", { id: "priceTo", type: "number", value: priceTo ?? '', onChange: handlePriceToChange, placeholder: "No limit", min: "0", className: "w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Maximum price" })] })] })] }), allergens.length > 0 && (_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-semibold text-gray-900 mb-3", children: "Exclude Allergens" }), _jsx("div", { className: "space-y-2", children: allergens.map((allergen) => (_jsxs("label", { className: "flex items-center cursor-pointer", children: [_jsx("input", { type: "checkbox", checked: excludedAllergens.includes(allergen.id), onChange: () => handleAllergenToggle(allergen.id), className: "w-4 h-4 text-red-600 rounded focus:ring-2 focus:ring-red-500", "aria-label": `Exclude ${allergen.nombre}` }), _jsxs("div", { className: "ml-3 flex items-center", children: [_jsx("span", { className: "text-sm text-gray-700", children: allergen.nombre }), _jsx("span", { className: "ml-2 inline-block px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full font-medium", children: "\u26A0\uFE0F" })] })] }, allergen.id))) })] })), isFilterActive() && (_jsx("button", { onClick: resetFilters, className: "w-full px-4 py-2 bg-gray-200 text-gray-900 font-semibold rounded-md hover:bg-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500", "aria-label": "Clear all filters", children: "Clear Filters" }))] })] }));
}
//# sourceMappingURL=CatalogFilters.js.map