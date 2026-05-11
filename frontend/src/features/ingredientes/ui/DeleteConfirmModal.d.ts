/**
 * DeleteConfirmModal component
 * Modal for confirming ingredient deletion
 */
interface DeleteConfirmModalProps {
    ingredientId: number | null;
    ingredientName?: string;
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}
export declare function DeleteConfirmModal({ ingredientId, ingredientName, isOpen, onClose, onSuccess, }: DeleteConfirmModalProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=DeleteConfirmModal.d.ts.map