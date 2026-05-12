/**
 * ProductList Component
 * Renders a grid of ProductCards with responsive layout
 */
import { ProductListItem } from '../types/catalog';
interface ProductListProps {
    products: ProductListItem[];
    onProductClick?: (id: number) => void;
    isLoading?: boolean;
}
export declare function ProductList({ products, onProductClick, isLoading }: ProductListProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=ProductList.d.ts.map