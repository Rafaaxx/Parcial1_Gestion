# Spec: CHANGE-05 — Direcciones de Entrega

## 1. Overview

Se agrega el módulo `direcciones` que permite a los clientes gestionar sus direcciones de entrega. Los endpoints están protegidos por JWT (roles CLIENT/ADMIN) y validan ownership por `user_id` del token. Se incorporan dos nuevas capacidades (`direcciones-crud`, `direcciones-predeterminada`) y se modifican `auth-rbac` y `uow-pattern` para soportar el nuevo módulo.

---

## 2. User Stories

### US-024: Crear dirección de entrega

**Requerimiento**: El sistema MUST permitir a un usuario autenticado crear una dirección de entrega. La primera dirección del usuario MUST marcarse como `es_principal=true` automáticamente.

| ID | Req | Source |
|----|-----|--------|
| REQ-DI-01 | MUST rechazar `linea1` vacío con 422 | US-024 |
| REQ-DI-02 | MUST rechazar `alias` > 50 caracteres con 422 | US-024 |
| REQ-DI-03 | MUST rechazar `linea1` > 500 caracteres con 422 | US-024 |
| REQ-DI-04 | MUST truncar whitespace en `alias` y `linea1` (trim) | US-024 |
| REQ-DI-05 | MUST setear `es_principal=true` si es la primera dirección del usuario | RN-DI01, US-024 |
| REQ-DI-06 | MUST responder 201 + `DireccionRead` en éxito | US-024 |
| REQ-DI-07 | MUST requerir autenticación (Bearer token) | US-024 |
| REQ-DI-08 | MUST aceptar roles CLIENT y ADMIN | US-024 |

#### Scenario: Creación exitosa sin alias
- **Given** usuario autenticado sin direcciones registradas
- **When** POST `/api/v1/direcciones` con `{"linea1": "Av. Siempre Viva 123, CABA"}`
- **Then** respuesta 201 con `DireccionRead`
- **And** `es_principal = true` (primera dirección)
- **And** `alias = null`

#### Scenario: Creación exitosa con alias
- **Given** usuario autenticado
- **When** POST `/api/v1/direcciones` con `{"linea1": "Av. Siempre Viva 123, CABA", "alias": "Casa"}`
- **Then** respuesta 201 con `DireccionRead`
- **And** `alias = "Casa"`

#### Scenario: Segunda dirección no se marca predeterminada
- **Given** usuario autenticado con 1 dirección existente (`es_principal=true`)
- **When** POST `/api/v1/direcciones` con nueva dirección
- **Then** respuesta 201
- **And** `es_principal = false` en la nueva dirección
- **And** la dirección anterior sigue siendo `es_principal = true`

#### Scenario: Validación — linea1 vacío
- **Given** usuario autenticado
- **When** POST `/api/v1/direcciones` con `{"linea1": ""}`
- **Then** respuesta 422

#### Scenario: Validación — alias excede 50 caracteres
- **Given** usuario autenticado
- **When** POST `/api/v1/direcciones` con `{"linea1": "dir", "alias": "a" * 51}`
- **Then** respuesta 422

#### Scenario: Sin autenticación
- **Given** request sin Authorization header
- **When** POST `/api/v1/direcciones`
- **Then** respuesta 401

---

### US-025: Listar direcciones del cliente

**Requerimiento**: El sistema MUST devolver solo las direcciones del usuario autenticado, excluyendo soft-deleted, ordenadas por `created_at` DESC, con paginación.

| ID | Req | Source |
|----|-----|--------|
| REQ-DI-09 | MUST devolver 200 + `DireccionListResponse` | US-025 |
| REQ-DI-10 | MUST filtrar por `user_id` del JWT (nunca direcciones de otros usuarios) | RN-DI03, US-025 |
| REQ-DI-11 | MUST excluir direcciones con `deleted_at` NOT NULL | US-025 |
| REQ-DI-12 | MUST ordenar por `created_at` DESC | US-025 |
| REQ-DI-13 | MUST soportar `skip` (default 0) y `limit` (default 100) | US-025 |
| REQ-DI-14 | MUST requerir autenticación | US-025 |

#### Scenario: Listado exitoso con direcciones
- **Given** usuario autenticado con 3 direcciones registradas
- **When** GET `/api/v1/direcciones`
- **Then** respuesta 200
- **And** `items` contiene 3 direcciones, solo del usuario autenticado
- **And** `total = 3`
- **And** ordenadas por `created_at` DESC (más reciente primero)

