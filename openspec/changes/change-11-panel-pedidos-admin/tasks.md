# CHANGE-11: Panel de Gestión de Pedidos — Tasks

## 1. Backend: Extender endpoint GET /pedidos con filtros

- [ ] 1.1 Agregar query params al router: `estado`, `desde`, `hasta`, `busqueda`
- [ ] 1.2 Modificar PedidoService.listar_pedidos() para aplicar filtros de estado, fecha y búsqueda
- [ ] 1.3 Agregar join con usuario en repository para obtener nombre/email del cliente
- [ ] 1.4 Actualizar schema PedidoListResponse para incluir campo `cliente` con {id, nombre, email}
- [ ] 1.5 Probar endpoint con filtros usando curl/Postman (estado=CONFIRMADO, desde=2026-01-01)
- [ ] 1.6 Ejecutar tests existentes para asegurar no regression

## 2. Frontend: Hooks y Types actualizados

- [ ] 2.1 Actualizar types.ts para incluir campo cliente en PedidoListItem
- [ ] 2.2 Crear tipo PedidoFilters para los filtros de UI { estado?, desde?, hasta?, busqueda? }
- [ ] 2.3 Actualizar usePedidos hook para aceptar parámetros de filtro
- [ ] 2.4 Actualizar API layer para enviar query params de filtro

## 3. Frontend: Componente OrderFilters

- [ ] 3.1 Crear componente OrderFilters.tsx con dropdown de estados
- [ ] 3.2 Agregar selector de rango de fechas (desde/hasta)
- [ ] 3.3 Agregar input de búsqueda por texto
- [ ] 3.4 Integrar filtros con TanStack Query (refetch con nuevos params)
- [ ] 3.5 Estilizar con Tailwind (responsive)

## 4. Frontend: Componente OrdersTable mejorado

- [ ] 4.1 Agregar columna "Cliente" a la tabla (nombre + email)
- [ ] 4.2 Agregar link/click en fila para abrir modal de detalle
- [ ] 4.3 Mantener paginación existente

## 5. Frontend: Componente OrderDetailModal

- [ ] 5.1 Crear OrderDetailModal.tsx con estado open/close
- [ ] 5.2 Implementar Tab "Resumen" con info general del pedido
- [ ] 5.3 Implementar Tab "Líneas" con tabla de productos
- [ ] 5.4 Implementar Tab "Historial" (placeholder por ahora)
- [ ] 5.5 Implementar Tab "Pago" (info básica si existe)
- [ ] 5.6 Agregar botones de transición de estado en footer del modal

## 6. Frontend: Componente HistorialTimeline

- [ ] 6.1 Crear HistorialTimeline.tsx (visual timeline)
- [ ] 6.2 Mostrar nodos de estado con timestamps y actor
- [ ] 6.3 Diseño vertical con conectores
- [ ] 6.4 Integrar en Tab "Historial" del modal

## 7. Frontend: Botones de transición contextuales

- [ ] 7.1 Crear función getTransicionesDisponibles(estado, roles)
- [ ] 7.2 Renderizar botones según transiciones disponibles
- [ ] 7.3 Manejar modal de motivo para cancelaciones
- [ ] 7.4 Integrar con useTransicionEstado hook existente

## 8. Frontend: Integración en AdminOrders.tsx

- [ ] 8.1 Importar y usar OrderFilters en la página
- [ ] 8.2 Importar y usar OrderDetailModal
- [ ] 8.3 Conectar tabla con modal (click en fila abre modal)
- [ ] 8.4 Mantener funcionalidad de transición de estado existente

## 9. Testing y verificación

- [ ] 9.1 Probar filtros con diferentes estados (PENDIENTE, CONFIRMADO, etc.)
- [ ] 9.2 Probar filtro de fecha con rango válido
- [ ] 9.3 Probar búsqueda con nombre de cliente
- [ ] 9.4 Probar búsqueda por ID de pedido
- [ ] 9.5 Probar modal de detalle con tabs
- [ ] 9.6 Probar timeline con historial real
- [ ] 9.7 Probar botones de transición con diferentes roles
- [ ] 9.8 Verificar responsive en mobile

## 10. Documentación y cleanup

- [ ] 10.1 Actualizar CHANGES.md con estado de CHANGE-11
- [ ] 10.2 Commit de las tareas completadas (conventional commits)