## Why

El módulo de Productos es fundamental para Food Store. Actualmente existe el cambio-04 (Ingredientes) pero falta el módulo de Productos que permite crear, editar, gestionar stock y asociar productos con categorías e ingredientes. Este módulo es la base para el catálogo público (CHANGE-07), el carrito (CHANGE-08) y los pedidos (CHANGE-09).

## What Changes

- **CREATE**: Alta de productos con nombre, descripción, precio, stock, disponibilidad e imagen
- **READ**: Listado de productos con filtros, paginación y detalle completo
- **UPDATE**: Edición de todos los campos del producto
- **DELETE**: Soft delete de productos (no borrar físicamente)
- **STOCK**: Gestión de stock con atomicidad (SELECT FOR UPDATE)
- **ASOCIACIONES**: Relación N:M con categorías y ingredientes (es_removible)

## Capabilities

### New Capabilities
- `product-crud`: CRUD completo de productos con soft delete
- `product-stock`: Gestión atómica de stock con validación
- `product-associations`: Asociación N:M con categorías e ingredientes
- `product-catalog-api`: Endpoints públicos para catálogo (filtrado, paginación)

### Modified Capabilities
- `ingredient-allergen-flag` (CHANGE-04): Los ingredientes ahora se asocian a productos

## Impact

- **Backend**: Nuevo módulo `app/modules/productos/` con router, service, schemas, repository
- **Modelos**: Producto, ProductoCategoria, ProductoIngrediente (nuevas tablas)
- **API**: Endpoints REST en `/api/v1/productos`
- **Dependencias**: CHANGE-04 (ingredientes), CHANGE-03 (categorías)