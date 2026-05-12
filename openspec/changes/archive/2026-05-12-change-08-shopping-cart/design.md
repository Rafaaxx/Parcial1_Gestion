## Context

El carrito de compras es el paso previo a la creación de un pedido. Según la arquitectura definida en `docs/Integrador.txt` (sección 9), el estado del carrito se gestiona **exclusivamente del lado del cliente** usando Zustand + localStorage (RN-CR01). No existe modelo de carrito en el backend.

**Estado actual**: CHANGE-07 (Catálogo Público) ya expone los endpoints necesarios:
- `GET /api/v1/productos` — listado paginado con filtros
- `GET /api/v1/productos/{id}` — detalle con ingredientes, categorías y `es_removible`

**Dependencias**: CHANGE-01 (Auth) provee el authStore con el usuario autenticado. CHANGE-07 provee los datos de producto desde el backend.

**Reglas de negocio aplicables**: RN-CR01 a RN-CR05 (ver `docs/Historias_de_usuario.txt`).

## Goals / Non-Goals

**Goals:**
- Implementar `cartStore` con Zustand + persist middleware en localStorage
- Proveer acciones: `addItem`, `removeItem`, `updateQuantity`, `clearCart`
- Proveer selectores: `totalItems`, `subtotal`, `costoEnvio` (flat rate $50), `total`
- Implementar personalización de ingredientes removibles (`es_removible = true`)
- Si un producto ya está en el carrito al agregarlo de nuevo → incrementar cantidad (no duplicar)
- Crear CartDrawer (panel lateral) con lista de items, cantidades, personalización y totales
- Crear CartBadge en la navbar con count de items
- Integrar botón "Agregar al carrito" en ProductCard y ProductDetail
- El carrito persiste a refresh, cierre del navegador y logout/login

**Non-Goals:**
- NO se crean endpoints ni tablas en el backend
- NO hay sincronización del carrito con el backend (es client-side only, v1)
- NO hay carrito multi-sesión (el carrito es por navegador, no por usuario)
- NO hay selección de dirección de entrega (pertenece a CHANGE-09)
- NO hay selección de forma de pago (pertenece a CHANGE-09)
- NO hay checkout/pago (pertenece a CHANGE-09 y CHANGE-12)

## Decisions

### D1: Zustand persist middleware para persistencia
- **Decisión**: Usar `persist` middleware de Zustand con `localStorage` como storage backend, clave `food-store-cart`
- **Razón**: El proyecto ya usa Zustand con persist middleware en authStore. Es consistente con la arquitectura existente. localStorage es síncrono y simple, ideal para un carrito client-side.
- **Alternativa considerada**: sessionStorage → No sobrevive al cierre del navegador (viola RN-CR02). IndexedDB → Overkill para un carrito v1.

### D2: Partialize para persistencia selectiva
- **Decisión**: Persistir solo `items` (no selectores computados ni estados transitorios)
- **Razón**: Los selectores son derivados del estado, no necesitan persistencia. Sigue el patrón de `partialize` usado en authStore. Reduce tamaño de localStorage.
- **Alternativa considerada**: Persistir todo el store → Mayor tamaño en localStorage, riesgo de datos desincronizados.

### D3: Flat rate de envío ($50)
- **Decisión**: Costo de envío fijo de $50 (constante en el store)
- **Razón**: Definido en `docs/Integrador.txt` sección 3.3 y en la especificación del CHANGE-08. Se puede parametrizar en el futuro via backend.
- **Alternativa considerada**: Calcular envío dinámico por distancia → Scope mayor, no justificado para v1.

### D4: Drawer vs Página dedicada
- **Decisión**: Implementar como **drawer lateral** (CartDrawer) + badge en navbar. Sin página dedicada en v1.
- **Razón**: Drawer permite ver el carrito sin salir del catálogo, mejor UX. Es el patrón de e-commerce moderno.
- **Alternativa considerada**: Página `/cart` dedicada → Más clicks para el usuario, peor UX. Se puede agregar en v2 si es necesario.

### D5: Personalización inline en el drawer
- **Decisión**: Cada CartItem en el drawer permite editar cantidad (+/-) y ver ingredientes excluidos. La personalización de ingredientes se hace desde el ProductDetail.
- **Razón**: El drawer es para revisión rápida. La personalización detallada requiere el contexto completo del producto.
- **Alternativa considerada**: Modal de personalización desde el drawer → Complejidad extra, el drawer se vuelve pesado.

