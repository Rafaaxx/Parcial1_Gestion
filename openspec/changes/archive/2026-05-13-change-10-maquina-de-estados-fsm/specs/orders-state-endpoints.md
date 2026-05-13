# Delta Spec — CHANGE-10: Orders State Endpoints

## Capability: orders-state-endpoints

### Purpose
PATCH /api/v1/pedidos/{id}/estado for explicit state transitions and DELETE /api/v1/pedidos/{id} as a convenience cancel for CLIENT role.

### Requirements

#### ORDERS-PATCH-01: AvanzarEstadoRequest Schema
The system MUST define schema `AvanzarEstadoRequest` with fields: `nuevo_estado: str` (required) and `motivo: Optional[str]` (required when `nuevo_estado=CANCELADO`, per RN-05).

#### Scenario: motivo required for cancel
- GIVEN a PATCH request with `nuevo_estado=CANCELADO` and no `motivo`
- WHEN the request is validated
- THEN the system MUST return HTTP 422 with field-level validation error

#### ORDERS-PATCH-02: PATCH /pedidos/{id}/estado
The system MUST expose `PATCH /api/v1/pedidos/{id}/estado` that validates the transition against the FSM map, checks role permissions, executes stock ops if needed, and persists atomically via UoW. Returns 200 `PedidoRead` on success.

#### Scenario: PATCH advance state by ADMIN
- GIVEN a pedido in CONFIRMADO
- WHEN ADMIN sends PATCH `{"nuevo_estado": "EN_PREP"}`
- THEN response is 200 with `estado_codigo=EN_PREP`
- AND the historial contains the new transition record

#### Scenario: PATCH advance state by PEDIDOS
- GIVEN a pedido in EN_PREP
- WHEN a PEDIDOS user sends PATCH `{"nuevo_estado": "EN_CAMINO"}`
- THEN response is 200 with `estado_codigo=EN_CAMINO`

#### ORDERS-DELETE-01: DELETE /pedidos/{id} (Cancel Convenience)
The system MUST expose `DELETE /api/v1/pedidos/{id}` that cancels a pedido. For CLIENT role: only cancels own orders in `PENDIENTE`. For ADMIN/PEDIDOS: cancels `PENDIENTE` or `CONFIRMADO`. Returns 200 `PedidoRead` on success.

#### Scenario: CLIENT cancels own PENDIENTE order
- GIVEN a CLIENT with an order in PENDIENTE
- WHEN the CLIENT sends DELETE with `motivo="Ya no lo quiero"`
- THEN response is 200 with `estado_codigo=CANCELADO`
- AND no stock restore is needed

#### Scenario: CLIENT cannot cancel CONFIRMADO order via DELETE
- GIVEN a CLIENT with an order in CONFIRMADO
- WHEN the CLIENT sends DELETE
- THEN response is HTTP 403 or 422 with detail about insufficient permissions

#### Scenario: ADMIN cancels CONFIRMADO order via DELETE
- GIVEN an ADMIN with an order in CONFIRMADO
- WHEN ADMIN sends DELETE with `motivo="Problema de stock"`
- THEN response is 200 with `estado_codigo=CANCELADO`
- AND stock is restored atomically
