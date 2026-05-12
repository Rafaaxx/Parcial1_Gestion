# Delta Spec: Módulo Pagos (MercadoPago)

## ADDED Requirements

### Requirement: Crear Pago con MercadoPago

El sistema DEBE permitir crear un pago asociado a un pedido Pendiente mediante la API de MercadoPago. El backend DEBE generar un idempotency_key UUID único, enviar la preferencia de pago a MercadoPago, y registrar el pago en la tabla `Pago`.

#### Scenario: Crear pago exitosamente

- GIVEN un pedido en estado PENDIENTE con ID válido
- WHEN el cliente envía POST /api/v1/pagos/crear con token de tarjeta y pedido_id
- THEN se genera idempotency_key UUID único
- AND se crea preferencia en MercadoPago
- AND se registra pago en tabla Pago con status pending
- AND se retorna mp_payment_id y status al cliente

#### Scenario: Crear pago con pedido no existente

- GIVEN un pedido_id que no existe en el sistema
- WHEN el cliente envía POST /api/v1/pagos/crear
- THEN se retorna error 404 "Pedido no encontrado"

#### Scenario: Crear pago con pedido no Pendiente

- GIVEN un pedido que NO está en estado PENDIENTE
- WHEN el cliente envía POST /api/v1/pagos/crear
- THEN se retorna error 400 "El pedido no está en estado Pendiente"

### Requirement: Webhook IPN de MercadoPago

El sistema DEBE procesar las notificaciones IPN de MercadoPago de forma asíncrona. El endpoint DEBE validar la firma del webhook, consultar el estado real del pago en la API de MercadoPago (nunca confiar solo en datos del payload), actualizar el registro en la tabla Pago, y avanzar el pedido de PENDIENTE a CONFIRMADO si el pago es approved.

#### Scenario: Webhook con pago aprobado

- GIVEN MercadoPago envía notificación de payment approved
- WHEN POST /api/v1/pagos/webhook recibe la notificación
- THEN se valida firma del webhook
- AND se consulta API de MP para obtener estado real
- AND se actualiza registro en tabla Pago con status approved
- AND se transiciona el pedido de PENDIENTE a CONFIRMADO
- AND se responde HTTP 200 inmediatamente

#### Scenario: Webhook con pago rechazado

- GIVEN MercadoPago envía notificación de payment rejected
- WHEN POST /api/v1/pagos/webhook recibe la notificación
- THEN se valida firma del webhook
- AND se consulta API de MP para obtener estado real
- AND se actualiza registro en tabla Pago con status rejected
- AND el pedido permanece en estado PENDIENTE
- AND se responde HTTP 200 inmediatamente

#### Scenario: Webhook con pago pendiente

- GIVEN MercadoPago envía notificación de payment pending
- WHEN POST /api/v1/pagos/webhook recibe la notificación
- THEN se actualiza registro en tabla Pago con status pending
- AND el pedido permanece en estado PENDIENTE
- AND se responde HTTP 200 inmediatamente

### Requirement: Consultar Estado de Pago

El sistema DEBE permitir consultar el estado del pago asociado a un pedido. Solo el propietario del pedido o un administrador DEBE poder consultar el estado.

#### Scenario: Consultar pago como propietario

- GIVEN un usuario autenticado que es propietario del pedido
- WHEN GET /api/v1/pagos/{pedido_id}
- THEN se retorna el estado del pago con mp_status y mp_payment_id

#### Scenario: Consultar pago sin autorización

- GIVEN un usuario que NO es propietario del pedido
- WHEN GET /api/v1/pagos/{pedido_id}
- THEN se retorna error 403 "No autorizado"

### Requirement: Idempotency en Pagos

El sistema DEBE utilizar un idempotency_key para evitar cobros duplicados. Si se recibe una solicitud con el mismo idempotency_key, DEBE retornarse el resultado anterior sin crear un nuevo pago.

#### Scenario: Solicitud con idempotency_key duplicado

- GIVEN una solicitud con idempotency_key ya utilizado
- WHEN se envía POST /api/v1/pagos/crear
- THEN se retorna el pago existente sin crear uno nuevo
- AND se retorna HTTP 200 con el mp_payment_id existente

---

## MODIFIED Requirements

### Requirement: Transición Automática PENDIENTE → CONFIRMADO

(Previously: No existía integración con pagos)

Cuando el webhook de MercadoPago confirma un pago con status "approved", el sistema DEBE automáticamente transicionar el pedido de estado PENDIENTE a CONFIRMADO, y decrementar el stock de los productos asociados.

#### Scenario: Pago aprobado dispara transición automática

- GIVEN un pedido en estado PENDIENTE
- WHEN el webhook recibe payment approved
- THEN se actualiza el estado del pago a approved
- AND se transiciona el pedido a CONFIRMADO
- AND se decrementa el stock de cada producto en el pedido