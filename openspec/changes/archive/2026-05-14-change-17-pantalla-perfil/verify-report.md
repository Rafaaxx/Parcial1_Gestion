# Verification Report — CHANGE-17: Pantalla de Perfil del Cliente

**Change**: change-17-pantalla-perfil
**Version**: N/A (no spec.md — proposal.md serves as spec)
**Mode**: Standard (NOT Strict TDD)
**Date**: 2026-05-14

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 12 |
| Tasks complete | 7 |
| Tasks incomplete | 5 |

### Tasks Status

| # | Task | Status |
|---|------|--------|
| 1.1 | Crear `backend/app/modules/perfil/` con `__init__.py` | ✅ |
| 1.2 | Crear `backend/app/modules/perfil/schemas.py` | ✅ |
| 1.3 | Crear `backend/app/modules/perfil/service.py` | ✅ |
| 1.4 | Crear `backend/app/modules/perfil/router.py` | ✅ |
| 1.5 | Registrar router en `backend/app/main.py` | ✅ |
| 2.1 | Crear `backend/tests/integration/test_perfil_api.py` | ✅ |
| 3.1 | Crear `frontend/src/features/perfil/types.ts` | ❌ No existe el directorio `features/perfil/` |
| 3.2 | Crear `frontend/src/features/perfil/api.ts` | ❌ No existe |
| 3.3 | Crear `frontend/src/features/perfil/hooks.ts` | ❌ No existe |
| 4.1 | Reescribir `frontend/src/pages/ProfilePage.tsx` | ❌ Sigue siendo el placeholder "Próximamente" |
| 5.1 | Ejecutar tests de backend | ✅ 14/14 passed |
| 5.2 | Verificar cobertura de US-061, US-062, US-063 | ✅ Se verifica en este reporte |

> **⚠️ WARNING**: Phases 3-4 (Frontend: feature + página) están completamente sin implementar. Solo el backend (Phases 1-2) está completo.

---

## Build & Tests Execution

**Build**: ➖ No aplica (backend Python/FastAPI sin step de build, no hay `pyproject.toml` con build config ni type checker configurado explícitamente para este módulo)

**Tests**: ✅ **14 passed** / ❌ **0 failed** / ⚠️ **0 skipped**

```
tests/integration/test_perfil_api.py::TestGetPerfil::test_get_perfil_success PASSED
tests/integration/test_perfil_api.py::TestGetPerfil::test_get_perfil_no_auth PASSED
tests/integration/test_perfil_api.py::TestGetPerfil::test_get_perfil_wrong_token PASSED
tests/integration/test_perfil_api.py::TestUpdatePerfil::test_update_nombre PASSED
tests/integration/test_perfil_api.py::TestUpdatePerfil::test_update_telefono PASSED
tests/integration/test_perfil_api.py::TestUpdatePerfil::test_update_multiple_fields PASSED
tests/integration/test_perfil_api.py::TestUpdatePerfil::test_update_no_fields PASSED
tests/integration/test_perfil_api.py::TestUpdatePerfil::test_update_no_auth PASSED
tests/integration/test_perfil_api.py::TestUpdatePerfil::test_email_not_changeable PASSED
tests/integration/test_perfil_api.py::TestChangePassword::test_change_password_success PASSED
tests/integration/test_perfil_api.py::TestChangePassword::test_change_password_wrong_actual PASSED
tests/integration/test_perfil_api.py::TestChangePassword::test_change_password_short_new PASSED
tests/integration/test_perfil_api.py::TestChangePassword::test_change_password_revokes_tokens PASSED
tests/integration/test_perfil_api.py::TestChangePassword::test_change_password_no_auth PASSED
```

**Coverage**: ➖ No disponible (no se ejecutó cobertura; no hay herramienta configurada explícitamente en `rules.verify` de `openspec/config.yaml`)

---

## Spec Compliance Matrix

Fuente: `proposal.md` — US-061, US-062, US-063 (no hay `spec.md` separado).

| User Story | Escenario | Test | Resultado |
|-----------|-----------|------|-----------|
| **US-061**: Ver perfil propio | Cliente autenticado obtiene nombre, email, teléfono, fecha de registro | `test_perfil_api.py::TestGetPerfil::test_get_perfil_success` | ✅ COMPLIANT |
| **US-061**: Ver perfil propio | No autenticado → 403 | `test_perfil_api.py::TestGetPerfil::test_get_perfil_no_auth` | ✅ COMPLIANT |
| **US-061**: Ver perfil propio | Token inválido → 401 | `test_perfil_api.py::TestGetPerfil::test_get_perfil_wrong_token` | ✅ COMPLIANT |
| **US-062**: Editar perfil | Modificar nombre | `test_perfil_api.py::TestUpdatePerfil::test_update_nombre` | ✅ COMPLIANT |
| **US-062**: Editar perfil | Modificar teléfono | `test_perfil_api.py::TestUpdatePerfil::test_update_telefono` | ✅ COMPLIANT |
| **US-062**: Editar perfil | Modificar múltiples campos | `test_perfil_api.py::TestUpdatePerfil::test_update_multiple_fields` | ✅ COMPLIANT |
| **US-062**: Editar perfil | Body vacío → 422 | `test_perfil_api.py::TestUpdatePerfil::test_update_no_fields` | ✅ COMPLIANT |
| **US-062**: Editar perfil | No autenticado → 403 | `test_perfil_api.py::TestUpdatePerfil::test_update_no_auth` | ✅ COMPLIANT |
| **US-062**: Editar perfil | Email inmutable (no cambia) | `test_perfil_api.py::TestUpdatePerfil::test_email_not_changeable` | ✅ COMPLIANT |
| **US-063**: Cambiar contraseña | Contraseña actual correcta → cambios persistidos | `test_perfil_api.py::TestChangePassword::test_change_password_success` | ✅ COMPLIANT |
| **US-063**: Cambiar contraseña | Contraseña actual incorrecta → 401 | `test_perfil_api.py::TestChangePassword::test_change_password_wrong_actual` | ✅ COMPLIANT |
| **US-063**: Cambiar contraseña | Nueva contraseña corta (< 8) → 422 | `test_perfil_api.py::TestChangePassword::test_change_password_short_new` | ✅ COMPLIANT |
| **US-063**: Cambiar contraseña | Revocación de todos los refresh tokens | `test_perfil_api.py::TestChangePassword::test_change_password_revokes_tokens` | ✅ COMPLIANT |
| **US-063**: Cambiar contraseña | No autenticado → 403 | `test_perfil_api.py::TestChangePassword::test_change_password_no_auth` | ✅ COMPLIANT |