#### Scenario: Listado vacío
- **Given** usuario autenticado sin direcciones registradas
- **When** GET `/api/v1/direcciones`
- **Then** respuesta 200
- **And** `items = []`, `total = 0`

#### Scenario: Paginación
- **Given** usuario autenticado con 10 direcciones
- **When** GET `/api/v1/direcciones?skip=0&limit=5`
- **Then** respuesta 200
- **And** `items` contiene 5 direcciones
- **And** `total = 10`, `skip = 0`, `limit = 5`

#### Scenario: No incluye soft-deleted
- **Given** usuario autenticado con 2 direcciones activas + 1 eliminada (soft delete)
- **When** GET `/api/v1/direcciones`
- **Then** `items` contiene solo 2 direcciones activas
- **And** `total = 2`

---

### US-026: Editar dirección de entrega

**Requerimiento**: El sistema MUST permitir a un usuario editar sus propias direcciones. Validar ownership: si la dirección no pertenece al usuario → 404 (no revelar existencia).

| ID | Req | Source |
|----|-----|--------|
| REQ-DI-15 | MUST rechazar actualización si `direccion.usuario_id != jwt.userId` (404, no 403) | RN-DI03, US-026 |
| REQ-DI-16 | MUST rechazar actualización de dirección soft-deleted (404) | US-026 |
| REQ-DI-17 | MUST rechazar `linea1` vacío con 422 | US-026 |
| REQ-DI-18 | MUST rechazar `alias` > 50 caracteres con 422 | US-026 |
| REQ-DI-19 | MUST responder 200 + `DireccionRead` actualizado en éxito | US-026 |
| REQ-DI-20 | MUST permitir actualización parcial (solo alias, solo linea1, o ambos) | US-026 |
| REQ-DI-21 | MUST NO permitir cambiar `es_principal` vía PUT (solo vía PATCH /predeterminada) | US-026 |

#### Scenario: Editar alias y linea1
- **Given** dirección existente del usuario autenticado
- **When** PUT `/api/v1/direcciones/{id}` con `{"alias": "Trabajo", "linea1": "Av. Corrientes 500, CABA"}`
- **Then** respuesta 200
- **And** `alias = "Trabajo"`, `linea1 = "Av. Corrientes 500, CABA"`

#### Scenario: Editar solo alias (parcial)
- **Given** dirección existente del usuario autenticado
- **When** PUT `/api/v1/direcciones/{id}` con `{"alias": "Nuevo Alias"}`
- **Then** respuesta 200
- **And** `alias = "Nuevo Alias"`, `linea1` no cambia

#### Scenario: Dirección no pertenece al usuario (404)
- **Given** dirección que pertenece a otro usuario
- **When** PUT `/api/v1/direcciones/{id}` con datos válidos
- **Then** respuesta 404 (no 403, para no revelar existencia)

#### Scenario: Dirección no existe (404)
- **Given** un ID de dirección que no existe
- **When** PUT `/api/v1/direcciones/{id}` con datos válidos
- **Then** respuesta 404

#### Scenario: Dirección soft-deleted (404)
- **Given** dirección del usuario pero con `deleted_at` seteado
- **When** PUT `/api/v1/direcciones/{id}`
- **Then** respuesta 404

---

### US-027: Eliminar dirección de entrega

**Requerimiento**: El sistema MUST realizar soft delete (marcar `deleted_at`, no borrar físicamente). Validar ownership con mismo criterio que US-026.

| ID | Req | Source |
|----|-----|--------|
| REQ-DI-22 | MUST marcar `deleted_at` con timestamp actual (no borrado físico) | US-027 |
| REQ-DI-23 | MUST validar ownership: 404 si no es del usuario | RN-DI03, US-027 |
| REQ-DI-24 | MUST responder 204 No Content en éxito | US-027 |
| REQ-DI-25 | MUST responder 404 si dirección no existe o ya eliminada | US-027 |
| REQ-DI-26 | Si se elimina la dirección predeterminada y existen otras direcciones activas, MUST asignar `es_principal=true` a la más reciente | RN-DI02, US-027 |

#### Scenario: Soft delete exitoso
- **Given** dirección activa del usuario autenticado
- **When** DELETE `/api/v1/direcciones/{id}`
- **Then** respuesta 204 No Content
- **And** `deleted_at` seteado en BD (no se borra el registro)

