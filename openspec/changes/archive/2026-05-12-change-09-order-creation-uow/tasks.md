# Tasks: CHANGE-09 — Order Creation with Unit of Work

Lista de tareas atomicas para implementar `change-09-order-creation-uow`.

**Reglas:**
- Cada tarea < 3 horas
- Prohibido tocar repo remoto (CERO push/pull/merge)
- Tests requieren PostgreSQL (no SQLite)

---

## Fase 1: Base de Datos

### Tarea 1: Crear migration pedidos tables
- **Archivo**: `migrations/versions/008_add_pedidos_tables.py`
- **Accion**: Crear migration Alembic para tablas `pedidos`, `detalles_pedido`, `historial_estado_pedido`
- **Validacion**: `alembic upgrade head` sin errores en PostgreSQL
- **Tiempo estimado**: 1h

### Tarea 2: Crear modelos SQLModel
- **Archivos**: 
  - `app/models/pedido.py` (nuevo)
  - `app/models/__init__.py` (actualizar exports)
- **Accion**: Crear clases `Pedido`, `DetallePedido`, `HistorialEstadoPedido` con relaciones
- **Validacion**: `python -c "from app.models.pedido import Pedido, DetallePedido, HistorialEstadoPedido; print('OK')"`
- **Tiempo estimado**: 1h

---

## Fase 2: Repositories

### Tarea 3: Extender ProductoRepository con get_for_update()
- **Archivo**: `app/repositories/producto_repository.py`
- **Accion**: Agregar metodo `get_for_update(producto_id)` con `SELECT ... FOR UPDATE`
- **Validacion**: Test que falla en SQLite, pasa en PostgreSQL
- **Tiempo estimado**: 1h

### Tarea 4: Crear PedidoRepository
- **Archivo**: `app/repositories/pedido_repository.py` (nuevo)
- **Accion**: Crear `PedidoRepository` y `DetallePedidoRepository`
- **Validacion**: Import correcto y herencia de BaseRepository
- **Tiempo estimado**: 1h

### Tarea 5: Crear HistorialEstadoPedidoRepository
- **Archivo**: `app/repositories/historial_repository.py` (nuevo)
- **Accion**: Crear `HistorialEstadoPedidoRepository` (SOLO create y find; NO update/delete)
- **Validacion**: No tiene metodos update/delete
- **Tiempo estimado**: 1h

---

## Fase 3: Unit of Work

### Tarea 6: Extender UnitOfWork
- **Archivo**: `app/uow.py`
- **Accion**: Agregar properties `pedidos`, `detalles_pedido`, `historial_pedido`
- **Validacion**: `uow.pedidos` retorna PedidoRepository; `uow.historial_pedido` retorna HistorialEstadoPedidoRepository
- **Tiempo estimado**: 1h

---

## Fase 4: Schemas

### Tarea 7: Crear schemas de pedidos
- **Archivo**: `app/modules/pedidos/schemas.py` (nuevo)
- **Accion**: Crear `ItemPedidoRequest`, `CrearPedidoRequest`, `DetallePedidoRead`, `HistorialEstadoPedidoRead`, `PedidoRead`, `PedidoDetail`, `PedidoListResponse`
- **Validacion**: Pydantic valida correctamente los request bodies
- **Tiempo estimado**: 2h

---

## Fase 5: Servicio

### Tarea 8: Crear PedidoService
- **Archivo**: `app/modules/pedidos/service.py` (nuevo)
- **Accion**: Implementar logica de creacion atomica con validaciones secuenciales
  - Validar direccion (ownership)
  - Validar forma_pago (existe y habilitada)
  - Validar stock (SELECT FOR UPDATE)
  - Calcular totales
  - Crear Pedido + DetallePedido + HistorialEstadoPedido
- **Validacion**: Tests de rollback completo cuando falla stock
- **Tiempo estimado**: 4h

---

## Fase 6: Router

### Tarea 9: Crear router de pedidos
- **Archivo**: `app/modules/pedidos/router.py` (nuevo)
- **Accion**: Implementar endpoints:
  - POST /api/v1/pedidos (crear, rol CLIENT/ADMIN)
  - GET /api/v1/pedidos (listar, filtrado por rol)
  - GET /api/v1/pedidos/{id} (detalle)
  - GET /api/v1/pedidos/{id}/historial (historial de estados)
- **Validacion**: `pytest tests/integration/test_pedidos_api.py` pasa
- **Tiempo estimado**: 3h

### Tarea 10: Registrar router en main.py
- **Archivo**: `app/main.py`
- **Accion**: Importar y registrar `pedidos_router` con prefijo `/api/v1`
- **Validacion**: Swagger UI muestra endpoints de pedidos
- **Tiempo estimado**: 30min

---

## Fase 7: Tests

### Tarea 11: Fixture de PostgreSQL para tests
- **Archivo**: `tests/conftest.py`
- **Accion**: Agregar fixture `postgres_db` que requiere PostgreSQL
- **Validacion**: Tests marcados con `@pytest.mark.postgres` fallan en SQLite

### Tarea 12: Tests de integracion de pedidos
- **Archivo**: `tests/integration/test_pedidos_api.py` (nuevo)
- **Accion**: Tests:
  - Crear pedido exitoso (201)
  - Stock insuficiente genera rollback (422)
  - Forma de pago invalida (422)
  - Direccion no pertenece al usuario (404)
  - CLIENT ve solo sus pedidos
  - ADMIN ve todos los pedidos
  - Historial tiene estado_desde=NULL inicial
- **Validacion**: Todos los tests pasan con PostgreSQL
- **Tiempo estimado**: 3h

---

## Fase 8: Verificacion

### Tarea 13: Ejecutar migration y seed
- **Accion**: `alembic upgrade head` + verificar que tablas existen en `food_store_db`
- **Validacion**: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';`
- **Tiempo estimado**: 30min

### Tarea 14: Verificar atomicidad
- **Accion**: Test manual: intentar crear pedido con stock insuficiente
- **Validacion**: `SELECT COUNT(*) FROM pedidos;` retorna 0

### Tarea 15: Verificar snapshots
- **Accion**: Crear pedido, modificar producto, verificar que DetallePedido tiene valores old
- **Validacion**: Query directa a BD confirma snapshots correctos

---

## Resumen de Tareas

| # | Tarea | Archivos | Tiempo |
|---|-------|---------|--------|
| 1 | Migration pedidos tables | `migrations/versions/008_add_pedidos_tables.py` | 1h |
| 2 | Modelos SQLModel | `app/models/pedido.py` | 1h |
| 3 | get_for_update() | `app/repositories/producto_repository.py` | 1h |
| 4 | PedidoRepository | `app/repositories/pedido_repository.py` | 1h |
| 5 | HistorialRepository | `app/repositories/historial_repository.py` | 1h |
| 6 | Extender UoW | `app/uow.py` | 1h |
| 7 | Schemas | `app/modules/pedidos/schemas.py` | 2h |
| 8 | PedidoService | `app/modules/pedidos/service.py` | 4h |
| 9 | Router | `app/modules/pedidos/router.py` | 3h |
| 10 | Registrar en main.py | `app/main.py` | 30min |
| 11 | Fixture PostgreSQL | `tests/conftest.py` | 1h |
| 12 | Tests integracion | `tests/integration/test_pedidos_api.py` | 3h |
| 13 | Ejecutar migration | - | 30min |
| 14 | Verificar atomicidad | - | 30min |
| 15 | Verificar snapshots | - | 30min |
| | **TOTAL** | | **~21h** |

---

**Generado**: 2026-05-12 | **Change**: change-09-order-creation-uow | **Metodologia**: SDD
