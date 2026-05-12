## Why

El carrito de compras es una funcionalidad central del e-commerce: permite a los clientes seleccionar productos del catálogo, personalizar ingredientes removibles, y prepararse para crear un pedido. Sin carrito, el flujo de compra está incompleto. Esta funcionalidad es prerrequisito directo de CHANGE-09 (Creación de Pedidos).

Actualmente los clientes pueden navegar el catálogo (CHANGE-07) pero no tienen forma de acumular productos para una compra. Este change implementa el carrito **100% client-side** vía Zustand + localStorage, siguiendo la arquitectura definida en `docs/Integrador.txt` (sección 9) y las user stories US-029 a US-034.

## What Changes

### Nuevo
- **cartStore (Zustand)**: Store completo del carrito con persistencia en localStorage, acciones CRUD de items, selectores de totales
- **CartDrawer component**: Panel lateral (drawer) que muestra los items del carrito, cantidades, personalización y totales
- **"Agregar al carrito" button + modal**: En la página de detalle de producto, permite seleccionar cantidad y excluir ingredientes removibles
- **CartProvider / CartBadge**: Badge en la navegación con count de items
- **Integración con catálogo**: Los botones de agregar aparecen en el listado de productos (card) y en el detalle
- **Persistencia del carrito**: Sobrevive a refresh, cierre del navegador y logout/login (vía Zustand persist middleware)

### Sin cambios en backend
El carrito es **exclusivamente client-side** (RN-CR01). No se crean endpoints ni tablas nuevas. El backend ya expone los datos necesarios vía los endpoints del catálogo (CHANGE-06/CHANGE-07).

## Capabilities

### New Capabilities
- `cart-store`: Store Zustand del carrito con persistencia, acciones (addItem, removeItem, updateQuantity, clearCart) y selectores (totalItems, subtotal, costoEnvio, total). Incluye lógica de personalización de ingredientes removibles.
- `cart-ui`: Componentes de frontend para visualizar e interactuar con el carrito: CartDrawer con lista de items y totales, CartBadge en navbar, botón "Agregar al carrito" en cards y detalle de producto, modal de personalización de ingredientes.

### Modified Capabilities
<!-- Sin cambios en capacidades existentes. El catálogo (CHANGE-07) ya expone los datos necesarios. -->

## Impact

### Frontend — Archivos a crear/modificar
- `frontend/src/shared/stores/cartStore.ts` — **NUEVO**: Store Zustand completo
- `frontend/src/features/cart/` — **NUEVO**: Feature completa del carrito
  - `components/CartDrawer.tsx` — Drawer lateral
  - `components/CartItem.tsx` — Item individual dentro del drawer
  - `components/CartBadge.tsx` — Badge en navbar
  - `components/AddToCartButton.tsx` — Botón de agregar
  - `components/IngredientCustomizer.tsx` — Modal/popup de personalización
  - `hooks/useCart.ts` — Hook que consume cartStore
- `frontend/src/pages/cart/` — **NUEVO**: Página de carrito (opcional, v1 usa drawer)
- `frontend/src/features/catalog/components/ProductCard.tsx` — **MODIFICAR**: Agregar botón "Agregar al carrito"
- `frontend/src/features/catalog/components/ProductDetail.tsx` — **MODIFICAR**: Agregar botón + personalización
- `frontend/src/app/App.tsx` o `frontend/src/app/Layout.tsx` — **MODIFICAR**: Integrar CartDrawer y CartBadge

### Backend
- Sin cambios. El carrito es client-side.

### Dependencias
- **CHANGE-07 (Catálogo)**: Necesita los endpoints de producto y detalle para obtener datos
- **CHANGE-01 (Auth)**: Necesita el authStore y el user autenticado (para asociar carrito en CHANGE-09)
- RN-CR01 a RN-CR05 como reglas de negocio

### Riesgos y rollback
- **Bajo**: El carrito es client-side, no afecta backend. Rollback = revertir cambios en frontend.
- **Riesgo**: Datos del carrito pueden perderse si el usuario borra localStorage. Mitigación: el cartStore persiste automáticamente y es transparente para el usuario.
