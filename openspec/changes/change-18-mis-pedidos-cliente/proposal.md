## Why

Los clientes necesitan una vista específica para consultar el historial de sus pedidos, ver el detalle con snapshots de precios y productos al momento de la compra, seguir el estado a través del timeline de transiciones, y cancelar pedidos solo cuando están en estado PENDIENTE. Actualmente CHANGE-11 cubre el panel de Admin/Gestor, pero falta la vista del Cliente que es un requisito fundamental del sistema (US-043, US-047, US-049, US-050).

## What Changes

- Nueva página `/mis-pedidos` en el frontend para clientes autenticados
- Componente `PedidoCard` para mostrar resumen: número, fecha, estado badge, total, cantidad de ítems
- Página de detalle `/mis-pedidos/:id` con tabs: Resumen | Líneas | Historial | Pago
- Componente `HistorialTimeline` visual con transiciones de estado y timestamps
- Componente `EstadoBadge` colorizado por estado (reutilizable en toda la app)
- Modal `CancelarPedidoModal` con motivo obligatorio (RN-FS08)
- Hooks TanStack Query: `useMisPedidos`, `usePedidoDetalle`, `usePedidoHistorial`, `usePedidoPago`, `useCancelarPedido`
- Filtro por estado en el listado (`?estado=EN_CAMINO`)
- Paginación con `page`, `size`, `total` (RN-DA07)

## Capabilities

### New Capabilities

- **mis-pedidos-cliente**: Vista del cliente para listar, ver detalle, seguir estado y cancelar sus propios pedidos. Backend endpoints ya existen (`GET /api/v1/pedidos`, `GET /api/v1/pedidos/{id}`, `GET /api/v1/pedidos/{id}/historial`, `DELETE /api/v1/pedidos/{id}`, `GET /api/v1/pagos/{pedido_id}`) — solo requiere integración frontend.

### Modified Capabilities

- Ninguno. Los endpoints de backend ya están implementados en CHANGE-09 y CHANGE-10.

## Impact

- **Frontend**: Nuevos componentes y páginas bajo `src/pages/pedidos/` y `src/features/pedidos/` siguiendo FSD
- **Backend**: No requiere cambios — endpoints existentes con filtrado por JWT userId
- **Dependencias**: CHANGE-09 (pedidos), CHANGE-10 (FSM), CHANGE-01 (auth JWT)

## Rollback Plan

Si la implementación falla, los cambios son puramente frontend:
1. Revertir cambios en `src/pages/pedidos/` y `src/features/pedidos/`
2. Los endpoints del backend no se modifican, por lo que no hay impacto en datos