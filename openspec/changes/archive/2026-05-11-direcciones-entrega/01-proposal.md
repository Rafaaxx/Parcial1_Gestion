# Proposal: CHANGE-05 — Direcciones de Entrega

## Why

El sistema Food Store requiere que los clientes puedan gestionar sus direcciones de entrega para poder asociarlas a sus pedidos. Esta capacidad es crítica para:

- **Experiencia de Usuario**: Los clientes necesitan registrar y seleccionar dónde recibir sus pedidos, con la posibilidad de tener múltiples direcciones (casa, trabajo, etc.).
- **Flujo de Pedidos**: La creación de pedidos (EPIC 09) depende de que existan direcciones registradas para generar el snapshot de dirección de entrega (RN-PE03).
- **Autonomía del Cliente**: Los clientes gestionan sus propias direcciones sin intervención de administradores, siguiendo el principio de ownership (RN-RB05, RN-DI03).
- **Predeterminada**: Solo una dirección puede ser la principal por usuario, agilizando el proceso de checkout al preseleccionar la dirección favorita.

## What Changes

- **Nuevo Modelo `DireccionEntrega`**: Tabla con `id`, `user_id` (FK a usuarios), `alias` (VARCHAR(50), nullable, ej: "Casa", "Trabajo"), `linea1` (TEXT, NOT NULL), `es_principal` (BOOLEAN, default false, solo una por usuario), más timestamps de auditoría y soft delete.
- **Ownership por JWT**: Todos los endpoints filtran por `user_id` extraído del token JWT. Un cliente solo ve/edita/elimina sus propias direcciones (RN-DI03).
- **Primera Dirección como Predeterminada**: Al crear la primera dirección de un usuario, se marca automáticamente como `es_principal = true` (RN-DI01).
- **Transacción Atómica en PATCH /predeterminada**: Se quita el flag de la dirección anterior y se setea en la nueva dentro de una misma transacción (RN-DI02).
- **Soft Delete**: Las direcciones se eliminan lógicamente (set `deleted_at`), no físicamente, preservando snapshots en pedidos existentes.
- **RBAC**: Los endpoints requieren rol `CLIENT` o `ADMIN`. Solo el dueño (validado por JWT) puede operar sus direcciones.

### Endpoints

| Método | Ruta | Descripción | Auth | Status Codes |
|--------|------|-------------|------|-------------|
| `POST` | `/api/v1/direcciones` | Crear dirección | CLIENT/ADMIN | 201, 400, 422, 403 |
| `GET` | `/api/v1/direcciones` | Listar direcciones propias | CLIENT/ADMIN | 200, 403 |
| `PUT` | `/api/v1/direcciones/{id}` | Editar dirección propia | CLIENT/ADMIN | 200, 400, 404, 422, 403 |
| `DELETE` | `/api/v1/direcciones/{id}` | Soft delete dirección propia | CLIENT/ADMIN | 204, 404, 403 |
| `PATCH` | `/api/v1/direcciones/{id}/predeterminada` | Establecer como predeterminada | CLIENT/ADMIN | 200, 404, 409, 422, 403 |

### Validation Rules

- `alias`: Opcional, máximo 50 caracteres, se trimea whitespace.
- `linea1`: Requerido, no vacío, máximo 500 caracteres.
- `es_principal`: No se envía en creación (se determina automáticamente); no se actualiza directamente (solo vía PATCH /predeterminada).
- Ownership: Toda operación sobre una dirección valida que `direccion.user_id === jwt.userId`.
- Soft delete: No se puede operar sobre una dirección ya eliminada (404).
- Al eliminar la dirección predeterminada, se debe asignar otra dirección como predeterminada si existen más, o dejar sin predeterminada si era la única.

## Capabilities

### New Capabilities

- `direcciones-crud`: Crear, listar, editar y eliminar direcciones de entrega con ownership por JWT, soft delete, y soporte de dirección predeterminada.
- `direcciones-predeterminada`: Establecer y gestionar la dirección predeterminada por usuario con transacción atómica (solo una por usuario).

### Modified Capabilities

- `auth-rbac`: Los roles CLIENT y ADMIN ya existen; esta change añade nuevos endpoints protegidos por estos roles.
- `uow-pattern`: Se agrega `direcciones` repository property al UnitOfWork.

## Impact

### Backend

- **Nuevo Módulo**: `backend/app/modules/direcciones/` con estructura feature-first:
  - `__init__.py` — Inicialización del paquete
  - `schemas.py` — Pydantic schemas (DireccionCreate, DireccionUpdate, DireccionRead, DireccionListResponse)
  - `service.py` — Lógica de negocio (validación de ownership, gestión de predeterminada)
  - `router.py` — 5 endpoints REST con RBAC y ownership
- **Nuevo Modelo**: `backend/app/models/direccion_entrega.py` — SQLModel con FK a Usuario, mixins de timestamp y soft delete
- **Nuevo Repository**: `backend/app/repositories/direccion_repository.py` — Extiende BaseRepository[DireccionEntrega] con métodos para:
  - `find_by_user(user_id)` — Listar direcciones de un usuario
  - `find_by_user_and_id(user_id, id)` — Buscar dirección verificando ownership
  - `get_default_by_user(user_id)` — Obtener predeterminada actual
  - `count_by_user(user_id)` — Contar direcciones de un usuario
  - `unset_default_for_user(user_id)` — Remover flag predeterminada de todas las direcciones del usuario
