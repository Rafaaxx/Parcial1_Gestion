import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * IngredientCustomizer — ingredient exclusion UI
 *
 * Receives a list of ingredients and shows a toggle for each
 * removable ingredient (es_removible = true).
 * Returns an array of excluded ingredient IDs.
 */
import { useCallback } from 'react';
export const IngredientCustomizer = ({ ingredientes, excludedIds, onChange, }) => {
    const removable = ingredientes.filter((ing) => ing.es_removible);
    const handleToggle = useCallback((ingredientId) => {
        const isExcluded = excludedIds.includes(ingredientId);
        if (isExcluded) {
            onChange(excludedIds.filter((id) => id !== ingredientId));
        }
        else {
            onChange([...excludedIds, ingredientId]);
        }
    }, [excludedIds, onChange]);
    if (removable.length === 0)
        return null;
    return (_jsxs("div", { className: "space-y-2", children: [_jsx("h4", { className: "text-sm font-medium text-gray-700 dark:text-gray-300", children: "Personalizar ingredientes" }), _jsx("p", { className: "text-xs text-gray-500 dark:text-gray-400", children: "Desmarc\u00E1 los ingredientes que quer\u00E9s excluir" }), _jsx("div", { className: "space-y-1.5", children: removable.map((ing) => {
                    const isExcluded = excludedIds.includes(ing.id);
                    return (_jsxs("label", { className: `flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${isExcluded
                            ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                            : 'bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'}`, children: [_jsx("input", { type: "checkbox", checked: !isExcluded, onChange: () => handleToggle(ing.id), className: "w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer" }), _jsx("span", { className: `text-sm ${isExcluded
                                    ? 'text-red-700 dark:text-red-400 line-through'
                                    : 'text-gray-900 dark:text-gray-100'}`, children: ing.nombre }), isExcluded && (_jsx("span", { className: "ml-auto text-xs text-red-500 font-medium", children: "Excluido" }))] }, ing.id));
                }) })] }));
};
export default IngredientCustomizer;
//# sourceMappingURL=IngredientCustomizer.js.map