# CHANGE-17: Tasks — Pantalla de Perfil del Cliente

## Fase 1: Backend — Infraestructura ✅

- [x] 1.1 Crear `backend/app/modules/perfil/` con `__init__.py`
- [x] 1.2 Crear `backend/app/modules/perfil/schemas.py` (PerfilRead, PerfilUpdate, PasswordChange)
- [x] 1.3 Crear `backend/app/modules/perfil/service.py` (PerfilService con get_profile, update_profile, change_password)
- [x] 1.4 Crear `backend/app/modules/perfil/router.py` (3 endpoints)
- [x] 1.5 Registrar router en `backend/app/main.py`

## Fase 2: Backend — Tests ✅

- [x] 2.1 Crear `backend/tests/integration/test_perfil_api.py`
      - 14 tests, todos pasando

## Fase 3: Frontend — Feature ✅

- [x] 3.1 Crear `frontend/src/features/perfil/types.ts`
      - PerfilData, PerfilUpdate, PasswordChange, PasswordChangeResponse
- [x] 3.2 Crear `frontend/src/features/perfil/api.ts`
      - getPerfil(), updatePerfil(), changePassword()
- [x] 3.3 Crear `frontend/src/features/perfil/hooks.ts`
      - usePerfil(), useUpdatePerfil(), useChangePassword()

## Fase 4: Frontend — Página ✅

- [x] 4.1 Reescribir `frontend/src/pages/ProfilePage.tsx`
      - Sección "Mis Datos": display + edición inline
      - Sección "Cambiar Contraseña": validación actual + nueva + re-login
      - Sección "Mis Direcciones": lista desde GET /api/v1/direcciones

## Fase 5: Verify ✅

- [x] 5.1 Ejecutar tests de backend
      - 14/14 tests pasando
- [x] 5.2 Verificar cobertura de US-061, US-062, US-063
      - 14/14 escenarios COMPLIANT
