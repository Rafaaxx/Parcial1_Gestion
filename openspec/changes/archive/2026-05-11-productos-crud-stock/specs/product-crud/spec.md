## ADDED Requirements

### Requirement: Crear producto
El sistema SHALL permitir a usuarios con rol ADMIN o STOCK crear nuevos productos con los campos: nombre, descripción, precio_base, stock_cantidad, disponible e imagen (URL opcional).

#### Scenario: Crear producto exitoso
- **WHEN** usuario autenticado con rol ADMIN envía POST /api/v1/productos con datos válidos
- **THEN** sistema retorna 201 Created con el producto creado incluyendo ID generado

#### Scenario: Crear producto con nombre duplicado
- **WHEN** usuario autenticado envía POST /api/v1/productos con nombre que ya existe (deleted_at IS NULL)
- **THEN** sistema retorna 409 Conflict con error "Ya existe un producto con ese nombre"

#### Scenario: Crear producto con precio negativo
- **WHEN** usuario autenticado envía POST /api/v1/productos con precio_base < 0
- **THEN** sistema retorna 422 Unprocessable Entity con error de validación

#### Scenario: Crear producto sin autenticación
- **WHEN** usuario no autenticado envía POST /api/v1/productos
- **THEN** sistema retorna 401 Unauthorized

### Requirement: Listar productos
El sistema SHALL permitir listar productos con filtrado por categoría, disponibilidad y búsqueda por nombre, con paginación.

#### Scenario: Listar productos público
- **WHEN** usuario envía GET /api/v1/productos
- **THEN** sistema retorna 200 OK con lista de productos disponibles (disponible=true, deleted_at IS NULL)

#### Scenario: Listar productos con filtros
- **WHEN** usuario envía GET /api/v1/productos?categoria=5&disponible=true&busqueda=pizza
- **THEN** sistema retorna solo productos que cumplen todos los filtros

#### Scenario: Listar productos con paginación
- **WHEN** usuario envía GET /api/v1/productos?skip=0&limit=20
- **THEN** sistema retorna máximo 20 productos con header X-Total-Count

### Requirement: Obtener detalle de producto
El sistema SHALL permitir obtener el detalle completo de un producto incluyendo sus categorías e ingredientes asociados.

#### Scenario: Obtener producto existente
- **WHEN** usuario envía GET /api/v1/productos/1
- **THEN** sistema retorna 200 OK con producto incluyendo array de categorías e ingredientes

#### Scenario: Obtener producto eliminado
- **WHEN** usuario envía GET /api/v1/productos/{id} donde producto tiene deleted_at no nulo
- **THEN** sistema retorna 404 Not Found

### Requirement: Editar producto
El sistema SHALL permitir a usuarios con rol ADMIN o STOCK editar todos los campos de un producto.

#### Scenario: Editar producto exitoso
- **WHEN** usuario ADMIN envía PUT /api/v1/productos/1 con datos válidos
- **THEN** sistema retorna 200 OK con producto actualizado

#### Scenario: Editar producto inexistente
- **WHEN** usuario ADMIN envía PUT /api/v1/productos/999
- **THEN** sistema retorna 404 Not Found

### Requirement: Eliminar producto (soft delete)
El sistema SHALL permitir a usuarios con rol ADMIN eliminar productos lógicamente (soft delete).

#### Scenario: Eliminar producto exitoso
- **WHEN** usuario ADMIN envía DELETE /api/v1/productos/1
- **THEN** sistema retorna 204 No Content y marca deleted_at con timestamp

#### Scenario: Eliminar producto con pedidos activos
- **WHEN** usuario ADMIN envía DELETE /api/v1/productos/1 que tiene pedidos asociados
- **THEN** sistema permite el soft delete (los pedidos históricos mantienen referencia)