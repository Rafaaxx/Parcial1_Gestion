/**
 * useCartDrawer — custom hook to manage cart drawer open/close state
 */
interface UseCartDrawerReturn {
    isOpen: boolean;
    openCart: () => void;
    closeCart: () => void;
    toggleCart: () => void;
}
export declare function useCartDrawer(): UseCartDrawerReturn;
export default useCartDrawer;
//# sourceMappingURL=useCartDrawer.d.ts.map