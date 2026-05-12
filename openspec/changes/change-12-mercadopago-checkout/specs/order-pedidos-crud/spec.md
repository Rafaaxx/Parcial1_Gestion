# Delta for order-pedidos-crud

## ADDED Requirements

### Requirement: Transición Automática por Pago Aprobado

El sistema SHALL transicionar automáticamente el pedido de PENDIENTE a CONFIRMADO cuando el pago asociado se marque como aprobado por MercadoPago.

#### Scenario: Pedido transiciona PENDIENTE → CONFIRMADO tras pago aprobado
- **GIVEN** pedido con estado_codigo=PENDIENTE, existe Pago relacionado con estado="approved"
- **WHEN** servicio de pagos invoca transicion_por_pago_aprobado(pedido_id)
- **THEN** pedido.estado_codigo = CONFIRMADO
- **AND** HistorialEstadoPedido registra transición con estado_desde=PENDIENTE

#### Scenario: Pedido no transiciona si pago no está aprobado
- **GIVEN** pedido con estado_codigo=PENDIENTE, Pago con estado="pending" o "rejected"
- **WHEN** servicio intenta transicionar por pago
- **THEN** NO se ejecuta transición
- **AND** pedido mantiene estado PENDIENTE

#### Scenario: Error en transición FSM no afecta estado del pago
- **GIVEN** pedido con estado_codigo=PENDIENTE, intento de transición por pago aprobado
- **WHEN** transición FSM falla por error de DB
- **THEN** pago sigue marcado como "approved"
- **AND** pedido permanece en PENDIENTE
- **AND** error se loggea para revisión manual

#### Scenario: Transición solo si pedido está en PENDIENTE
- **GIVEN** pedido con estado_codigo=CONFIRMADO o CANCELADO
- **WHEN** servicio recibe notificación de pago aprobado
- **THEN** NO se ejecuta transición (ya transicionó o está cancelado)