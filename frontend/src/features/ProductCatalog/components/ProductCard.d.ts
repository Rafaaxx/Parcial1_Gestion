/**
 * ProductCard Component
 * Displays a single product in card format with image, price, categories, and availability
 */
import { ProductListItem } from '../types/catalog';
interface ProductCardProps {
    product: ProductListItem;
    onClick?: () => void;
}
export declare function ProductCard({ product, onClick }: ProductCardProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=ProductCard.d.ts.map