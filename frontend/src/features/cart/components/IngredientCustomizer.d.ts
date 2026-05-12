/**
 * IngredientCustomizer — ingredient exclusion UI
 *
 * Receives a list of ingredients and shows a toggle for each
 * removable ingredient (es_removible = true).
 * Returns an array of excluded ingredient IDs.
 */
import React from 'react';
import type { IngredientInfo } from '@/features/ProductCatalog/types/catalog';
interface IngredientCustomizerProps {
    ingredientes: IngredientInfo[];
    /** Currently excluded ingredient IDs */
    excludedIds: number[];
    /** Called when the excluded set changes */
    onChange: (ids: number[]) => void;
}
export declare const IngredientCustomizer: React.FC<IngredientCustomizerProps>;
export default IngredientCustomizer;
//# sourceMappingURL=IngredientCustomizer.d.ts.map