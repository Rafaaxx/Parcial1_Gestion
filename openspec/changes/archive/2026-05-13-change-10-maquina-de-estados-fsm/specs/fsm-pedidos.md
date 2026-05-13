# Delta Spec — CHANGE-10: FSM Pedidos

## Capability: fsm-pedidos

### Purpose
Defines the FSM core: transition validation map, role-based permissions per transition, terminal state enforcement, and the transicionar_estado() service method.

### Requirements

#### FSM-TRANS-01: Transition Map
The system MUST define a strict transition map: `PENDIENTE→CONFIRMADO`, `PENDIENTE→CANCELADO`, `CONFIRMADO→EN_PREP`, `CONFIRMADO→CANCELADO`, `EN_PREP→EN_CAMINO`, `EN_PREP→CANCELADO`, `EN_CAMINO→ENTREGADO`. Any transition not in this map MUST be rejected with HTTP 422.

#### Scenario: Valid forward transition
- GIVEN a pedido in state `CONFIRMADO`
- WHEN `transicionar_estado()` is called with `nuevo_estado=EN_PREP` by ADMIN
- THEN the pedido's `estado_codigo` becomes `EN_PREP`
- AND a new `HistorialEstadoPedido` record is created with `estado_desde=CONFIRMADO, estado_hacia=EN_PREP`

#### Scenario: Invalid transition rejected
- GIVEN a pedido in state `PENDIENTE`
- WHEN `transicionar_estado()` is called with `nuevo_estado=EN_CAMINO`
- THEN the system MUST return HTTP 422 with detail "Transición no válida"

#### FSM-TRANS-02: Terminal State Guard
The system MUST reject ANY transition from a terminal state (`ENTREGADO` or `CANCELADO`) by checking `EstadoPedido.es_terminal`.

#### Scenario: Terminal state rejects transitions
- GIVEN a pedido in state `ENTREGADO` (es_terminal=true)
- WHEN any `transicionar_estado()` is attempted
- THEN the system MUST return HTTP 422 with detail "Estado terminal: no se permiten transiciones"

#### FSM-TRANS-03: Role Validation per Transition
The system MUST enforce per-transition role permissions:
- `PENDIENTE→CANCELADO`: CLIENT (owner), PEDIDOS, ADMIN
- `CONFIRMADO→CANCELADO`: PEDIDOS, ADMIN
- `EN_PREP→CANCELADO`: ADMIN only
- All forward transitions (`CONFIRMADO→EN_PREP`, `EN_PREP→EN_CAMINO`, `EN_CAMINO→ENTREGADO`): PEDIDOS, ADMIN
- `PENDIENTE→CONFIRMADO`: SISTEMA only (webhook), rejected for all human roles

#### Scenario: Role rejected for transition
- GIVEN a pedido in state `EN_PREP`
- WHEN a CLIENT user attempts to cancel it
- THEN the system MUST return HTTP 403 with detail "No tienes permisos para esta transición"

#### FSM-TRANS-04: Forward-Only constraint (RN-FS01)
The system MUST reject transitions that would go "backward" in order (e.g., `EN_PREP→CONFIRMADO` or `EN_CAMINO→EN_PREP`), enforced by the explicit transition map.

#### Scenario: Backward transition rejected
- GIVEN a pedido in state `EN_CAMINO`
- WHEN `transicionar_estado()` is called with `nuevo_estado=EN_PREP`
- THEN the system MUST return HTTP 422 with detail "Transición no válida"

#### FSM-TRANS-05: Append-Only Audit Trail (RN-FS07)
Every successful transition MUST create exactly one `HistorialEstadoPedido` record with `estado_desde`, `estado_hacia`, `usuario_id`, `observacion`, and `created_at`. The service MUST NOT update or delete existing historial records.

#### Scenario: Every transition registered
- GIVEN a pedido advancing from CONFIRMADO→EN_PREP
- WHEN the transition succeeds
- THEN a new `HistorialEstadoPedido` record exists with `estado_desde=CONFIRMADO, estado_hacia=EN_PREP, usuario_id=<actor>`
