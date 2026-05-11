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
export const MENU_BY_ROLE: MenuItem[] = [
  // Common menu items
  {
    label: 'Dashboard',
    path: '/app/dashboard',
    icon: '📊',
    roles: ['ADMIN', 'STOCK', 'PEDIDOS'],
  },

  // CLIENT role
  {
    label: 'Catálogo',
    path: '/app/catalog',
    icon: '🛒',
    roles: ['CLIENT'],
  },
  {
    label: 'Carrito',
    path: '/app/cart',
    icon: '🛍️',
    roles: ['CLIENT'],
  },
  {
    label: 'Mis Pedidos',
    path: '/app/orders',
    icon: '📋',
    roles: ['CLIENT'],
  },
  {
    label: 'Mi Perfil',
    path: '/app/profile',
    icon: '👤',
    roles: ['CLIENT'],
  },

  // STOCK role
  {
    label: 'Productos',
    path: '/app/products',
    icon: '📦',
    roles: ['STOCK', 'ADMIN'],
  },
  {
    label: 'Categorías',
    path: '/app/categories',
    icon: '🏷️',
    roles: ['STOCK', 'ADMIN'],
  },
  {
    label: 'Ingredientes',
    path: '/app/ingredients',
    icon: '🥬',
    roles: ['STOCK', 'ADMIN'],
  },
  {
    label: 'Stock',
    path: '/app/stock',
    icon: '📊',
    roles: ['STOCK', 'ADMIN'],
  },

  // PEDIDOS role
  {
    label: 'Panel de Pedidos',
    path: '/app/orders-panel',
    icon: '📦',
    roles: ['PEDIDOS'],
  },

  // ADMIN role
  {
    label: 'Usuarios',
    path: '/app/users',
    icon: '👥',
    roles: ['ADMIN'],
  },
  {
    label: 'Métricas',
    path: '/app/metrics',
    icon: '📈',
    roles: ['ADMIN'],
  },
  {
    label: 'Configuración',
    path: '/app/settings',
    icon: '⚙️',
    roles: ['ADMIN'],
  },
];

/**
 * Get menu items for a specific user role
 */
export function getMenuItemsByRole(userRoles: string[]): MenuItem[] {
  return MENU_BY_ROLE.filter((item) => item.roles.some((role) => userRoles.includes(role)));
}
