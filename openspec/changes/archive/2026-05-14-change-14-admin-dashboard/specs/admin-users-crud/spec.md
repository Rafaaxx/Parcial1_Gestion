## ADDED Requirements

### Requirement: Listar usuarios con paginación y filtros

El sistema SHALL exponer `GET /api/v1/admin/usuarios` para listar usuarios del sistema.

- **Autenticación**: Requiere rol ADMIN
- **Query params**: `skip` (default 0), `limit` (default 20, max 100), `busqueda` (filtro ILIKE por nombre o email), `rol` (filtro por ID de rol), `activo` (filtro booleano)
- **Respuesta**: `{ items: UsuarioAdmin[], total: number, skip: number, limit: number }`
- **UsuarioAdmin**: id, nombre, email, roles (array de nombres), activo, creado_en, ultimo_login

#### Scenario: Admin lista usuarios sin filtros

- **WHEN** un Admin hace GET a `/api/v1/admin/usuarios?skip=0&limit=20`
- **THEN** el sistema retorna 200 con los primeros 20 usuarios y el total de registros

#### Scenario: Admin busca usuario por email

- **WHEN** un Admin hace GET a `/api/v1/admin/usuarios?busqueda=juan@example.com`
- **THEN** el sistema retorna 200 con los usuarios cuyo email coincide (ILIKE) con el término

#### Scenario: Admin filtra por rol

- **WHEN** un Admin hace GET a `/api/v1/admin/usuarios?rol=1`
- **THEN** el sistema retorna 200 solo con usuarios que tienen el rol ADMIN

---

### Requirement: Editar usuario

El sistema SHALL exponer `PUT /api/v1/admin/usuarios/{id}` para modificar datos y roles de un usuario.

- **Body**: `{ nombre?: string, email?: string, roles_ids?: int[] }`
- **Respuesta**: UsuarioAdmin actualizado
- **Validación**: 
  - No se permite degradar al último ADMIN del sistema (si se intenta remover rol ADMIN del único admin, retorna 409 Conflict)
  - Si se cambia el rol, se invalidan TODOS los refresh tokens del usuario (debe re-login)

#### Scenario: Admin actualiza roles de usuario

- **WHEN** un Admin hace PUT a `/api/v1/admin/usuarios/5` con body `{ roles_ids: [1, 4] }`
- **THEN** el sistema retorna 200 y el usuario 5 ahora tiene roles ADMIN y CLIENT

#### Scenario: Admin intenta remover único ADMIN del sistema

- **WHEN** un Admin hace PUT a `/api/v1/admin/usuarios/1` removiendo el rol ADMIN y es el único admin
- **THEN** el sistema retorna 409 Conflict con mensaje "No se puede remover el último administrador del sistema"

#### Scenario: Usuario modificado debe re-login

- **WHEN** un Admin modifica los roles de un usuario
- **THEN** los refresh tokens activos de ese usuario se revocan inmediatamente

---

### Requirement: Activar/Desactivar usuario

El sistema SHALL exponer `PATCH /api/v1/admin/usuarios/{id}/estado` para activar o desactivar un usuario.

- **Body**: `{ activo: boolean }`
- **Validación**: Al desactivar, se invalidan todos los refresh tokens del usuario
- **Validación**: No se puede desactivar al propio Admin autenticado (retorna 409)

#### Scenario: Admin desactiva usuario

- **WHEN** un Admin hace PATCH a `/api/v1/admin/usuarios/5/estado` con body `{ activo: false }`
- **THEN** el sistema retorna 200, el usuario 5 queda desactivado y sus tokens revocados

#### Scenario: Usuario desactivado no puede loguearse

- **WHEN** un usuario con activo=false intenta login con credenciales válidas
- **THEN** el sistema retorna 403 Forbidden con mensaje "Cuenta desactivada"

#### Scenario: Admin no puede desactivarse a sí mismo

- **WHEN** un Admin hace PATCH a su propio ID con `{ activo: false }`
- **THEN** el sistema retorna 409 Conflict