### D6: Estructura de carpetas (Feature-Sliced Design)
- **Decisión**: Crear feature `cart/` dentro de `frontend/src/features/cart/` con sus propios componentes, hooks y tipos
- **Razón**: Sigue FSD, el feature es autocontenido. Los componentes se importan desde pages y widgets según necesidad.
- **Alternativa considerada**: Poner todo en `entities/cart/` → El carrito es un feature completo con UI, no solo una entidad de datos.

## Architecture

### Flujo de datos

```
ProductCard / ProductDetail
        │
        ▼
  useCart() hook ──────→ cartStore (Zustand + persist)
        │                        │
        │                   ┌────┴────┐
        │                   │         │
        ▼                   ▼         ▼
  CartBadge (count)    CartDrawer   localStorage
                      (items,       (persist)
                       totales,
                       cantidades)
```

### cartStore — State shape

```typescript
interface CartItem {
  productoId: number;
  nombre: string;
  precio: number;        // precio_snapshot al agregar
  imagenUrl: string;
  cantidad: number;
  personalizacion: number[]; // IDs de ingredientes removidos
  ingredientes: Ingrediente[]; // info completa para mostrar
}

interface CartState {
  items: CartItem[];
  // Actions
  addItem: (producto: Producto, cantidad?: number, personalizacion?: number[]) => void;
  removeItem: (productoId: number) => void;
  updateQuantity: (productoId: number, cantidad: number) => void;
  clearCart: () => void;
  // Selectors (computados)
  totalItems: () => number;
  subtotal: () => number;
  costoEnvio: () => number;    // flat rate $50 si hay items
  total: () => number;         // subtotal + costoEnvio
}
```

### Component Tree

```typescript
// Layout (Navbar)
<CartBadge count={totalItems} onClick={openDrawer} />

// Catalog → ProductCard
<AddToCartButton producto={producto} onAdded={...} />

// Catalog → ProductDetail
<ProductDetail>
  <IngredientCustomizer ingredientes={removibles} />
  <AddToCartButton cantidad={qty} personalizacion={excludedIds} />
</ProductDetail>

// Cart Drawer (slide-over panel)
<CartDrawer open={isOpen} onClose={closeDrawer}>
  {items.map(item => <CartItem key={item.productoId} item={item} />)}
  <CartSummary subtotal={subtotal} envio={costoEnvio} total={total} />
  <CheckoutButton /> {/* nollega a CHANGE-09, placeholder */}
</CartDrawer>
```

### Reglas de negocio implementadas

| Regla | Implementación |
|-------|---------------|
| RN-CR01: Carrito client-side only | Store Zustand, sin endpoints |
| RN-CR02: Persiste a refresh/cierre/logout | Zustand persist → localStorage |
| RN-CR03: Producto duplicado → incrementar cantidad | `addItem` busca productoId existente |
| RN-CR04: Solo ingredientes removibles | `personalizacion` filtra por `es_removible` |
| RN-CR05: Personalización como array de IDs | `personalizacion: number[]` |

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| [R1] Datos del carrito se pierden si usuario borra localStorage | Es comportamiento esperado del navegador. El carrito se reconstruye vacío. |
| [R2] Precio del producto puede cambiar entre que se agrega al carrito y se crea el pedido | El precio se "congela" al agregar al carrito, pero el snapshot final se toma al crear el pedido (CHANGE-09). El carrito muestra el precio actual del catálogo como referencia. |
| [R3] Cientos de items en el carrito degradan performance | Limitar a ~50 items máximo. El drawer usa virtualización si es necesario. |
| [R4] Personalización solo funciona si el backend devuelve `es_removible` | Ya está implementado en CHANGE-06 (ProductoIngrediente.es_removible). Verificar en verify. |
| [R5] El carrito no persiste si el usuario cambia de navegador/dispositivo | Limitación conocida del carrito client-side. En v2 se podría sincronizar con backend. |

## Open Questions

1. ¿Máximo de items en el carrito? Sugerencia: 50 items.
2. ¿Mostrar precio unitario vs precio total por línea? Sugerencia: ambos.
3. ¿El CartDrawer debe mostrar botón "Ir a pagar" aunque CHANGE-09 no esté implementado? Sugerencia: mostrar botón deshabilitado con tooltip "Próximamente".
