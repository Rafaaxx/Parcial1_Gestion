# CHANGE-17: Pantalla de Perfil del Cliente

## ¿Qué?
Pantalla unificada de perfil para que el cliente pueda ver y editar sus datos personales, cambiar su contraseña, y gestionar sus direcciones de entrega desde un solo lugar.

## ¿Por qué?
Actualmente no hay forma para que un cliente vea o modifique sus datos personales una vez registrado. El perfil existe como placeholder "Próximamente". Se requiere:

- **US-061**: Visualización de datos personales (nombre, email, teléfono, fecha de registro)
- **US-062**: Edición de nombre y teléfono (email es inmutable)
- **US-063**: Cambio de contraseña con validación de la actual + invalidación de tokens

## Alcance

### Incluye
- Backend: 3 endpoints (`GET /api/v1/perfil`, `PUT /api/v1/perfil`, `PUT /api/v1/perfil/password`)
- Frontend: Pantalla de perfil completa con secciones de datos, contraseña y direcciones
- Tests de integración para los 3 endpoints

### No incluye
- Panel admin de perfiles (ya existe en admin/usuarios)
- Cambio de email (explícitamente prohibido por US-062)
- Roles (el perfil es solo CLIENT, aunque ADMIN también puede acceder)

## Dependencias
- CHANGE-01 (Auth): get_current_user, JWT, password hashing, refresh token revocation
- CHANGE-05 (Direcciones): CRUD de direcciones ya implementado y funcionando

## Riesgos
- Bajo: los 3 endpoints son simples CRUD de un solo registro (el usuario autenticado)
- Password change revoca todos los tokens → el usuario debe re-logearse
