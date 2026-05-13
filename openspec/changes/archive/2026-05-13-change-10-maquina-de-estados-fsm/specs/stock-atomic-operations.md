# Delta Spec — CHANGE-10: Stock Atomic Operations

## Capability: stock-atomic-operations

### Purpose
Atomic stock decrement on CONFIRMADO and atomic restore on cancel, both inside the same UoW transaction as the state transition.

### Requirements

#### STOCK-DEC-01: Decrement on CONFIRMADO (RN-FS03)
When a pedido transitions to `CONFIRMADO`, the system MUST decrement `stock_cantidad` for each `DetallePedido.producto_id` by the ordered `cantidad`. The operation MUST use `SELECT FOR UPDATE` to lock product rows and MUST be in the same UoW transaction as the transition.

#### Scenario: Stock decremented atomically
- GIVEN a pedido with 2x Product A (stock=10) transitioning to CONFIRMADO
- WHEN the transition succeeds
- THEN Product A's `stock_cantidad` is 8
- AND if any decrement fails, the entire transaction rolls back

#### Scenario: Race condition prevented
- GIVEN two concurrent requests for the same product's last unit
- WHEN both attempt CONFIRMADO simultaneously
- THEN exactly one succeeds; the other MUST fail with HTTP 409 or rollback

#### STOCK-RES-01: Restore on Cancel (RN-FS05)
When a pedido transitions to `CANCELADO` from `CONFIRMADO` or `EN_PREP`, the system MUST revert the stock decrement by incrementing `stock_cantidad` for each item by the ordered quantity. MUST use FOR UPDATE inside the same UoW.

#### Scenario: Stock restored on cancel from CONFIRMADO
- GIVEN a pedido with 3x Product B (stock=7 after decrement) being canceled from CONFIRMADO
- WHEN the cancel transition succeeds
- THEN Product B's `stock_cantidad` returns to 10

#### Scenario: No restore for PENDIENTE→CANCELADO
- GIVEN a pedido in PENDIENTE being canceled (stock was never decremented)
- WHEN the cancel transition succeeds
- THEN no stock modification occurs (restore is unnecessary)
