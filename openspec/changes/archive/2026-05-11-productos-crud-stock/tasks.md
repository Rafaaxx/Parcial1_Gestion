## 1. Modelos y Migraciones

- [x] 1.1 Crear modelo Producto en app/models/producto.py
- [x] 1.2 Crear modelo ProductoCategoria en app/models/producto_categoria.py
- [x] 1.3 Crear modelo ProductoIngrediente en app/models/producto_ingrediente.py
- [x] 1.4 Actualizar app/models/__init__.py con los nuevos modelos
- [x] 1.5 Generar migración Alembic: alembic revision --autogenerate -m "add productos tables"
- [x] 1.6 Aplicar migración: alembic upgrade head

## 2. Repositorios

- [x] 2.1 Crear producto_repository.py en app/repositories/
- [x] 2.2 Implementar métodos: get_by_id, list_with_filters, create, update, soft_delete
- [x] 2.3 Implementar métodos para asociaciones: add_categoria, remove_categoria, add_ingrediente, remove_ingrediente
- [x] 2.4 Crear método de stock con SELECT FOR UPDATE para atomicidad

## 3. Schemas Pydantic

- [x] 3.1 Crear app/modules/productos/schemas.py
- [x] 3.2 Definir ProductoCreate, ProductoUpdate, ProductoRead, ProductoDetail
- [x] 3.3 Definir schemas para asociaciones: ProductoCategoriaCreate, ProductoIngredienteCreate

## 4. Service Layer

- [x] 4.1 Crear app/modules/productos/service.py
- [x] 4.2 Implementar validación de nombre único
- [x] 4.3 Implementar validación de stock >= 0
- [x] 4.4 Implementar lógica de soft delete
- [x] 4.5 Implementar métodos para gestionar asociaciones con categorías e ingredientes

## 5. Router / Endpoints

- [x] 5.1 Crear app/modules/productos/router.py
- [x] 5.2 POST /productos - Crear producto (ADMIN/STOCK)
- [x] 5.3 GET /productos - Listar productos con filtros (público)
- [x] 5.4 GET /productos/{id} - Detalle producto
- [x] 5.5 PUT /productos/{id} - Editar producto (ADMIN/STOCK)
- [x] 5.6 DELETE /productos/{id} - Soft delete (ADMIN)
- [x] 5.7 PATCH /productos/{id}/stock - Actualizar stock (ADMIN/STOCK)
- [x] 5.8 PATCH /productos/{id}/disponibilidad - Toggle disponible (ADMIN/STOCK)
- [x] 5.9 POST/DELETE /productos/{id}/categorias - Gestionar categorías
- [x] 5.10 POST/DELETE /productos/{id}/ingredientes - Gestionar ingredientes
- [x] 5.11 Registrar router en app/main.py

## 6. Testing

- [x] 6.1 Crear tests/integration/test_productos_api.py
- [x] 6.2 Tests para CRUD completo
- [x] 6.3 Tests para filtros y paginación
- [x] 6.4 Tests para gestión de stock
- [x] 6.5 Tests para asociaciones
- [x] 6.6 Tests para RBAC (permisos por rol)

## 7. Documentación

- [x] 7.1 Actualizar README del backend con endpoints de productos
- [x] 7.2 Verificar que Swagger UI muestre los nuevos endpoints