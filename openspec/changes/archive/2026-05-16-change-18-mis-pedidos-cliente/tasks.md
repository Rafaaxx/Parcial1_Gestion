## 1. Estructura Base y Tipos

- [x] 1.1 Crear directorio `src/features/pedidos/` siguiendo FSD
- [x] 1.2 Crear subdirectorios: `api/`, `components/`, `types/`
- [x] 1.3 Crear `types/pedidos.ts` con interfaces: Pedido, PedidoDetalle, HistorialEstado, LineaPedido, PagoInfo
- [x] 1.4 Crear `types/index.ts` exportando todos los tipos del dominio pedidos

## 2. API Layer (TanStack Query)

- [x] 2.1 Crear `api/useMisPedidos.ts` → hook con paginación y filtro por estado (existe en hooks/index.ts)
- [x] 2.2 Crear `api/usePedidoDetalle.ts` → hook para obtener detalle de un pedido (existe en hooks/index.ts)
- [x] 2.3 Crear `api/usePedidoHistorial.ts` → hook para obtener timeline de estados
- [x] 2.4 Crear `api/usePedidoPago.ts` → hook para obtener info de pago
- [x] 2.5 Crear `api/useCancelarPedido.ts` → mutation para cancelar pedido (existe en hooks/index.ts)
- [x] 2.6 Crear `api/index.ts` exportando todos los hooks (existe en hooks/index.ts)

## 3. Componentes UI

- [x] 3.1 Mover/crear `EstadoBadge.tsx` en `src/components/ui/` (reutilizable) - ya existe en pedidos
- [x] 3.2 Crear `components/PedidoCard.tsx` → tarjeta resumen (id, fecha, estado badge, total, cantidad)
- [x] 3.3 Crear `components/PedidoSkeleton.tsx` → skeleton para listado
- [x] 3.4 Crear `components/HistorialTimeline.tsx` → timeline visual de transiciones
- [x] 3.5 Crear `components/CancelarPedidoModal.tsx` → modal con campo motivo obligatorio
- [x] 3.6 Crear `components/PaymentStatusBadge.tsx` → badge para estado de pago
- [x] 3.7 Crear `components/PedidoDetailTabs.tsx` → tabs: Resumen | Líneas | Historial | Pago

## 4. Páginas

- [x] 4.1 Crear `src/pages/mis-pedidos/MisPedidosPage.tsx` → página principal con listado y filtros
- [x] 4.2 Crear `src/pages/mis-pedidos/PedidoDetailPage.tsx` → página de detalle con tabs
- [x] 4.3 Crear `src/pages/mis-pedidos/MisPedidosEmpty.tsx` → estado vacío con link al catálogo
- [x] 4.4 Crear `pages/mis-pedidos/index.ts` exportando las páginas

## 5. Navegación y Routing

- [x] 5.1 Agregar ruta `/mis-pedidos` en el router principal (protegida, rol CLIENT)
- [x] 5.2 Agregar ruta `/mis-pedidos/:pedidoId` para detalle
- [x] 5.3 Agregar link en navbar/sidebar del cliente (depende de CHANGE-02)
- [x] 5.4 Verificar que las rutas estén protegidas y solo accesibles para rol CLIENT

## 6. Testing y Verificación

- [x] 6.1 Verificar listado de pedidos propios (no ajenos) - 403 si accede a otro
- [x] 6.2 Verificar paginación (page, size, total)
- [x] 6.3 Verificar filtro por estado (?estado=PENDIENTE)
- [x] 6.4 Verificar detalle muestra las 4 tabs correctamente
- [x] 6.5 Verificar timeline con actor "SISTEMA" para transiciones automáticas
- [x] 6.6 Verificar botón cancelar oculto para estados no PENDIENTE
- [x] 6.7 Verificar modal requiere motivo obligatorio
- [x] 6.8 Verificar estado de pago (approved/rejected/pending/none)
- [x] 6.9 Verificar skeleton loaders durante carga
- [x] 6.10 Verificar toast de éxito/error en operaciones

## 7. Integración Final

- [x] 7.1 Verificar navegación fluida entre listado y detalle
- [x] 7.2 Verificar que al cancelar redirecciona al listado con toast
- [x] 7.3 Verificar estado vacío cuando no hay pedidos