#### Scenario: Dirección no pertenece al usuario (404)
- **Given** dirección que pertenece a otro usuario
- **When** DELETE `/api/v1/direcciones/{id}`
- **Then** respuesta 404

#### Scenario: Dirección ya eliminada (404)
- **Given** dirección del usuario ya con `deleted_at` seteado
- **When** DELETE `/api/v1/direcciones/{id}`
- **Then** respuesta 404

#### Scenario: Eliminar predeterminada con otras direcciones existentes
- **Given** usuario con 3 direcciones, la predeterminada es ID=1
- **When** DELETE `/api/v1/direcciones/1`
- **Then** respuesta 204
- **And** la dirección más reciente (mayor `created_at`) entre las restantes ahora tiene `es_principal=true`

#### Scenario: Eliminar única dirección
- **Given** usuario con 1 sola dirección (que es predeterminada)
- **When** DELETE `/api/v1/direcciones/{id}`
- **Then** respuesta 204
- **And** usuario queda sin direcciones

---

### US-028: Establecer dirección predeterminada

**Requerimiento**: El sistema MUST cambiar la dirección predeterminada del usuario usando una transacción atómica: quita `es_principal` de la anterior y setea en la nueva. Idempotente (si ya es la predeterminada, responde 200 igual).

| ID | Req | Source |
|----|-----|--------|
| REQ-DI-27 | MUST usar transacción atómica (unset anterior + set nueva en mismo flush) | RN-DI02, US-028 |
| REQ-DI-28 | MUST validar ownership: 404 si no es del usuario | US-028 |
| REQ-DI-29 | MUST responder 200 + `DireccionRead` con `es_principal=true` | US-028 |
| REQ-DI-30 | MUST ser idempotente: si ya es la predeterminada, responder 200 igual | US-028 |
| REQ-DI-31 | MUST responder 404 si dirección no existe o soft-deleted | US-028 |

#### Scenario: Cambiar predeterminada exitosamente
- **Given** usuario con 2 direcciones: ID=1 (`es_principal=true`), ID=2 (`es_principal=false`)
- **When** PATCH `/api/v1/direcciones/2/predeterminada`
- **Then** respuesta 200
- **And** ID=1 ahora tiene `es_principal=false`
- **And** ID=2 ahora tiene `es_principal=true`

#### Scenario: Idempotente — ya es predeterminada
- **Given** dirección ID=1 con `es_principal=true`
- **When** PATCH `/api/v1/direcciones/1/predeterminada`
- **Then** respuesta 200
- **And** `es_principal=true` se mantiene

#### Scenario: Dirección no pertenece al usuario (404)
- **Given** dirección que pertenece a otro usuario
- **When** PATCH `/api/v1/direcciones/{id}/predeterminada`
- **Then** respuesta 404

#### Scenario: Dirección soft-deleted (404)
- **Given** dirección del usuario con `deleted_at` seteado
- **When** PATCH `/api/v1/direcciones/{id}/predeterminada`
- **Then** respuesta 404

---

## 3. Business Rules — Validation Matrix

| ID | Regla | Verificación | Violación |
|----|-------|-------------|-----------|
| RN-DI01 | Primera dirección del usuario se marca `es_principal=true` automáticamente | Service: `count_by_user(user_id) == 0` antes de crear | — (no hay violación, es automático) |
| RN-DI02 | Solo una dirección predeterminada por usuario a la vez | Transacción atómica en PATCH + índice único parcial `(user_id) WHERE es_principal=true` a nivel DB | 409 Conflict si el índice único parcial detecta duplicado (race condition) |
| RN-DI03 | Cliente solo ve/edita/elimina sus propias direcciones | Endpoints filtrar por `direccion.usuario_id == jwt.userId` | 404 (no revelar existencia de dirección ajena) |

---

## 4. Error Scenarios

| HTTP | Condición | Formato (RFC 7807) |
|------|-----------|-------------------|
| 401 | Token faltante, inválido o expirado | `{ status: 401, code: "UNAUTHORIZED", detail: "..." }` |
| 403 | Token válido pero rol insuficiente (ej: ADMIN requerido) | `{ status: 403, code: "FORBIDDEN", detail: "..." }` |
| 404 | Dirección no existe, no pertenece al usuario, o soft-deleted | `{ status: 404, code: "NOT_FOUND", detail: "Dirección no encontrada" }` |
| 409 | Violación de unicidad de predeterminada (race condition) | `{ status: 409, code: "CONFLICT", detail: "Ya existe una dirección predeterminada" }` |
| 422 | Error de validación de campos (linea1 vacío, alias > 50, linea1 > 500) | `{ status: 422, code: "VALIDATION_ERROR", detail: [...], fields: [...] }` |

