## ADDED Requirements

### Requirement: Actualizar stock de producto
El sistema SHALL permitir a usuarios con rol STOCK o ADMIN actualizar la cantidad de stock de un producto de forma atómica.

#### Scenario: Actualizar stock exitoso
- **WHEN** usuario STOCK envía PATCH /api/v1/productos/1/stock con stock_cantidad=50
- **THEN** sistema retorna 200 OK con producto actualizado y stock_cantidad=50

#### Scenario: Stock no puede ser negativo
- **WHEN** usuario STOCK envía PATCH /api/v1/productos/1/stock con stock_cantidad=-5
- **THEN** sistema retorna 422 Unprocessable Entity con error "El stock no puede ser negativo"

#### Scenario: Stock con race condition
- **WHEN** dos requests concurrentes intentan actualizar stock del mismo producto
- **THEN** sistema usa SELECT FOR UPDATE para garantizar atomicidad y evitar race conditions

### Requirement: Toggle disponibilidad
El sistema SHALL permitir a usuarios con rol STOCK o ADMIN cambiar el campo disponible de un producto independientemente del stock.

#### Scenario: Desactivar producto
- **WHEN** usuario STOCK envía PATCH /api/v1/productos/1/disponibilidad con disponible=false
- **THEN** sistema retorna 200 OK y producto no aparece en listados públicos

#### Scenario: Reactivar producto
- **WHEN** usuario STOCK envía PATCH /api/v1/productos/1/disponibilidad con disponible=true
- **THEN** sistema retorna 200 OK y producto aparece en listados públicos

### Requirement: Consultar stock actual
El sistema SHALL permitir consultar el stock actual de un producto.

#### Scenario: Consultar stock de producto
- **WHEN** usuario envía GET /api/v1/productos/1
- **THEN** sistema retorna producto con campo stock_cantidad visible

#### Scenario: Stock cero no necessarily means unavailable
- **WHEN** producto tiene stock_cantidad=0 pero disponible=true
- **THEN** producto aparece en catálogo pero debe indicate que no hay disponibilidad
- **THEN** el endpoint de detalle indica disponibilidad=false si stock_cantidad=0