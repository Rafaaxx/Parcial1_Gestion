## 1. Estructura Base y Tipos

- [ ] 1.1 Crear directorio `src/features/pedidos/` siguiendo FSD
- [ ] 1.2 Crear subdirectorios: `api/`, `components/`, `types/`
- [ ] 1.3 Crear `types/pedidos.ts` con interfaces: Pedido, PedidoDetalle, HistorialEstado, LineaPedido, PagoInfo
- [ ] 1.4 Crear `types/index.ts` exportando todos los tipos del dominio pedidos

## 2. API Layer (TanStack Query)

- [ ] 2.1 Crear `api/useMisPedidos.ts` → hook con paginación y filtro por estado
- [ ] 2.2 Crear `api/usePedidoDetalle.ts` → hook para obtener detalle de un pedido
- [ ] 2.3 Crear `api/usePedidoHistorial.ts` → hook para obtener timeline de estados
- [ ] 2.4 Crear `api/usePedidoPago.ts` → hook para obtener info de pago
- [ ] 2.5 Crear `api/useCancelarPedido.ts` → mutation para cancelar pedido
- [ ] 2.6 Crear `api/index.ts` exportando todos los hooks

## 3. Componentes UI

- [ ] 3.1 Mover/crear `EstadoBadge.tsx` en `src/components/ui/` (reutilizable)
- [ ] 3.2 Crear `components/PedidoCard.tsx` → tarjeta resumen (id, fecha, estado badge, total, cantidad)
- [ ] 3.3 Crear `components/PedidoSkeleton.tsx` → skeleton para listado
- [ ] 3.4 Crear `components/HistorialTimeline.tsx` → timeline visual de transiciones
- [ ] 3.5 Crear `components/CancelarPedidoModal.tsx` → modal con campo motivo obligatorio
- [ ] 3.6 Crear `components/PaymentStatusBadge.tsx` → badge para estado de pago
- [ ] 3.7 Crear `components/PedidoDetailTabs.tsx` → tabs: Resumen | Líneas | Historial | Pago

## 4. Páginas

- [ ] 4.1 Crear `src/pages/mis-pedidos/MisPedidosPage.tsx` → página principal con listado y filtros
- [ ] 4.2 Crear `src/pages/mis-pedidos/PedidoDetailPage.tsx` → página de detalle con tabs
- [ ] 4.3 Crear `src/pages/mis-pedidos/MisPedidosEmpty.tsx` → estado vacío con link al catálogo
- [ ] 4.4 Crear `pages/mis-pedidos/index.ts` exportando las páginas

## 5. Navegación y Routing

- [ ] 5.1 Agregar ruta `/mis-pedidos` en el router principal (protegida, rol CLIENT)
- [ ] 5.2 Agregar ruta `/mis-pedidos/:pedidoId` para detalle
- [ ] 5.3 Agregar link en navbar/sidebar del cliente (depende de CHANGE-02)
- [ ] 5.4 Verificar que las rutas estén protegidas y solo accesibles para rol CLIENT

## 6. Testing y Verificación

- [ ] 6.1 Verificar listado de pedidos propios (no ajenos) - 403 si accede a otro
- [ ] 6.2 Verificar paginación (page, size, total)
- [ ] 6.3 Verificar filtro por estado (?estado=PENDIENTE)
- [ ] 6.4 Verificar detalle muestra las 4 tabs correctamente
- [ ] 6.5 Verificar timeline con actor "SISTEMA" para transiciones automáticas
- [ ] 6.6 Verificar botón cancelar oculto para estados no PENDIENTE
- [ ] 6.7 Verificar modal requiere motivo obligatorio
- [ ] 6.8 Verificar estado de pago (approved/rejected/pending/none)
- [ ] 6.9 Verificar skeleton loaders durante carga
- [ ] 6.10 Verificar toast de éxito/error en operaciones

## 7. Integración Final

- [ ] 7.1 Verificar navegación fluida entre listado y detalle
- [ ] 7.2 Verificar que al cancelar redirecciona al listado con toast
- [ ] 7.3 Verificar estado vacío cuando no hay pedidos