## ADDED Requirements

### Requirement: Página de Dashboard con KPIs

El frontend SHALL tener una ruta `/admin/dashboard` que muestre indicadores clave del negocio.

- **KPIs numéricos**: Tarjetas con total ventas, cantidad de pedidos, usuarios registrados
- **Carga de datos**: vía TanStack Query con `useQuery` a los endpoints de métricas
- **Filtro de fechas**: Selector de rango de fechas que refresca todos los widgets
- **Estados**: Loading (skeleton), Error (toast/mensaje), Empty (mensaje "sin datos")

#### Scenario: Admin ve dashboard con datos

- **WHEN** un Admin navega a `/admin/dashboard`
- **THEN** el sistema muestra 4 tarjetas de KPIs con valores cargados del endpoint resumen

#### Scenario: Dashboard sin datos (proyecto nuevo)

- **WHEN** un Admin navega a `/admin/dashboard` y no hay pedidos
- **THEN** el sistema muestra KPIs en cero y gráficos vacíos con mensaje "Sin datos para el período"

---

### Requirement: Gráfico de ventas por período (líneas)

El dashboard SHALL incluir un gráfico de líneas con evolución de ventas.

- **Componente**: `<LineChart>` de Recharts
- **Eje X**: Período (día/semana/mes)
- **Eje Y**: Monto total
- **Datos**: `GET /api/v1/admin/metricas/ventas`
- **Selector de granularidad**: Botones dia/semana/mes que recargan el gráfico

#### Scenario: Admin cambia granularidad

- **WHEN** un Admin selecciona "Mes" en el selector de granularidad
- **THEN** el gráfico se refresca con datos agrupados por mes

---

### Requirement: Ranking de productos más vendidos (barras)

El dashboard SHALL incluir un gráfico de barras con top productos.

- **Componente**: `<BarChart>` de Recharts
- **Eje X**: Nombre del producto
- **Eje Y**: Cantidad vendida
- **Datos**: `GET /api/v1/admin/metricas/productos-top?top=10`

#### Scenario: Admin ve top productos

- **WHEN** un Admin está en `/admin/dashboard`
- **THEN** ve un gráfico de barras con los 10 productos más vendidos

---

### Requirement: Distribución de pedidos por estado (circular)

El dashboard SHALL incluir un gráfico circular con distribución de estados.

- **Componente**: `<PieChart>` de Recharts
- **Labels**: Nombre del estado + porcentaje
- **Datos**: `GET /api/v1/admin/metricas/pedidos-por-estado`

#### Scenario: Admin ve distribución de estados

- **WHEN** un Admin está en `/admin/dashboard`
- **THEN** ve un gráfico circular con la distribución de pedidos por estado y sus porcentajes
