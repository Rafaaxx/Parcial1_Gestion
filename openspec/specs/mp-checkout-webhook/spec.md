# mp-checkout-webhook Specification

## Purpose

Webhook endpoint for receiving IPN (Instant Payment Notification) from MercadoPago. Processes async notifications and updates payment/pedido status accordingly.

## Requirements

### Requirement: Webhook Endpoint — Receive IPN

El sistema SHALL exponer endpoint público POST /api/v1/pagos/webhook que procese notificaciones de MercadoPago y responda inmediatamente para evitar timeout.

#### Scenario: Webhook recibe notificación de pago aprobado
- **GIVEN** MP envía POST con topic="payment" y data.id válido
- **WHEN** POST /api/v1/pagos/webhook
- **THEN** responde 200 OK inmediatamente (async processing)
- **AND** status de Pago en BD se actualiza a "approved"
- **AND** pedido transiciona PENDIENTE → CONFIRMADO

#### Scenario: Webhook recibe notificación de pago rechazado
- **GIVEN** MP envía notification con payment.status="rejected"
- **WHEN** POST /api/v1/pagos/webhook
- **THEN** responde 200 OK
- **AND** Pago.estado="rejected"
- **AND** pedido NO transiciona (queda PENDIENTE o CANCELADO por timeout)

#### Scenario: Webhook recibe notificación de pago cancelado
- **GIVEN** MP envía notification con payment.status="cancelled"
- **WHEN** POST /api/v1/pagos/webhook
- **THEN** responde 200 OK
- **AND** Pago.estado="cancelled"

### Requirement: Seguridad Webhook — Validar Topic

El sistema SHALL validar que el topic sea "payment" antes de procesar, ignorando otros tipos de notificaciones.

#### Scenario: Topic inválido se ignora
- **GIVEN** POST /api/v1/pagos/webhook con topic="merchant_order"
- **WHEN** procesa request
- **THEN** responde 200 OK pero NO actualiza ningún registro

### Requirement: Idempotency Webhook — Evitar Duplicados

El sistema SHALL validar idempotency_key antes de procesar el webhook para evitar actualizaciones duplicadas por retry de MP.

#### Scenario: Webhook duplicado se ignora
- **GIVEN** mismo idempotency_key procesado anteriormente
- **WHEN** POST /api/v1/pagos/webhook con topic="payment"
- **THEN** responde 200 OK
- **AND** NO se procesa (ya fue procesado previamente)

#### Scenario: Nueva notificación se procesa
- **GIVEN** notification con idempotency_key nuevo
- **WHEN** POST /api/v1/pagos/webhook
- **THEN** procesa y actualiza estado en BD

### Requirement: Validar Estado Real — No Confiar en Webhook Solo

El sistema SHALL consultar la API de MercadoPago para confirmar el estado real del pago, nunca confiando solo en los datos del webhook.

#### Scenario: Confirmar estado con API MP
- **GIVEN** webhook recibe notification con payment.id
- **WHEN** procesar notificación
- **THEN** consulta GET /v1/payments/{id} a API de MP
- **AND** usa ese status para actualizar BD (no el del webhook)

### Requirement: Transición FSM — Pedido tras Pago Aprobado

El sistema SHALL transicionar el pedido automáticamente de PENDIENTE a CONFIRMADO cuando el pago se marque como approved.

#### Scenario: Pago aprobado transiciona pedido
- **GIVEN** pedido con estado_codigo=PENDIENTE, pago con estado="pending"
- **WHEN** webhook procesa payment.status="approved"
- **THEN** Pedido.transicionar("CONFIRMADO") se ejecuta
- **AND** HistorialEstadoPedido registra transición

#### Scenario: Transición FSM falla no bloquea webhook
- **GIVEN** error al ejecutar transicion FSM
- **WHEN** webhook está procesando pago aprobado
- **THEN** responde 200 OK
- **AND** error se loggea para revisión manual
- **AND** pago se marca como approved aunque FSM falle