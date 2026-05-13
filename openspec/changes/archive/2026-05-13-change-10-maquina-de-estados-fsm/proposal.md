# Proposal: CHANGE-10 — Máquina de Estados (FSM)

## Intent
El módulo pedidos actualmente solo crea órdenes y las consulta. No hay lógica para avanzar el estado del pedido a través de su ciclo de vida (PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO), ni para cancelaciones. Sin FSM no hay trazabilidad real, no hay control de stock atómico al confirmar/cancelar, y los endpoints PATCH/DELETE no existen. Este cambio implementa la máquina de estados completa con validación, permisos por rol, operaciones atómicas de stock y el audit trail append-only.

## Scope

### In Scope
- **Backend**: FSM transition map, transicionar_estado(), cancelar_pedido(), stock decrement/restore, PATCH+DELETE endpoints, AvanzarEstadoRequest schema
- **Frontend**: AdminOrders functional UI with hook-based architecture, transition buttons, cancel dialog with motivo
- **Tests**: Full FSM test suite covering all valid transitions (6), invalid transitions (8+), stock operations, permission checks, historic audit

### Out of Scope
- Webhook IPN (CHANGE-13) — PENDIENTE→CONFIRMADO será llamable por ahora para testing
- MercadoPago integration (CHANGE-12)
- Order Management Panel full (CHANGE-11)

## Capabilities

### New Capabilities
- `fsm-pedidos`: FSM validation, transition map, transicionar_estado() service method
- `orders-state-endpoints`: PATCH /pedidos/{id}/estado, DELETE /pedidos/{id}
- `stock-atomic-operations`: decrement on CONFIRMADO, restore on cancel
- `admin-orders-ui`: AdminOrders with transition buttons and cancel dialog

### Modified Capabilities
- `order-pedidos-crud`: New endpoints PATCH estado and DELETE cancel
- `historial-audit`: Existing historial endpoint fed by real FSM transitions

## Approach
FSM map as dict {origin: [(target, allowed_roles, action)]} in PedidoService. Each transition validates: origin exists in map, target allowed, user role matches, origin not terminal. Stock ops via update_stock_atomic() inside UoW transaction. Cancel requires motivo (RN-05). PATCH handles advance and cancel; DELETE is convenience for client cancel from PENDIENTE. Frontend: new features/pedidos/ with api.ts, types.ts, hooks, AdminOrders rewritten with TanStack Query.

## Affected Areas
| Area | Impact | Description |
|------|--------|-------------|
| schemas.py | Modified | +AvanzarEstadoRequest |
| service.py | Modified | +FSM map, transicionar_estado, cancelar_pedido |
| router.py | Modified | +PATCH /{id}/estado, +DELETE /{id} |
| __init__.py | Modified | Export new symbols |
| features/pedidos/ | New | API layer, types, hooks, components |
| AdminOrders.tsx | Modified | Real order list + transitions |
| test_pedidos_api.py | Modified | +FSM test classes |

## Risks
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Race double transition | Low | SELECT FOR UPDATE on Pedido row |
| Stock inconsistency | Low | All stock ops inside same UoW transaction |
| Concurrent cancel+advance | Low | Row lock via UoW FOR UPDATE |
| CLIENT cancels after advance | Med | Check es_terminal from DB inside locked transaction |

## Rollback Plan
- **Revert code**: git revert on all FSM-related files
- **Revert DB**: No new migrations needed
- **Data integrity**: FSM transitions are append-only; revert prevents new transitions

## Dependencies
- CHANGE-09 (order creation) — archived and implemented
- CHANGE-01 (auth JWT + RBAC) — roles exist
- ProductoRepository.update_stock_atomic — ready
- 6 EstadoPedido values seeded — ready

## Success Criteria
- [ ] All 6 forward transitions succeed with correct stock ops
- [ ] All invalid transitions return proper 4xx errors
- [ ] Stock decremented atomically on CONFIRMADO
- [ ] Stock restored atomically on cancel
- [ ] motivo required for cancelations (422)
- [ ] DELETE /pedidos/{id} cancels PENDIENTE for CLIENT only
- [ ] Every transition creates 1 HistorialEstadoPedido record
- [ ] Terminal states reject all transitions
- [ ] AdminOrders UI functional with transitions
- [ ] All existing CHANGE-09 tests still pass
- [ ] Manual test list verified post-implementation
