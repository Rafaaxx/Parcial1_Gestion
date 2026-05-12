## ADDED Requirements

### Requirement: Catálogo público sin autenticación
El sistema SHALL permitir acceso público al catálogo de productos sin necesidad de autenticación.

#### Scenario: Acceso público al catálogo
- **WHEN** usuario sin auth envía GET /api/v1/productos
- **THEN** sistema retorna 200 OK con lista de productos disponibles

#### Scenario: Producto no disponible no aparece en catálogo
- **WHEN** producto tiene disponible=false
- **THEN** NO aparece en GET /api/v1/productos (público)

### Requirement: Búsqueda de productos
El sistema SHALL permitir buscar productos por nombre usando ILIKE.

#### Scenario: Búsqueda por nombre
- **WHEN** usuario envía GET /api/v1/productos?busqueda=pizza
- **THEN** sistema retorna productos cuyo nombre contiene "pizza" (case-insensitive)

#### Scenario: Búsqueda sin resultados
- **WHEN** usuario envía GET /api/v1/productos?busqueda=xyz123
- **THEN** sistema retorna 200 OK con array vacío y X-Total-Count=0

### Requirement: Filtro por rango de precio
El sistema SHALL permitir filtrar productos por rango de precio.

#### Scenario: Filtro precio desde-hasta
- **WHEN** usuario envía GET /api/v1/productos?precio_desde=100&precio_hasta=500
- **THEN** sistema retorna productos con precio_base entre 100 y 500

### Requirement: No revelar stock exacto
El sistema SHALL no revelar el stock exacto en endpoints públicos, solo indicar si hay disponibilidad.

#### Scenario: Stock visible solo para admin
- **WHEN** usuario ADMIN envía GET /api/v1/productos/1
- **THEN** sistema incluye campo stock_cantidad en respuesta

#### Scenario: Stock oculto en público
- **WHEN** usuario sin auth envía GET /api/v1/productos/1
- **THEN** sistema NO incluye campo stock_cantidad, solo disponibilidad booleana

### Requirement: Paginación
El sistema SHALL soportar paginación con parámetros skip y limit.

#### Scenario: Paginación default
- **WHEN** usuario envía GET /api/v1/productos
- **THEN** sistema usa skip=0, limit=20 por defecto

#### Scenario: Paginación custom
- **WHEN** usuario envía GET /api/v1/productos?skip=40&limit=20
- **THEN** sistema retorna productos 41-60 ordered by created_at DESC