# order-pedidos-crud Specification

## Purpose
TBD - created by archiving change change-09-order-creation-uow. Update Purpose after archive.

## MODIFIED Requirements

### Requirement: Listar pedidos con filtros (MODIFIED)

El sistema SHALL permitir filtrar pedidos por estado, rango de fechas, y búsqueda por cliente/ID, además de la paginación existente.

#### Scenario: Filtrar por estado
- **GIVEN** 10 pedidos con diferentes estados (3 CONFIRMADOS, 4 PENDIENTES, 3 ENTREGADOS)
- **WHEN** GET /api/v1/pedidos?estado=CONFIRMADO
- **THEN** responde 200 con solo los 3 pedidos en estado CONFIRMADO
- **AND** total=3 en la respuesta

#### Scenario: Filtrar por rango de fechas
- **GIVEN** pedidos creados en diferentes fechas (2026-01-01, 2026-01-15, 2026-02-01, 2026-03-01)
- **WHEN** GET /api/v1/pedidos?desde=2026-01-10&hasta=2026-02-15
- **THEN** responde con pedidos creados entre esas fechas

#### Scenario: Filtrar por búsqueda (cliente o ID)
- **GIVEN** pedido con id=42 hecho por cliente "Juan Pérez"
- **WHEN** GET /api/v1/pedidos?busqueda=Juan
- **THEN** responde con ese pedido (match por nombre de cliente)
- **WHEN** GET /api/v1/pedidos?busqueda=42
- **THEN** responde con ese pedido (match por ID)

#### Scenario: Filtros combinados
- **GIVEN** pedidos en diferentes estados y fechas
- **WHEN** GET /api/v1/pedidos?estado=CONFIRMADO&desde=2026-01-01&busqueda=pizza
- **THEN** responde con pedidos que cumplen TODOS los filtros (AND)

#### Scenario: Sin resultados para filtros
- **GIVEN** no hay pedidos que coincidan con los filtros
- **WHEN** GET /api/v1/pedidos?estado=CONFIRMADO&desde=2027-01-01
- **THEN** responde 200 con items=[] y total=0

---

### Requirement: Listar pedidos incluyendo información del cliente

El sistema SHALL incluir el nombre y email del cliente en la respuesta del listado de pedidos para ADMIN/PEDIDOS.

#### Scenario: Obtener pedidos con datos del cliente
- **GIVEN** pedido con usuario_id=5 que tiene nombre="Juan Pérez" y email="juan@test.com"
- **WHEN** GET /api/v1/pedidos como ADMIN
- **THEN** la respuesta incluye campo cliente: { id: 5, nombre: "Juan Pérez", email: "juan@test.com" }

---

## ADDED Requirements

### Requirement: GET /pedidos/{id} — Include usuario info

El endpoint de detalle SHALL incluir información del usuario cliente en la respuesta.

#### Scenario: Ver detalle con info del cliente
- **GIVEN** pedido con usuario_id=10 existe
- **WHEN** GET /api/v1/pedidos/10 como ADMIN
- **THEN** la respuesta PedidoDetail incluye campo usuario: { id: 10, nombre: "...", email: "..." }

---

## Original Requirements (preserved)

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

### Requirement: UoW — SELECT FOR UPDATE

El sistema SHALL implementar get_for_update(producto_id) en ProductoRepository con SELECT FOR UPDATE para bloquear la fila durante validacion de stock.

#### Scenario: SELECT FOR UPDATE bloquea fila
- **GIVEN** dos requests simultaneos para crear pedido con el mismo producto (stock=10, ambos piden cantidad=8)
- **WHEN** Request A ejecuta get_for_update(producto_id)
- **THEN** Request B queda en espera hasta que Request A complete la transaccion
- **AND** Request A puede validar stock y crear su pedido
- **AND** Request B al ejecutarse ve stock剩余=2 y recibe 422