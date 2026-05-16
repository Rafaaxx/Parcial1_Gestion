## Context

El change-18 implementa la vista "Mis Pedidos" para clientes. CHANGE-11 ya implementa el panel de Admin/Gestor con funcionalidades completas (todos los pedidos, acciones FSM, filtros avanzados). El change-18 es la vista del Cliente: solo sus propios pedidos, solo acción de cancelar desde PENDIENTE.

Los endpoints del backend ya están implementados y funcionando:
- `GET /api/v1/pedidos` → lista propia del cliente (filtrado por JWT userId)
- `GET /api/v1/pedidos/{id}` → detalle completo
- `GET /api/v1/pedidos/{id}/historial` → timeline de estados
- `DELETE /api/v1/pedidos/{id}` → cancelar pedido propio
- `GET /api/v1/pagos/{pedido_id}` → estado de pago

## Goals / Non-Goals

**Goals:**
- Implementar página principal de listado con paginación y filtro por estado
- Implementar página de detalle con tabs (Resumen | Líneas | Historial | Pago)
- Mostrar timeline visual de transiciones de estado con timestamps
- Permitir cancelación de pedidos solo cuando están en PENDIENTE
- Mostrar estado de pago (approved / rejected / pending)
- Aplicar reglas de negocio: RN-RB05, RN-FS08, RN-DA07, RN-FS06

**Non-Goals:**
- Modificar backend (endpoints ya existen)
- Implementar panel de Admin (ya está en CHANGE-11)
- Notificaciones push o email al cliente

## Decisions

### 1. Estructura de Componentes

Se sigue Feature-Sliced Design (FSD) para organizar el código:
- `src/pages/mis-pedidos/` → páginas principales
- `src/features/pedidos/` → componentes de dominio
- `src/features/pedidos/api/` → queries y mutations TanStack Query
- `src/features/pedidos/components/` → componentes específicos
- `src/features/pedidos/types/` → tipos TypeScript

### 2. Estado de Carga y Errores

- Skeleton loaders durante fetch (vistos en CHANGE-07)
- Toast de éxito/error en acciones (sistema existente en CHANGE-02)
- Estado vacío con link al catálogo cuando no hay pedidos

### 3. Reutilización de Componentes

- `EstadoBadge` se comparte con Admin (CHANGE-11) → mover a `src/components/ui/`
- `HistorialTimeline` mismo componente usado en Admin → shared component
- Skeleton loaders reutilizables de `src/components/ui/Skeleton`

### 4. Navegación

- Ruta: `/mis-pedidos` (protegida, solo CLIENT)
- Detalle: `/mis-pedidos/:pedidoId`
- Integrar en sidebar/navbar del cliente (CHANGE-02)

### 5. Paginación

- Usar `page` (0-indexed) y `size` en query params
- Obtener `total` del response para controles de UI
- Mantener estado de filtros en URL para shareability

## Risks / Trade-offs

- **[Risk]** El endpoint de listado retorna todos los pedidos del cliente → pueden ser muchos
  - **Mitigation**: Implementar paginación desde el inicio (RN-DA07 requiere `page`, `size`, `total`)

- **[Risk]** Estado de pago puede no existir si el pedido aún no fue procesado por MercadoPago
  - **Mitigation**: Mostrar "Sin información de pago" con styling apropiado, no romper la UI

- **[Risk]** Timeline de historial requiere parseo de timestamps
  - **Mitigation**: Usar utility de formato de fecha existente en el proyecto

- **[Risk]** El modal de cancelación requiere motivo obligatorio
  - **Mitigation**: Validar en frontend antes de llamar al endpoint, mostrar error si vacío

## Migration Plan

1. Crear estructura de archivos FSD en `src/features/pedidos/`
2. Implementar hooks TanStack Query en `api/`
3. Crear componentes en `components/`
4. Crear páginas en `src/pages/`
5. Agregar rutas en router (protegidas con role CLIENT)
6. Agregar link en navbar/sidebar del cliente
7. Testear flujo completo: listado → detalle → historial → cancelación