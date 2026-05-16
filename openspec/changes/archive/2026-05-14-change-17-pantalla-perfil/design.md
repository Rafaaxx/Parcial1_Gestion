# CHANGE-17: Diseño Técnico — Pantalla de Perfil del Cliente

## Endpoints

### GET /api/v1/perfil
Obtiene el perfil completo del usuario autenticado.

**Response** (200):
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan@example.com",
  "telefono": "+541112345678",
  "roles": ["CLIENT"],
  "fecha_registro": "2026-04-21T10:00:00Z"
}
```

**Auth**: Bearer token (cualquier rol activo)

### PUT /api/v1/perfil
Actualiza nombre, apellido y/o teléfono del usuario autenticado.

**Request**:
```json
{
  "nombre": "Juan Carlos",
  "apellido": "Pérez García",
  "telefono": "+5491112345678"
}
```
Todos los campos son opcionales. Al menos uno debe ser enviado.

**Response** (200): Mismo schema que GET.

**Validaciones**:
- `nombre`: min 2, max 100 caracteres
- `apellido`: min 2, max 100 caracteres
- `telefono`: max 20 caracteres, opcional
- Al menos un campo para actualizar → 422 si vacío
- Email NO se puede cambiar (es identificador)

**Auth**: Bearer token (CLIENT, ADMIN)

### PUT /api/v1/perfil/password
Cambia la contraseña del usuario autenticado.

**Request**:
```json
{
  "password_actual": "MiViejaPass123",
  "password_nueva": "MiNuevaPass456"
}
```

**Response** (200):
```json
{
  "message": "Contraseña actualizada exitosamente",
  "requires_relogin": true
}
```

**Validaciones**:
- `password_actual`: debe coincidir con la almacenada (bcrypt compare)
- `password_nueva`: min 8 caracteres
- Si password_actual es incorrecta → 401
- Al cambiar: se revocan TODOS los refresh tokens del usuario (forzar re-login)

## Arquitectura

### Backend — Módulo `perfil`
```
backend/app/modules/perfil/
├── __init__.py
├── schemas.py      → PerfilRead, PerfilUpdate, PasswordChange, PerfilResponse
├── service.py      → PerfilService (get_profile, update_profile, change_password)
└── router.py       → 3 endpoints
```

Dependency injection: usa `get_current_user` y `get_uow` existentes.
AuthRepository se reusa para `find_with_roles`.
RefreshTokenRepository se reusa para `revoke_all_for_user`.

### Frontend — Feature `perfil`
```
frontend/src/features/perfil/
├── api.ts          → getPerfil(), updatePerfil(), changePassword()
├── hooks.ts        → usePerfil(), useUpdatePerfil(), useChangePassword()
└── types.ts        → PerfilData, PerfilUpdate, PasswordChange
```

### Frontend — Página
`ProfilePage.tsx` (ya existe como placeholder, se reescribe):
- Sección "Mis Datos": muestra datos, botón "Editar" que activa formulario inline
- Sección "Cambiar Contraseña": formulario con password_actual y password_nueva
- Sección "Mis Direcciones": lista direcciones existentes (integra con CHANGE-05)
