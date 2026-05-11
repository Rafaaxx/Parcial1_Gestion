## ADDED Requirements

### Requirement: Asociar producto a categorías
El sistema SHALL permitir a usuarios ADMIN o STOCK asociar un producto a múltiples categorías (relación N:M).

#### Scenario: Agregar categoría a producto
- **WHEN** usuario ADMIN envía POST /api/v1/productos/1/categorias con categoria_id=5
- **THEN** sistema retorna 201 Created con asociación creada

#### Scenario: Asociación duplicada
- **WHEN** usuario ADMIN envía POST /api/v1/productos/1/categorias con categoria_id que ya está asociada
- **THEN** sistema retorna 409 Conflict con error "La categoría ya está asociada al producto"

#### Scenario: Categoría inexistente
- **WHEN** usuario ADMIN envía POST /api/v1/productos/1/categorias con categoria_id=999
- **THEN** sistema retorna 404 Not Found

### Requirement: Quitar categoría de producto
El sistema SHALL permitir a usuarios ADMIN o STOCK desasociar una categoría de un producto.

#### Scenario: Quitar categoría exitosa
- **WHEN** usuario ADMIN envía DELETE /api/v1/productos/1/categorias/5
- **THEN** sistema retorna 204 No Content

### Requirement: Asociar ingredientes a producto
El sistema SHALL permitir a usuarios ADMIN o STOCK asociar ingredientes a un producto, indicando si son removibles.

#### Scenario: Agregar ingrediente removible
- **WHEN** usuario ADMIN envía POST /api/v1/productos/1/ingredientes con ingrediente_id=3 y es_removible=true
- **THEN** sistema retorna 201 Created y el ingrediente aparece en el producto como removible

#### Scenario: Agregar ingrediente no removible
- **WHEN** usuario ADMIN envía POST /api/v1/productos/1/ingredientes con ingrediente_id=3 y es_removible=false
- **THEN** sistema retorna 201 Created y el ingrediente aparece como no removible

#### Scenario: Ingrediente es alérgeno
- **WHEN** ingrediente tiene es_alergeno=true
- **THEN** el producto muestra badge de alérgeno en el catálogo público

### Requirement: Quitar ingrediente de producto
El sistema SHALL permitir a usuarios ADMIN o STOCK desasociar un ingrediente de un producto.

#### Scenario: Quitar ingrediente exitoso
- **WHEN** usuario ADMIN DELETE /api/v1/productos/1/ingredientes/3
- **THEN** sistema retorna 204 No Content

### Requirement: Listar ingredientes de producto
El sistema SHALL permitir listar los ingredientes asociados a un producto.

#### Scenario: Listar ingredientes
- **WHEN** usuario envía GET /api/v1/productos/1/ingredientes
- **THEN** sistema retorna lista de ingredientes con flag es_removible y es_alergeno