/**
 * IngredientList component
 * Displays a table of active ingredients with pagination and filters
 */
interface IngredientListProps {
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  readonly?: boolean;
}
export declare function IngredientList({
  onEdit,
  onDelete,
  readonly,
}: IngredientListProps): import('react/jsx-runtime').JSX.Element;
export {};
//# sourceMappingURL=IngredientList.d.ts.map