**Compliance summary**: **14/14 escenarios compliant** (backend). Frontend no implementado.

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| **US-061**: GET /api/v1/perfil retorna datos personales | ✅ Implementado | `router.py` → `PerfilService.get_profile()` → `auth_repo.find_with_roles()`. Response incluye id, nombre, apellido, email, telefono, roles, fecha_registro |
| **US-062**: PUT /api/v1/perfil edita nombre/teléfono | ✅ Implementado | `router.py` → `PerfilService.update_profile()`. Solo actualiza campos enviados. `model_dump(exclude_none=True)` + validación de al menos un campo |
| **US-062**: Email inmutable | ✅ Implementado | Email nunca se incluye como campo editable. No hay manera de modificarlo vía API |
| **US-063**: PUT /api/v1/perfil/password | ✅ Implementado | `router.py` → `PerfilService.change_password()`. Verifica con bcrypt, hashea nueva, revoca tokens |
| **US-063**: Revocación de tokens | ✅ Implementado | `refresh_repo.revoke_all_for_user(usuario.id)` en `service.py` línea 149 |
| Response indica re-login requerido | ✅ Implementado | `PasswordChangeResponse` con `requires_relogin: true` |
| Roles en perfil | ✅ Implementado | Se obtienen de `usuario.usuario_roles` y se mapean a `roles: list[str]` |

---

## Coherence (Design)

| Decision | Seguido? | Notes |
|----------|----------|-------|
| Módulo `backend/app/modules/perfil/` con 4 archivos | ✅ Sí | `__init__.py`, `schemas.py`, `service.py`, `router.py` — estructura exacta |
| 3 endpoints: GET, PUT, PUT/password | ✅ Sí | Coinciden con diseño |
| Schemas: PerfilRead, PerfilUpdate, PasswordChange | ✅ Sí | Adicionalmente tiene `PasswordChangeResponse` (no mencionado en diseño pero necesario) |
| Dependency injection: get_current_user + get_uow | ✅ Sí | Ambos usados consistentemente |
| AuthRepository reusado para find_with_roles | ✅ Sí | Usado en `get_profile()` y `update_profile()` |
| RefreshTokenRepository reusado para revoke_all_for_user | ✅ Sí | Usado en `change_password()` |
| PUT /perfil: todos los campos opcionales, al menos uno | ✅ Sí | `update_dict = data.model_dump(exclude_none=True)` + raise ValidationError si vacío |
| PUT /perfil: nombre min 2 max 100 | ✅ Sí | `Field(min_length=2, max_length=100)` en schema |
| PUT /perfil: apellido min 2 max 100 | ✅ Sí | `Field(min_length=2, max_length=100)` en schema |
| PUT /perfil: telefono max 20 | ✅ Sí | `Field(max_length=20)` en schema |
| PUT /perfil/password: password_nueva min 8 | ✅ Sí | `Field(min_length=8)` en schema |
| PUT /perfil/password: actual incorrecta → 401 | ✅ Sí | `raise UnauthorizedError` en service, mapeado a 401 en router |
| Frontend feature en `frontend/src/features/perfil/` | ❌ No implementado | No existe el directorio |
| ProfilePage.tsx reescrita con secciones | ❌ No implementado | Sigue siendo el placeholder |
| Frontend: integración con CHANGE-05 (direcciones) | ❌ No implementado | No existe el frontend |

---

## Issues Found

### CRITICAL (must fix before archive)
- **Frontend Phases 3-4 no implementados**: `frontend/src/features/perfil/` no existe, `ProfilePage.tsx` sigue siendo el placeholder "Próximamente". Si el alcance de CHANGE-17 incluye frontend, esto debe completarse antes de archivar.

### WARNING (should fix)
- **Design.md menciona schema `PerfilResponse`** que no existe en el código. La implementación usa `PasswordChangeResponse` que es más específico y correcto. Esto es una mejora sobre el diseño, no un error.

### SUGGESTION (nice to have)
- Los schemas del perfil (PerfilRead) usan `model_config = {"from_attributes": True}` (Pydantic v2 style) correctamente.
- El naming de `fecha_registro` en la API (español) vs `created_at` en el modelo (inglés) se mapea correctamente en el service.

---

## Verdict

### PASS WITH WARNINGS

**Backend**: ✅ **Completo y verificado**. Los 3 endpoints (GET/PUT /perfil, PUT /perfil/password) están implementados, registrados en main.py, y los 14 tests de integración pasan exitosamente. Todas las validaciones del diseño se cumplen: email inmutable, revocación de tokens, mínimo 8 caracteres en password, etc.

**Frontend**: ❌ **No implementado**. Phases 3-4 están completamente pendientes. Si el alcance del change incluye frontend, esto debe abordarse antes del archive. Si el change se limita al backend, el backend está listo.

**Decisión recomendada**: Backend listo para archivar si el alcance acepta backend-only, o continuar con frontend antes del archive.
