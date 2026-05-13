# CHANGE-11: Panel de Gestión de Pedidos (Admin)

## Why

El sistema Food Store necesita una interfaz completa para que los roles ADMIN y PEDIDOS puedan gestionar pedidos del sistema. Actualmente existe un componente básico AdminOrders.tsx con tabla y paginación, pero faltan funcionalidades críticas: filtros por estado y fecha, búsqueda por cliente, modal de detalle con tabs (Resumen/Líneas/Historial/Pago), y visualización timeline del historial de estados. Los clientes también necesitan ver su propio historial de pedidos con los mismos detalles.

Este change es prioritario porque el equipo de pedidos no puede operar efectivamente sin filtros y el panel de detalle es esencial para tomar decisiones sobre procesamiento de pedidos.

## What Changes

**Nuevas capacidades frontend:**
- ✅ OrdersTable mejorada: agregar columna "Cliente" (nombre/email del usuario)
- ✅ OrderFilters: dropdown por estado, selector de rango de fechas
- ✅ Búsqueda: input para buscar por número de pedido o nombre de cliente
- ✅ OrderDetail modal: 4 tabs (Resumen, Líneas, Historial, Pago)
- ✅ HistorialTimeline: visualización visual de transiciones de estado con timestamps y actor
- ✅ StateTransitionButtons: botones de acción contextuales según rol y estado actual del pedido

**Modificaciones backend:**
- Agregar query params de filtro a GET /pedidos: `?estado=CONFIRMADO&desde=2026-01-01&hasta=2026-03-31&busqueda=pizza`
- El endpoint actual ya soporta paginación y filtrado por rol (CLIENT vs ADMIN/PEDIDOS)
- Agregar join con usuario para incluir nombre/email del cliente en la respuesta

**Rollback plan:**
- Si el frontend tiene problemas de renderizado, el endpoint GET /pedidos sigue funcionando igual
- Los cambios son additive (solo se agregan features, no se rompe nada existente)

## Capabilities

### New Capabilities
- `order-management-ui`: Panel de gestión de pedidos con filtros, búsqueda, y detalle modal — cubre US-051 y US-052
- `order-history-timeline`: Visualización Timeline del historial de transiciones de estado — cubre requisito de US-052 "historial completo de estados con fechas y actores"

### Modified Capabilities
- `order-pedidos-crud`: Se extiende la especificación existente para agregar filtros de búsqueda por estado, fecha y texto en el endpoint GET /api/v1/pedidos

## Impact

**Backend:**
- `backend/app/modules/pedidos/router.py`: agregar query params (estado, desde, hasta, busqueda)
- `backend/app/modules/pedidos/service.py`: agregar lógica de filtrado
- `backend/app/modules/pedidos/schemas.py`: agregar campos de filtro al request

**Frontend:**
- `frontend/src/pages/AdminOrders.tsx`: mejorar tabla con filtros, búsqueda, y detalle modal
- `frontend/src/features/pedidos/`: posiblemente agregar nuevos hooks useOrderDetail
- Nuevo componente `frontend/src/features/pedidos/components/OrderDetailModal.tsx`
- Nuevo componente `frontend/src/features/pedidos/components/HistorialTimeline.tsx`
- Nuevo componente `frontend/src/features/pedidos/components/OrderFilters.tsx`

**Rutas afectadas:**
- `/admin/pedidos` (ya existe, se mejora)

**User Stories relacionadas:**
- US-049: Ver mis pedidos (Cliente)
- US-050: Ver detalle de mi pedido (Cliente)
- US-051: Ver todos los pedidos (Gestor de Pedidos)
- US-052: Ver detalle de cualquier pedido (Gestor/Admin)