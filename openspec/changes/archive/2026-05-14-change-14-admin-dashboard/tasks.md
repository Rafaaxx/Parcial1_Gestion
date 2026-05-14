## 1. Base de datos: migraciones

- [ ] 1.1 Crear migración Alembic para añadir columna `activo` BOOLEAN DEFAULT TRUE a tabla `usuarios`
- [ ] 1.2 Crear índices en `pedidos.creado_en`, `pedidos.estado_codigo` para optimizar queries de métricas
- [ ] 1.3 Ejecutar migración y verificar en base de datos local

## 2. Backend: Middleware de roles (ADMIN implícito)

- [ ] 2.1 Modificar `requires_roles` en middleware de autenticación para que ADMIN tenga acceso implícito a cualquier endpoint
- [ ] 2.2 Verificar que endpoints existentes de catálogo y pedidos funcionan con ADMIN sin rol STOCK/PEDIDOS
- [ ] 2.3 Tests: ADMIN accede a endpoint de catálogo, ADMIN accede a endpoint de pedidos, STOCK no accede a pedidos

## 3. Backend: Admin router base

- [ ] 3.1 Crear router `/api/v1/admin/` con dependencia de autenticación ADMIN
- [ ] 3.2 Registrar router en `main.py`

## 4. Backend: Endpoints de métricas

- [ ] 4.1 Implementar `GET /api/v1/admin/metricas/resumen` con KPIs agregados (ventas, pedidos, usuarios, top productos)
- [ ] 4.2 Implementar `GET /api/v1/admin/metricas/ventas` con granularidad (dia/semana/mes)
- [ ] 4.3 Implementar `GET /api/v1/admin/metricas/productos-top` con ranking de productos
- [ ] 4.4 Implementar `GET /api/v1/admin/metricas/pedidos-por-estado` con distribución y porcentajes
- [ ] 4.5 Agregar esquemas Pydantic de respuesta para cada endpoint de métricas
- [ ] 4.6 Tests: cada endpoint de métricas con datos reales y con filtros

## 5. Backend: Endpoints de gestión de usuarios

- [ ] 5.1 Implementar `GET /api/v1/admin/usuarios` con paginación, búsqueda ILIKE y filtro por rol
- [ ] 5.2 Implementar `PUT /api/v1/admin/usuarios/{id}` con validación de último ADMIN
- [ ] 5.3 Implementar `PATCH /api/v1/admin/usuarios/{id}/estado` con invalidación de tokens
- [ ] 5.4 Implementar lógica de invalidación de refresh tokens al cambiar roles/estado
- [ ] 5.5 Agregar esquemas Pydantic de request/response para usuarios admin
- [ ] 5.6 Tests: listar, editar rol, desactivar, validar último ADMIN, auto-desactivar prohibido

## 6. Frontend: Página de Dashboard

- [ ] 6.1 Crear hook `useAdminMetrics` con TanStack Query para consumir endpoints de métricas
- [ ] 6.2 Crear componente `MetricCard` para KPIs individuales
- [ ] 6.3 Crear componente `SalesLineChart` con `<LineChart>` de Recharts (ventas por período)
- [ ] 6.4 Crear componente `TopProductsBarChart` con `<BarChart>` de Recharts
- [ ] 6.5 Crear componente `OrdersPieChart` con `<PieChart>` de Recharts
- [ ] 6.6 Crear página `/admin/dashboard` con grid de KPIs + gráficos + selector de fechas
- [ ] 6.7 Agregar ruta `/admin/dashboard` al router protegido del frontend
- [ ] 6.8 Manejar estados: loading (skeleton), error (toast), empty (sin datos)

## 7. Frontend: Página de gestión de usuarios

- [ ] 7.1 Crear hook `useAdminUsers` con TanStack Query (listar, editar, desactivar)
- [ ] 7.2 Crear componente `UsersTable` con tabla paginada y búsqueda
- [ ] 7.3 Crear modal `EditUserModal` para editar datos y roles
- [ ] 7.4 Crear componente `UserStatusToggle` para activar/desactivar
- [ ] 7.5 Crear página `/admin/usuarios` con tabla + modal
- [ ] 7.6 Agregar ruta `/admin/usuarios` al router protegido

## 8. Frontend: Sidebar y navegación ADMIN

- [ ] 8.1 Agregar ítem "Dashboard" al sidebar con icono para rol ADMIN
- [ ] 8.2 Agregar ítem "Usuarios" al sidebar con icono para rol ADMIN
- [ ] 8.3 Verificar que STOCK y PEDIDOS no vean estos ítems

## 9. Testing integral

- [ ] 9.1 Tests de integración backend: flujo completo de métricas con datos seed
- [ ] 9.2 Tests de integración backend: ciclo completo de gestión de usuarios
- [ ] 9.3 Tests de frontend: renderizado de dashboard con datos mock
- [ ] 9.4 Tests de frontend: tabla de usuarios y modal de edición
