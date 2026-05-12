/**
 * PaginationControls Component
 * Navigation controls for paginated product listing
 */
interface PaginationControlsProps {
    currentPage: number;
    totalItems: number;
    itemsPerPage: number;
    onPageChange: (page: number) => void;
    isLoading?: boolean;
}
export declare function PaginationControls({ currentPage, totalItems, itemsPerPage, onPageChange, isLoading, }: PaginationControlsProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=PaginationControls.d.ts.map