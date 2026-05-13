# CHANGE-11: Panel de Gestión de Pedidos — Tasks

## 1. Backend: Extender endpoint GET /pedidos con filtros

- [x] 1.1 Agregar query params al router: `estado`, `desde`, `hasta`, `busqueda`
- [x] 1.2 Modificar PedidoService.listar_pedidos() para aplicar filtros de estado, fecha y búsqueda
- [x] 1.3 Agregar join con usuario en repository para obtener nombre/email del cliente
- [x] 1.4 Actualizar schema PedidoListResponse para incluir campo `cliente` con {id, nombre, email}
- [x] 1.5 Probar endpoint con filtros usando curl/Postman (estado=CONFIRMADO, desde=2026-01-01)
- [x] 1.6 Ejecutar tests existentes para asegurar no regression

## 2. Frontend: Hooks y Types actualizados

- [x] 2.1 Actualizar types.ts para incluir campo cliente en PedidoListItem
- [x] 2.2 Crear tipo PedidoFilters para los filtros de UI { estado?, desde?, hasta?, busqueda? }
- [x] 2.3 Actualizar usePedidos hook para aceptar parámetros de filtro
- [x] 2.4 Actualizar API layer para enviar query params de filtro

## 3. Frontend: Componente OrderFilters

- [x] 3.1 Crear componente OrderFilters.tsx con dropdown de estados
- [x] 3.2 Agregar selector de rango de fechas (desde/hasta)
- [x] 3.3 Agregar input de búsqueda por texto
- [x] 3.4 Integrar filtros con TanStack Query (refetch con nuevos params)
- [x] 3.5 Estilizar con Tailwind (responsive)

## 4. Frontend: Componente OrdersTable mejorado

- [x] 4.1 Agregar columna "Cliente" a la tabla (nombre + email)
- [x] 4.2 Agregar link/click en fila para abrir modal de detalle
- [x] 4.3 Mantener paginación existente

## 5. Frontend: Componente OrderDetailModal

- [x] 5.1 Crear OrderDetailModal.tsx con estado open/close
- [x] 5.2 Implementar Tab "Resumen" con info general del pedido
- [x] 5.3 Implementar Tab "Líneas" con tabla de productos
- [x] 5.4 Implementar Tab "Historial" (placeholder por ahora)
- [x] 5.5 Implementar Tab "Pago" (info básica si existe)
- [x] 5.6 Agregar botones de transición de estado en footer del modal

## 6. Frontend: Componente HistorialTimeline

- [x] 6.1 Crear HistorialTimeline.tsx (visual timeline)
- [x] 6.2 Mostrar nodos de estado con timestamps y actor
- [x] 6.3 Diseño vertical con conectores
- [x] 6.4 Integrar en Tab "Historial" del modal

## 7. Frontend: Botones de transición contextuales

- [x] 7.1 Crear función getTransicionesDisponibles(estado, roles) - ya existía
- [x] 7.2 Renderizar botones según transiciones disponibles
- [x] 7.3 Manejar modal de motivo para cancelaciones
- [x] 7.4 Integrar con useTransicionEstado hook existente

## 8. Frontend: Integración en AdminOrders.tsx

- [x] 8.1 Importar y usar OrderFilters en la página
- [x] 8.2 Importar y usar OrderDetailModal
- [x] 8.3 Conectar tabla con modal (click en fila abre modal)
- [x] 8.4 Mantener funcionalidad de transición de estado existente

## 9. Testing y verificación

- [x] 9.1 Probar filtros con diferentes estados (PENDIENTE, CONFIRMADO, etc.)
- [x] 9.2 Probar filtro de fecha con rango válido
- [x] 9.3 Probar búsqueda con nombre de cliente
- [x] 9.4 Probar búsqueda por ID de pedido
- [x] 9.5 Probar modal de detalle con tabs
- [x] 9.6 Probar timeline con historial real
- [x] 9.7 Probar botones de transición con diferentes roles
- [x] 9.8 Verificar responsive en mobile

## 10. Documentación y cleanup

- [x] 10.1 Actualizar CHANGES.md con estado de CHANGE-11
- [x] 10.2 Commit de las tareas completadas (conventional commits)