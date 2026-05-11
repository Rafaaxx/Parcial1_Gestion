## Context

El CHANGE-04 (Ingredientes) está implementado. Ahora se necesita crear el módulo de Productos que permita CRUD completo, gestión de stock atómico y asociaciones N:M con categorías e ingredientes. Este módulo es prerequisito para CHANGE-07 (Catálogo público) y CHANGE-08 (Carrito).

## Goals / Non-Goals

**Goals:**
- CRUD completo de productos con soft delete
- Gestión de stock con atomicidad (SELECT FOR UPDATE)
- Asociación N:M con categorías (ProductoCategoria)
- Asociación N:M con ingredientes con flag es_removible (ProductoIngrediente)
- Endpoints públicos para catálogo (filtrado, paginación)
- Validaciones: precio como NUMERIC, stock >= 0

**Non-Goals:**
- Integración con MercadoPago (CHANGE-12)
- Carrito de compras (CHANGE-08) — solo API
- Panel admin de productos (CHANGE-14)

## Decisions

### Estructura de modelos
- `Producto`: tabla principal con campos: nombre, descripcion, precio_base (NUMERIC), stock_cantidad, disponible, imagen
- `ProductoCategoria`: tabla pivot con producto_id, categoria_id, es_principal
- `ProductoIngrediente`: tabla pivot con producto_id, ingrediente_id, es_removible

### Gestión de stock
- Actualización de stock usa SELECT FOR UPDATE para evitar race conditions
- Validación: stock_cantidad >= 0 en todo momento
- El campo "disponible" es independiente del stock (permite ocultar sin importar cantidad)

### Endpoints
- CRUD: POST/GET/PUT/DELETE /api/v1/productos
- Stock: PATCH /api/v1/productos/{id}/stock
- Associations: endpoints para agregar/eliminar categorías e ingredientes
- Público: GET /api/v1/productos (con filtros, paginación)

### Permisos RBAC
- READ público (sin auth)
- CREATE/UPDATE/DELETE: solo ADMIN y STOCK

## Risks / Trade-offs

- [Riesgo]软删除 productos con pedidos activos → Mitigación: El soft delete solo marca deleted_at, los pedidos históricos mantienen referencia
- [Riesgo]Precio NUMERIC vs float → Mitigación: Usar Decimal de Python, no float
- [Riesgo] atomicidad stock en Updates → Mitigación: Service valida stock nuevo >= 0 antes de actualizar

## Migration Plan

1. Crear modelos: Producto, ProductoCategoria, ProductoIngrediente
2. Generar migración Alembic
3. Crear repository con BaseRepository
4. Implementar service con validaciones
5. Crear router con endpoints
6. Registrar router en main.py