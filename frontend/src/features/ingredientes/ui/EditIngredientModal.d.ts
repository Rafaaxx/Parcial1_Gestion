/**
 * EditIngredientModal component
 * Modal form for editing an existing ingredient
 */
interface EditIngredientModalProps {
    ingredientId: number | null;
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}
export declare function EditIngredientModal({ ingredientId, isOpen, onClose, onSuccess, }: EditIngredientModalProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=EditIngredientModal.d.ts.map