---

## 5. Edge Cases

| # | Caso | Comportamiento Esperado |
|---|------|------------------------|
| EC-01 | **Race condition**: dos requests PATCH simultáneos intentan establecer diferente predeterminada | La transacción atómica + el índice único parcial `(user_id) WHERE es_principal = true` garantizan integridad. Un request falla con 409, se captura `IntegrityError` y se retorna 409 Conflict. |
| EC-02 | **Eliminar predeterminada cuando hay otras direcciones** | El service SHALL asignar `es_principal=true` a la dirección activa más reciente (mayor `created_at`). |
| EC-03 | **Eliminar única dirección (que es predeterminada)** | El service SHALL permitirlo. El usuario queda sin direcciones. No hay predeterminada que reasignar. |
| EC-04 | **Alias con solo whitespace** | El service MUST trimear whitespace. Si después del trim queda vacío, MUST tratar como `null`. |
| EC-05 | **linea1 con solo whitespace** | El service MUST trimear whitespace. Si después del trim queda vacío, MUST rechazar con 422. |
| EC-06 | **Usuario ADMIN accediendo a direcciones de otro usuario** | El ownership filter se aplica igual: ADMIN MUST ver solo sus propias direcciones (por ahora). No hay endpoint de administración global de direcciones en este cambio. |
| EC-07 | **Crear dirección con alias que excede 50 caracteres después de trim** | La validación SHALL hacerse después del trim. Si excede, 422. |
| EC-08 | **PATCH /predeterminada sobre dirección recién eliminada** | La validación de `deleted_at` MUST ejecutarse antes de la transacción. Si soft-deleted, 404. |
| EC-09 | **Listar con skip mayor al total de direcciones** | `items = []`, `total` refleja el conteo real sin paginación. |
| EC-10 | **PUT con body vacío `{}`** | MUST responder 422 (no hay campos para actualizar, o se trata como no-op si el service lo permite — debe definirse en implementación). Por claridad: el service SHOULD rechazar un update sin campos con 422. |

---

## 6. Delta Specs — Capabilities Modificadas

### 6.1 Delta: auth-rbac

**Capability**: `rbac-authorization`

#### ADDED Requirements

##### Requirement: Nuevos endpoints protegidos por RBAC

El sistema MUST aplicar `require_role(["CLIENT", "ADMIN"])` en los 5 endpoints del módulo `direcciones`.

| ID | Req | Source |
|----|-----|--------|
| REQ-RBAC-09 | MUST aplicar `require_role(["CLIENT", "ADMIN"])` en POST/GET/PUT/DELETE /api/v1/direcciones/* | CHANGE-05 |
| REQ-RBAC-10 | MUST aplicar `require_role(["CLIENT", "ADMIN"])` en PATCH /api/v1/direcciones/{id}/predeterminada | CHANGE-05 |

#### Scenario: Cliente accede a sus direcciones
- **Given** usuario con rol CLIENT y JWT válido
- **When** GET `/api/v1/direcciones`
- **Then** respuesta 200

#### Scenario: Admin accede a sus propias direcciones
- **Given** usuario con rol ADMIN y JWT válido
- **When** GET `/api/v1/direcciones`
- **Then** respuesta 200 (solo sus propias direcciones, mismo ownership)

### 6.2 Delta: uow-pattern

**Capability**: UnitOfWork exposes multiple repositories

#### ADDED Requirements

##### Requirement: UnitOfWork expone DireccionRepository

El sistema SHALL agregar `uow.direcciones` como property que retorna `DireccionRepository`.

#### Scenario: Acceso a direcciones via UoW
- **WHEN** código accede a `uow.direcciones`
- **THEN** retorna instancia de `DireccionRepository` dentro del contexto transaccional actual

---

## 7. Dependencias con Otras Capabilities

| Capability | Relación | Detalle |
|------------|----------|---------|
| `auth-jwt-rbac` | Dependencia fuerte | Los 5 endpoints requieren `get_current_user` + `require_role` |
| `uow-pattern` | Dependencia fuerte | Los services usan UoW para transacciones atómicas (PATCH, DELETE con reasignación) |
| `ingredient-crud-basic` | Inspiración patrón | Misma estructura feature-first: schemas → service → router |
