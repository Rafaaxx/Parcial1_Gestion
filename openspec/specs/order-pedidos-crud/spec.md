# order-pedidos-crud Specification

## Purpose
TBD - created by archiving change change-09-order-creation-uow. Update Purpose after archive.
## Requirements
### Requirement: Pedido CRUD — Create Order with Atomic UoW

El sistema SHALL crear pedidos con atomicidad completa usando Unit of Work, garantizando que todas las operaciones en la transaccion se completen o ninguna (rollback completo).

#### Scenario: Crear pedido exitoso
- **GIVEN** usuario autenticado (CLIENT), producto disponible con stock, forma_pago valida
- **WHEN** POST /api/v1/pedidos con body valido
- **THEN** responde 201 + PedidoRead
- **AND** Pedido existe en BD con estado_codigo=PENDIENTE
- **AND** DetallePedido tiene snapshots de nombre y precio
- **AND** HistorialEstadoPedido tiene estado_desde=NULL

#### Scenario: Stock insuficiente genera rollback
- **GIVEN** producto con stock_cantidad=5
- **WHEN** POST /api/v1/pedidos con cantidad=100 para ese producto
- **THEN** responde 422 con mensaje "Stock insuficiente"
- **AND** NO Pedido existe en BD

#### Scenario: Forma de pago invalida genera 422
- **GIVEN** forma_pago_codigo="INVALIDO"
- **WHEN** POST /api/v1/pedidos
- **THEN** responde 422 con mensaje "Forma de pago no existe o esta deshabilitada"

#### Scenario: Direccion no pertenece al usuario genera 404
- **GIVEN** direccion pertenece a otro usuario
- **WHEN** POST /api/v1/pedidos con esa direccion
- **THEN** responde 404 (no 403, no revelar existencia)

#### Scenario: Listar pedidos como CLIENT
- **GIVEN** usuario CLIENT con 3 pedidos y otro usuario con 5 pedidos
- **WHEN** GET /api/v1/pedidos como CLIENT
- **THEN** responde 200 con solo 3 pedidos del usuario

#### Scenario: Listar pedidos como ADMIN
- **GIVEN** 8 pedidos en total en BD
- **WHEN** GET /api/v1/pedidos como ADMIN
- **THEN** responde 200 con los 8 pedidos

#### Scenario: Ver detalle de pedido
- **GIVEN** pedido existe con detalles y historial
- **WHEN** GET /api/v1/pedidos/{id} como propietario
- **THEN** responde 200 con PedidoDetail (incluye detalles e historial)

#### Scenario: Ver historial de estados
- **GIVEN** pedido con 2 transiciones de estado
- **WHEN** GET /api/v1/pedidos/{id}/historial
- **THEN** responde 200 con 2 registros ordenados por created_at ASC
- **AND** primer registro tiene estado_desde=NULL

### Requirement: Pedido CRUD — Snapshot Pattern

El sistema SHALL guardar snapshots inmutables de nombre y precio en DetallePedido al momento de crear el pedido.

#### Scenario: Snapshot de nombre persiste aunque producto cambie
- **GIVEN** producto "Pizza" con precio 100
- **WHEN** se crea pedido con ese producto
- **AND** luego se renombra producto a "Pizza Grande"
- **THEN** DetallePedido.nombre_snapshot sigue siendo "Pizza"

#### Scenario: Snapshot de precio persiste aunque producto cambie
- **GIVEN** producto con precio_base=100
- **WHEN** se crea pedido con cantidad=2 de ese producto
- **AND** luego precio_base cambia a 150
- **THEN** DetallePedido.precio_snapshot sigue siendo 100

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

### Requirement: UoW — SELECT FOR UPDATE

El sistema SHALL implementar get_for_update(producto_id) en ProductoRepository con SELECT FOR UPDATE para bloquear la fila durante validacion de stock.

#### Scenario: SELECT FOR UPDATE bloquea fila
- **GIVEN** dos requests simultaneos para crear pedido con el mismo producto (stock=10, ambos piden cantidad=8)
- **WHEN** Request A ejecuta get_for_update(producto_id)
- **THEN** Request B queda en espera hasta que Request A complete la transaccion
- **AND** Request A puede validar stock y crear su pedido
- **AND** Request B al ejecutarse ve stock剩余=2 y recibe 422

