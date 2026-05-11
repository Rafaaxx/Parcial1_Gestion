/**
 * useCategories hook for fetching product categories
 */
export interface Category {
    id: string;
    nombre: string;
    subcategorias?: Category[];
}
export declare function useCategories(): {
    data: Category[];
    isLoading: boolean;
    error: Error | null;
};
//# sourceMappingURL=useCategories.d.ts.map