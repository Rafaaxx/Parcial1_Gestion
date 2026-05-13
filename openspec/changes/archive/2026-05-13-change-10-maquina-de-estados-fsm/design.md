## Design: CHANGE-10 — Máquina de Estados (FSM)

### Technical Approach

Se implementa una FSM como diccionario de transiciones en `PedidoService`, con validación de roles, operaciones atómicas de stock dentro de la transacción UoW, y endpoints RESTful para transicionar y cancelar pedidos. El frontend usa TanStack Query con hooks especializados y componentes de UI para las transiciones.

### Architecture Decisions

#### Decision: FSM structure as in-memory constant

**Choice**: Dictionary `{ origin: [(target, roles, action), ...] }` as module-level constant in `service.py`

**Alternatives considered**: 
- Database-driven FSM with `estados_pedido_transiciones` table — over-engineering, harder to iterate
- Enum-based FSM — rigid, requires code changes for new transitions

**Rationale**: Simple, fast, easy to read and modify. Since there are only 6 states and 7 transitions, hardcoding is more practical than dynamic configuration. Allows action functions as closures (decrement_stock, restore_stock).

#### Decision: Stock operations inside UoW transaction

**Choice**: Stock decrement on CONFIRMADO and restore on CANCEL happen inside the same `async with self.uow` block that updates the pedido and creates the historial.

**Alternatives considered**:
- Separate transactions for stock and order — risk of inconsistency
- Optimistic locking — complex for this use case

**Rationale**: SELECT FOR UPDATE on both the pedido row and each producto row ensures no race conditions. The UoW context manager guarantees atomic commit or rollback.

#### Decision: DELETE endpoint for cancellation

**Choice**: `DELETE /pedidos/{id}` cancels a PENDIENTE order (convenience for CLIENT role)

**Alternatives considered**:
- Only PATCH with { estado: "CANCELADO" } — requires Body payload, more verbose
- POST /pedidos/{id}/cancel — more semantic but inconsistent with REST patterns

**Rationale**: DELETE is RESTful for "cancel/delete" semantics. Role check ensures CLIENT can only cancel their own PENDIENTE orders. PATCH remains for staff-controlled transitions (CONFIRMADO→EN_PREP→EN_CAMINO→ENTREGADO).

### Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Router    │────▶│   Service    │────▶│  UoW        │
│             │     │              │     │             │
│ PATCH/DELETE│     │ transicionar │     │ SELECT FK  │
└─────────────┘     │ _estado()    │     │ UPDATE stock│
                    └──────────────┘     │ INSERT      │
                         │               │ historial   │
                         ▼               └─────────────┘
                  ┌─────────────────┐
                  │ FSM Validation │
                  │ - origin valid?│
                  │ - target valid?│
                  │ - role allowed?│
                  │ - not terminal?│
                  └─────────────────┘
```

### File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/modules/pedidos/schemas.py` | Modify | +AvanzarEstadoRequest, +TransicionResponse |
| `backend/app/modules/pedidos/service.py` | Modify | +FSM_TRANSITION_MAP, transicionar_estado(), _decrementar_stock_en_pedido(), _restaurar_stock_en_pedido() |
| `backend/app/modules/pedidos/router.py` | Modify | +PATCH /{id}/estado, +DELETE /{id} |
| `backend/app/modules/pedidos/__init__.py` | Modify | Export new schemas and service methods |
| `frontend/src/features/pedidos/types.ts` | Create | Tipos para FSM (TransicionEstado, pedido con estado) |
| `frontend/src/features/pedidos/api.ts` | Create | Funciones HTTP para transition/cancel |
| `frontend/src/features/pedidos/hooks/useTransicionEstado.ts` | Create | Hook TanStack Query para mutaciones |
| `frontend/src/features/pedidos/components/OrderList.tsx` | Create | Lista de pedidos con botones de transición |
| `frontend/src/features/pedidos/components/CancelDialog.tsx` | Create | Dialog para cancelar con motivo |
| `frontend/src/pages/AdminOrders.tsx` | Modify | Reemplaza placeholder por OrderList + integración de hooks |

### Interfaces / Contracts

#### Backend Schema (Python)

```python
# schemas.py
class AvanzarEstadoRequest(SQLModel):
    nuevo_estado: str = Field(max_length=20, description="Target state code")
    observacion: Optional[str] = Field(default=None, description="Optional transition note")

class TransicionResponse(SQLModel):
    id: int
    estado_codigo: str
    mensaje: str = "Estado actualizado"
```

#### Frontend Types (TypeScript)

```typescript
// types.ts
export type EstadoPedido = 'PENDIENTE' | 'CONFIRMADO' | 'EN_PREP' | 'EN_CAMINO' | 'ENTREGADO' | 'CANCELADO'

export interface TransicionRequest {
  nuevo_estado: EstadoPedido
  observacion?: string
}

export interface PedidoConEstado extends PedidoRead {
  es_terminal: boolean
  siguiente_estados: EstadoPedido[]
}
```

### Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | FSM map validity, transition validation logic, stock math | pytest - isolate transicionar_estado() with mocked UoW |
| Integration | Full PATCH flow, DELETE flow, role enforcement | pytest - call endpoints with TestClient, check DB state |
| E2E | Manual browser flow: PEDIDOS role advances states | Playwright/codegen - order lifecycle |

**Key test cases:**
- 6 valid forward transitions succeed
- 8+ invalid transitions return 422/403
- Stock decrements on PENDIENTE→CONFIRMADO
- Stock restores on any cancel
- motivo required for cancel (422)
- Terminal states reject transitions
- Historial append-only (1 record per transition)

### Migration / Rollout

No migration required. EstadoPedido table already seeded with 6 states and `es_terminal` flag. FSM is pure application logic.

### Open Questions

- [ ] Should CANCELADO be considered a terminal state? The proposal treats ENTREGADO and CANCELADO as terminals. Need to verify `es_terminal` for CANCELADO in seed data.
- [ ] Role "SISTEMA" for PENDIENTE→CONFIRMADO — is this for future webhook use only, or should we expose a bypass for testing? (Treat as webhook-only for now, use PEDIDOS role for manual testing)
