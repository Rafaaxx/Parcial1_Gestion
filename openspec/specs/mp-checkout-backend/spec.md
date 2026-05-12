# mp-checkout-backend Specification

## Purpose

Backend module for MercadoPago Checkout integration. Handles payment creation, idempotency, and status tracking for Food Store orders.

## Requirements

### Requirement: Crear Pago — Create Payment via MP API

El sistema SHALL crear pagos en MercadoPago usando el SDK oficial, generando un mp_payment_id único y gestionando idempotency para evitar cobros duplicados.

#### Scenario: Crear pago exitoso
- **GIVEN** pedido existe con estado_codigo=PENDIENTE, forma_pago=MERCADO_PAGO
- **WHEN** POST /api/v1/pagos/crear con pedido_id válido
- **THEN** responde 201 + { mp_payment_id, status: "pending", init_point }
- **AND** Pago existe en BD con estado="pending"
- **AND** idempotency_key se genera como UUID único

#### Scenario: Idempotency key evita duplicado
- **GIVEN** request previo con mismo pedido_id e idempotency_key
- **WHEN** POST /api/v1/pagos/crear con mismos datos
- **THEN** responde 200 (no 201) + mp_payment_id del request original
- **AND** NO nuevo pago se crea en BD

#### Scenario: Pedido no encontrado genera 404
- **GIVEN** pedido_id no existe
- **WHEN** POST /api/v1/pagos/crear
- **THEN** responde 404 con mensaje "Pedido no encontrado"

#### Scenario: Pedido no pertenece al usuario genera 403
- **GIVEN** pedido existe pero pertenece a otro usuario
- **WHEN** POST /api/v1/pagos/crear
- **THEN** responde 403 (no 404, no revelar existencia)

#### Scenario: Pedido no está en estado PENDIENTE
- **GIVEN** pedido con estado_codigo=CONFIRMADO
- **WHEN** POST /api/v1/pagos/crear
- **THEN** responde 422 con mensaje "El pedido no está en estado pendiente"

### Requirement: Consultar Pago — Get Payment Status

El sistema SHALL consultar el estado de un pago, validando que el usuario sea propietario del pedido relacionado.

#### Scenario: Consultar pago exitoso
- **GIVEN** pago existe asociado a pedido del usuario
- **WHEN** GET /api/v1/pagos/{pedido_id}
- **THEN** responde 200 + { mp_payment_id, status, status_detail, estado_codigo }

#### Scenario: Pago no existe para el pedido
- **GIVEN** pedido existe pero no tiene pago asociado
- **WHEN** GET /api/v1/pagos/{pedido_id}
- **THEN** responde 404 con mensaje "Pago no encontrado para este pedido"

### Requirement: Modelo de Datos — Pago Entity

El sistema SHALL almacenar información del pago en la tabla Pago con los campos requeridos por el dominio.

#### Scenario: Tabla Pago tiene campos requeridos
- **GIVEN** migración Alembic ejecutada
- **WHEN** consultar schema de tabla Pago
- **THEN** existe columna id (PK), pedido_id (FK), mp_payment_id, estado (pending/approved/rejected/cancelled), idempotency_key, external_reference, created_at, updated_at

### Requirement: SDK Integration — Abstraer MercadoPago

El sistema SHALL usar el SDK mercadopago>=2.3.0 con adapter pattern para permitir cambios futuros sin impactar el código de negocio.

#### Scenario: Service usa adapter para MP
- **GIVEN** MPService implementado con adapter
- **WHEN** cambiar de sandbox a producción
- **THEN** solo cambia config de ACCESS_TOKEN, código de negocio no cambia