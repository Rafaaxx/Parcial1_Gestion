## MODIFIED Requirements

### Requirement: Verificación de roles en endpoints protegidos

El sistema SHALL permitir que un usuario con rol ADMIN acceda a cualquier endpoint protegido por los roles STOCK o PEDIDOS.

- **Comportamiento actual**: El middleware `requires_roles(['ADMIN', 'STOCK'])` verifica que el usuario tenga AL MENOS UNO de los roles listados.
- **Comportamiento modificado**: Se añade lógica implícita: si el usuario tiene rol ADMIN, se concede acceso automáticamente SIN IMPORTAR qué roles exige el endpoint.
- **No breaking**: Los endpoints existentes no cambian su declaración de roles.

#### Scenario: Admin accede a endpoint de catálogo

- **WHEN** un Admin hace GET a `/api/v1/productos` (endpoint marcado con `@Roles('ADMIN', 'STOCK')`)
- **THEN** el sistema concede acceso aunque el Admin no tenga rol STOCK

#### Scenario: Admin accede a endpoint de pedidos

- **WHEN** un Admin hace GET a `/api/v1/pedidos` (endpoint marcado con `@Roles('ADMIN', 'PEDIDOS')`)
- **THEN** el sistema concede acceso aunque el Admin no tenga rol PEDIDOS

#### Scenario: STOCK no accede a endpoint de pedidos

- **WHEN** un usuario con rol STOCK hace GET a `/api/v1/pedidos`
- **THEN** el sistema retorna 403 Forbidden (comportamiento existente, no modificado)

---

## ADDED Requirements

### Requirement: Página de gestión de usuarios

El frontend SHALL agregar la ruta `/admin/usuarios` al menú de navegación del ADMIN y al sidebar.

- **Sidebar**: Nuevo ítem "Usuarios" visible solo para rol ADMIN
- **Enlace**: Apunta a `/admin/usuarios`

#### Scenario: Admin ve enlace a usuarios en sidebar

- **WHEN** un Admin autenticado ve el sidebar
- **THEN** ve el ítem "Usuarios" con icono y enlace a `/admin/usuarios`

#### Scenario: STOCK no ve enlace a usuarios

- **WHEN** un usuario con rol STOCK ve el sidebar
- **THEN** NO ve el ítem "Usuarios"
