# Design: MercadoPago Checkout Integration

## Technical Approach

Se implementa un módulo de pagos desacoplado que usa el SDK `mercadopago` para procesar pagos via Checkout API. El diseño sigue el patrón de módulos existentes (pedidos, auth): modelo → schemas → repository → service → router. La integración con el FSM de pedidos ocurre en el service de pagos, que delega la transición de estado al UoW del módulo pedidos.

## Architecture Decisions

### Decision: Abstracción del SDK de MercadoPago

**Choice**: Adapter pattern con interfaz `MercadoPagoGateway` que encapsula llamadas al SDK
**Alternatives considered**: Llamar directamente al SDK en el service, usar librería externa
**Rationale**: Facilita testing (mock del gateway) y aísla cambios de API de terceros. El SDK `mercadopago` ya está en requirements.txt.

### Decision: Webhook validation approach

**Choice**: Validar firma del webhook + consulta API de verificación (dual validation)
**Alternatives considered**: Solo validar firma, solo confiar en payload
**Rationale**: Seguridad PCI-DSS requiere nunca confiar solo en datos recibidos. La consulta a la API real previene ataques de spoofing.

### Decision: Idempotency strategy

**Choice**: Generar UUID como idempotency_key en el backend, no exponérselo al cliente
**Alternatives considered**: Idempotency key del lado cliente, ключ basado en hash del pedido
**Rationale**: Evita race conditions si el cliente hace retry. El UUID garantiza unicidad sin coordinación.

### Decision: Transición FSM desde pagos service

**Choice**: El `PagosService` recibe el `UnitOfWork` de pedidos y avanza el estado
**Alternatives considered**: Callback desde pedidos, evento pub/sub
**Rationale**: Mantiene consistencia transaccional dentro del mismo UoW. El service de pagos tiene acceso al UoW via inyección en el router.

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Router    │────▶│   Service   │
│ (Checkout)  │     │  (pagos)    │     │  (pagos)    │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                   ┌─────────────┐            │
                   │   Model     │◀───────────┤
                   │   (Pago)    │            ▼
                   └─────────────┘     ┌─────────────┐
                                        │   MP SDK    │
                                        │  (gateway)  │
                                        └─────────────┘

Webhook Flow:
MP Server ──▶ Router /webhook ──▶ Service.procesar_webhook()
                                          │
                         ┌────────────────┴────────────────┐
                         ▼                                   ▼
                  MP Gateway (verify)              FSM: pedido → CONFIRMADO
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/modules/pagos/__init__.py` | Create | Module init, exports |
| `backend/app/modules/pagos/model.py` | Create | SQLModel `Pago` con campos: id, pedido_id, mp_payment_id, mp_status, external_reference, idempotency_key, created_at, updated_at, deleted_at |
| `backend/app/modules/pagos/schemas.py` | Create | Pydantic schemas: PagoCreate, PagoResponse, WebhookPayload, PagoStatus |
| `backend/app/modules/pagos/repository.py` | Create | Repository con: create, get_by_pedido_id, get_by_idempotency_key, update_status |
| `backend/app/modules/pagos/gateway.py` | Create | MercadoPagoGateway adapter: create_preference, get_payment_status |
| `backend/app/modules/pagos/service.py` | Create | PagosService con crear_pago, procesar_webhook, consultar_pago |
| `backend/app/modules/pagos/router.py` | Create | Endpoints: POST /crear, POST /webhook, GET /{pedido_id} |
| `backend/app/modules/pedidos/service.py` | Modify | Agregar método `_transicionar_a_confirmado` llamado desde pagos service |
| `backend/migrations/versions/011_add_pagos_table.py` | Create | Alembic migration para tabla pagos |
| `backend/tests/test_pagos.py` | Create | Tests pytest >60% coverage |
| `frontend/src/features/cart/stores/paymentStore.ts` | Create | Zustand store: status, mpPaymentId, statusDetail, error |
| `frontend/src/features/cart/components/CheckoutForm.tsx` | Create | Componente con @mercadopago/sdk-react |
| `frontend/src/features/cart/components/PaymentStatus.tsx` | Create | Componente para mostrar estado del pago |
| `backend/.env.example` | Modify | Agregar MP_ACCESS_TOKEN, MP_PUBLIC_KEY, MP_NOTIFICATION_URL |

## Interfaces / Contracts

### Backend - Pagos Module

```python
# model.py
class Pago(SQLModel, table=True):
    __tablename__ = "pagos"
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id")
    mp_payment_id: Optional[str] = Field(max_length=50)
    mp_status: str = Field(max_length=20)  # pending, approved, rejected, cancelled
    external_reference: Optional[str] = Field(max_length=100)
    idempotency_key: str = Field(max_length=36, unique=True)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

# gateway.py
class MercadoPagoGateway(Protocol):
    async def create_preference(self, idempotency_key: str, amount: Decimal, external_reference: str) -> dict: ...
    async def get_payment_status(self, payment_id: str) -> dict: ...

# service.py
class PagosService:
    async def crear_pago(uow: UnitOfWork, pedido_id: int) -> Pago: ...
    async def procesar_webhook(uow: UnitOfWork, payload: dict) -> None: ...
    async def consultar_pago(uow: UnitOfWork, pedido_id: int, usuario_id: int) -> Pago: ...
```

### Frontend - Payment Store

```typescript
interface PaymentState {
  status: 'idle' | 'processing' | 'approved' | 'rejected' | 'error'
  mpPaymentId: string | null
  statusDetail: string | null
  error: string | null

  createPayment: (pedidoId: number) => Promise<void>
  checkStatus: (pedidoId: number) => Promise<void>
  reset: () => void
}
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | PagosService.crear_pago, gateway mocking | pytest + unittest.mock |
| Unit | Idempotency duplicate rejection |pytest con UUID fijo |
| Unit | Webhook status transitions | pytest parametrizado |
| Integration | POST /pagos/crear → 201 + db record | TestClient |
| Integration | Webhook → FSM transition | TestClient con pedidos fixtures |
| E2E | Checkout flow completo | Playwright (fuera de scope MVP) |

## Migration / Rollout

**Migration**: Nueva migración Alembic `011_add_pagos_table.py` con columnas nullable inicialmente. El mp_payment_id se completa cuando MercadoPago responde.

**Feature Flag**: No requerido — el módulo es nuevo y no afecta funcionalidad existente.

**Rollout Plan**:
1. Apply migration: `alembic upgrade head`
2. Deploy backend con nuevo router
3. Deploy frontend con paymentStore
4. Configurar MP_NOTIFICATION_URL en dashboard de MercadoPago (ngrok para dev)

## Open Questions

- [ ] ¿El webhook necesita autenticación JWT o puede ser público? **R: Público pero con validación de firma.**
- [ ] ¿Cómo manejar reintentos del webhook si la transición FSM falla? **R: Retry logic con exponential backoff, registrar en tabla para auditoría.**
- [ ] ¿El frontend usa el SDK React o API directa? **R: SDK React para tokenización PCI-compliant.**