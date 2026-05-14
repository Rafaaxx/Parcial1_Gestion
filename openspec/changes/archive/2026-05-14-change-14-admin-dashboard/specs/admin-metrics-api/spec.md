## ADDED Requirements

### Requirement: Resumen de métricas del sistema

El sistema SHALL exponer un endpoint `GET /api/v1/admin/metricas/resumen` que retorne KPIs generales del negocio.

- **Autenticación**: Requiere rol ADMIN
- **Query params opcionales**: `desde`, `hasta` (ISO date) para filtrar por rango de fechas
- **Respuesta**: Objeto con:
  - `total_ventas`: SUM de pedidos ENTREGADOS en el período
  - `cantidad_pedidos`: Total de pedidos en el período
  - `pedidos_por_estado`: Array de `{ estado, cantidad }` agrupado por código de estado
  - `usuarios_registrados`: Total de usuarios registrados (sin filtro de fecha)
  - `productos_mas_vendidos`: Array de `{ producto_id, nombre, cantidad, ingreso_total }` top 5

#### Scenario: Admin solicita resumen sin filtros

- **WHEN** un Admin autenticado hace GET a `/api/v1/admin/metricas/resumen`
- **THEN** el sistema retorna 200 con KPIs de todo el histórico

#### Scenario: Admin solicita resumen con rango de fechas

- **WHEN** un Admin hace GET a `/api/v1/admin/metricas/resumen?desde=2026-01-01&hasta=2026-03-31`
- **THEN** el sistema retorna KPIs filtrados al período indicado

#### Scenario: Usuario sin rol ADMIN intenta acceder

- **WHEN** un usuario con rol STOCK hace GET a `/api/v1/admin/metricas/resumen`
- **THEN** el sistema retorna 403 Forbidden

---

### Requirement: Ventas por período con granularidad

El sistema SHALL exponer `GET /api/v1/admin/metricas/ventas` con evolución de ventas.

- **Query params**: `desde`, `hasta` (ISO date), `granularidad` (`dia` | `semana` | `mes`)
- **Respuesta**: Array de `{ periodo, monto_total, cantidad_pedidos }`
- **Agregación**: `DATE_TRUNC` según granularidad en PostgreSQL

#### Scenario: Admin consulta ventas por día

- **WHEN** un Admin hace GET a `/api/v1/admin/metricas/ventas?granularidad=dia&desde=2026-03-01&hasta=2026-03-07`
- **THEN** el sistema retorna 200 con array de 7 elementos, uno por día, cada uno con `periodo`, `monto_total`, `cantidad_pedidos`

#### Scenario: Granularidad inválida

- **WHEN** un Admin hace GET a `/api/v1/admin/metricas/ventas?granularidad=invalid`
- **THEN** el sistema retorna 422 con error de validación

---

### Requirement: Top productos más vendidos

El sistema SHALL exponer `GET /api/v1/admin/metricas/productos-top` con ranking de productos.

- **Query params**: `top` (default 10, max 50), `desde`, `hasta`
- **Respuesta**: Array de `{ producto_id, nombre, cantidad_total, ingreso_total }`
- **Orden**: Descendente por `cantidad_total`

#### Scenario: Admin consulta top 10 productos

- **WHEN** un Admin hace GET a `/api/v1/admin/metricas/productos-top?top=10`
- **THEN** el sistema retorna 200 con los 10 productos más vendidos ordenados por cantidad

#### Scenario: Top con rango de fechas

- **WHEN** un Admin hace GET a `/api/v1/admin/metricas/productos-top?top=5&desde=2026-01-01&hasta=2026-06-30`
- **THEN** el sistema retorna 200 con top 5 del período

---

### Requirement: Distribución de pedidos por estado

El sistema SHALL exponer `GET /api/v1/admin/metricas/pedidos-por-estado` para distribución de pedidos.

- **Query params**: `desde`, `hasta`
- **Respuesta**: Array de `{ estado, cantidad, porcentaje }` donde porcentaje = (cantidad / total) * 100

#### Scenario: Admin consulta distribución

- **WHEN** un Admin hace GET a `/api/v1/admin/metricas/pedidos-por-estado`
- **THEN** el sistema retorna 200 con todos los estados que tienen al menos 1 pedido, cada uno con cantidad y porcentaje