- **Base de Datos**: Una nueva tabla `direccion_entrega` con FK a `usuarios`, índice compuesto en `(user_id, es_principal)` para optimizar búsqueda de predeterminada.
- **Migración Alembic**: Nuevo script de migración para crear la tabla.

### APIs

- Cinco nuevos endpoints bajo `/api/v1/direcciones`
- Todos responden con formato de error RFC 7807 (consistente con el resto del sistema)
- Rate limiting heredado de CHANGE-00 (slowapi)

### Testing

- Tests de integración para cada endpoint cubriendo:
  - Creación exitosa (con y sin alias)
  - Primera dirección se marca como predeterminada automáticamente
  - Listar solo direcciones del usuario autenticado
  - Editar dirección propia (y rechazar edición de dirección ajena)
  - Soft delete con verificación de exclusión en listados
  - PATCH /predeterminada: transacción atómica (desmarcar anterior, marcar nueva)
  - Eliminar dirección predeterminada: asignar nueva predeterminada si existe otra
  - 403 cuando otro usuario intenta acceder
  - 404 cuando la dirección no existe o está eliminada

## Linked User Stories

- **US-024**: Crear dirección de entrega
- **US-025**: Listar direcciones del cliente
- **US-026**: Editar dirección de entrega
- **US-027**: Eliminar dirección de entrega
- **US-028**: Establecer dirección predeterminada

## Business Rules Enforced

| ID | Regla | Implementación |
|----|-------|---------------|
| RN-DI01 | Primera dirección se marca predeterminada | Service cuenta direcciones del usuario; si count == 0, setea `es_principal = true` |
| RN-DI02 | Solo una predeterminada por usuario | PATCH usa transacción atómica: unset anterior + set nueva en mismo flush |
| RN-DI03 | Cliente solo ve/edita/elimina sus propias direcciones | Todo endpoint filtra por `user_id` del JWT; validación en service |

## Technical Notes

1. **Naming Convention**: El campo `es_principal` (Spanish, per project convention), no `is_default`.
2. **Soft Delete Field**: Usa `deleted_at` (TIMESTAMPTZ, nullable) per el mixin `SoftDeleteMixin` de Food Store.
3. **Foreign Key**: `user_id` → `usuarios.id` con ON DELETE CASCADE (si un usuario se elimina, sus direcciones también).
4. **Índice Único Parcial**: Se considera un índice único parcial `CREATE UNIQUE INDEX idx_direccion_principal ON direccion_entrega (user_id) WHERE es_principal = true` para garantizar a nivel DB que solo haya una predeterminada por usuario. Esto actúa como doble seguridad junto con la lógica de aplicación.
5. **Snapshot Pattern**: Las direcciones existentes se referencian por FK en pedidos, pero al crear un pedido se genera un snapshot del texto de la dirección (RN-PE03). El soft delete preserva la integridad referencial.
6. **Dependencia de US-002 (Auth)**: El sistema de autenticación JWT debe estar operativo para extraer `user_id` y roles del token.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/models/direccion_entrega.py` | New | SQLModel con FK a Usuario, timestamp mixin, soft delete |
| `app/models/__init__.py` | Modified | Exportar DireccionEntrega |
| `app/repositories/direccion_repository.py` | New | Custom repository con métodos de ownership y predeterminada |
| `app/modules/direcciones/` | New | Feature module completo (schemas, service, router, __init__) |
| `app/uow.py` | Modified | Agregar property `direcciones: DireccionRepository` |
| `app/main.py` | Modified | Registrar `router_direcciones` con prefijo `/api/v1/direcciones` |
| `backend/migrations/versions/` | New | Migration para crear tabla `direccion_entrega` |
| `backend/tests/test_direcciones.py` | New | Tests de integración para los 5 endpoints |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Race condition en PATCH /predeterminada** si dos requests simultáneos intentan establecer diferente predeterminada | Low | La transacción atómica dentro del flush de SQLAlchemy + el índice único parcial a nivel DB garantizan integridad. En caso de violación, se captura la excepción de integridad y se retorna 409. |
| **Eliminación de dirección referenciada en pedido activo** | Medium | Se evaluará si implementar validación RN-US-027 ("sin pedidos activos asociados") en el service. Por ahora, soft delete preserva el dato. |
| **Cliente con token válido intenta acceder a direcciones de otro usuario** | Low | Validación estricta de ownership en cada operación: `direccion.user_id === jwt.userId` |

## Rollback Plan

1. **Data Preservation**: Soft delete ensures no data is physically lost.
2. **Revert Migration**: `alembic downgrade -1` removes `direccion_entrega` table.
3. **Code Cleanup**: Remove `app/modules/direcciones/` directory.
4. **Router Cleanup**: Remove `app.include_router(direcciones_router)` from `app/main.py`.
5. **UoW Cleanup**: Remove `self._direcciones` and `direcciones` property from `app/uow.py`.
6. **Model Cleanup**: Remove `DireccionEntrega` from `app/models/direccion_entrega.py` and `app/models/__init__.py`.
7. **Verification**: Run test suite to ensure nothing is broken.

## Dependencies

- **change-01** (US-001, US-002, US-006): Auth system (JWT + RBAC) must be operational for ownership validation and role checking.
- **change-00** (US-000b): Database and Alembic migrations must be functional.
- **change-00d**: Unit of Work pattern and BaseRepository must exist.

---

**Estimated Effort**: 4-6 hours
**Sprint**: Sprint 4 (EPIC 07 — Direcciones de Entrega)
**Status**: Ready for design (sdd-design phase)
