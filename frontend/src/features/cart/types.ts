/**
 * Cart store interface for CHANGE-08 (Shopping Cart)
 * Reserved for future implementation
 */

export interface CartItem {
  productoId: string;
  producto: {
    id: string;
    nombre: string;
    precio: number;
    imagen?: string;
  };
  cantidad: number;
  personalizacion?: {
    ingredienteId: string;
    removido: boolean;
  }[];
}

export interface CartState {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (productoId: string) => void;
  updateQuantity: (productoId: string, cantidad: number) => void;
  clearCart: () => void;
  totalItems: () => number;
  subtotal: () => number;
  total: () => number;
}
