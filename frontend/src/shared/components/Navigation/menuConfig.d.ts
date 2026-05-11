/**
 * Menu configuration by role for role-based navigation
 */
export interface MenuItem {
    label: string;
    path: string;
    icon: string;
    roles: Array<'ADMIN' | 'STOCK' | 'PEDIDOS' | 'CLIENT'>;
}
/**
 * Menu items grouped by role
 * - CLIENT: Catálogo, Carrito, Mis Pedidos, Mi Perfil
 * - STOCK: Productos, Categorías, Ingredientes, Stock
 * - PEDIDOS: Panel de Pedidos
 * - ADMIN: All items + Usuarios, Métricas, Configuración
 */
export declare const MENU_BY_ROLE: MenuItem[];
/**
 * Get menu items for a specific user role
 */
export declare function getMenuItemsByRole(userRoles: string[]): MenuItem[];
//# sourceMappingURL=menuConfig.d.ts.map