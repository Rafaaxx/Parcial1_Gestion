## ADDED Requirements

### Requirement: Tests de integración con SQLite in-memory

El sistema SHALL usar SQLite in-memory para ejecutar tests de integración sin necesidad de PostgreSQL.

#### Scenario: Setup de base de datos en memoria
- **GIVEN** pytest configurado con SQLite in-memory
- **WHEN** un test necesita acceso a base de datos
- **THEN** debe crear una base de datos efímera para ese test

#### Scenario: Migraciones aplicadas en tests
- **GIVEN** la configuración de Alembic para tests
- **WHEN** se ejecutan los tests
- **THEN** debe aplicar las migraciones automáticamente (fixture autouse)

### Requirement: Endpoint POST /api/v1/auth/register debe pasar tests de integración

El sistema SHALL tener tests de integración que verifiquen el endpoint de registro.

#### Scenario: Registro exitoso retorna 201
- **GIVEN** payload válido de registro
- **WHEN** se hace POST a /api/v1/auth/register
- **THEN** debe retornar 201 con tokens de acceso y refresh

#### Scenario: Registro con email duplicado retorna 409
- **GIVEN** un email que ya existe
- **WHEN** se hace POST a /api/v1/auth/register
- **THEN** debe retornar 409 Conflict

#### Scenario: Registro con datos inválidos retorna 422
- **GIVEN** payload con datos faltantes o inválidos
- **WHEN** se hace POST a /api/v1/auth/register
- **THEN** debe retornar 422 con errores de validación

### Requirement: Endpoint POST /api/v1/auth/login debe pasar tests de integración

El sistema SHALL tener tests de integración para el endpoint de login.

#### Scenario: Login exitoso retorna 200
- **GIVEN** credenciales válidas
- **WHEN** se hace POST a /api/v1/auth/login
- **THEN** debe retornar 200 con tokens

#### Scenario: Login con credenciales inválidas retorna 401
- **GIVEN** email o password incorrectos
- **WHEN** se hace POST a /api/v1/auth/login
- **THEN** debe retornar 401 Unauthorized

### Requirement: Creación de pedidos (UoW) debe pasar tests de integración

El sistema SHALL tener tests de integración que verifiquen el Unit of Work para crear pedidos.

#### Scenario: Pedido creado exitosamente
- **GIVEN** un usuario autenticado, items en carrito, dirección válida
- **WHEN** se hace POST a /api/v1/pedidos
- **THEN** debe crear el pedido, crear los detalles, y retornar 201

#### Scenario: Pedido con stock insuficiente hace rollback
- **GIVEN** un producto con stock 0
- **WHEN** se intenta crear un pedido con ese producto
- **THEN** debe hacer rollback completo y retornar 400

#### Scenario: Pedido con dirección inválida retorna 403
- **GIVEN** una dirección que no pertenece al usuario
- **WHEN** se intenta crear un pedido
- **THEN** debe retornar 403 Forbidden

### Requirement: Máquina de Estados (FSM) debe pasar tests de integración

El sistema SHALL tener tests de integración para las transiciones de estado de pedidos.

#### Scenario: Transición PENDIENTE → CONFIRMADO
- **GIVEN** un pedido en estado PENDIENTE
- **WHEN** se envía transición a CONFIRMADO
- **THEN** debe actualizar el estado y decrementar stock

#### Scenario: Transición inválida es rechazada
- **GIVEN** un pedido en estado PENDIENTE
- **WHEN** se intenta transicionar a ENTREGADO (no válido desde PENDIENTE)
- **THEN** debe retornar 400 con error indicando transición no permitida

#### Scenario: Transición desde estado terminal es rechazada
- **GIVEN** un pedido en estado ENTREGADO (terminal)
- **WHEN** se intenta transicionar a cualquier estado
- **THEN** debe retornar 400 indicando que no hay transiciones disponibles

### Requirement: Webhook MercadoPago debe pasar tests de integración

El sistema SHALL tener tests de integración para el webhook de MercadoPago.

#### Scenario: Webhook con pago aprobado transiciona pedido
- **GIVEN** un pedido en estado PENDIENTE y un webhook de pago aprobado
- **WHEN** se recibe POST en /api/v1/pagos/webhook
- **THEN** debe actualizar el pago y transicionar el pedido a CONFIRMADO

#### Scenario: Webhook con firma inválida retorna 401
- **GIVEN** un webhook con X-Signature incorrecta
- **WHEN** se recibe POST en /api/v1/pagos/webhook
- **THEN** debe retornar 401 Unauthorized

#### Scenario: Webhook duplicado no procesa dos veces
- **GIVEN** el mismo webhook recibido dos veces
- **WHEN** se recibe el segundo webhook
- **THEN** debe retornar 200 pero no procesar (idempotency)