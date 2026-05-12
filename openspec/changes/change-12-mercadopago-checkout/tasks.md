# Tasks: change-12-mercadopago-checkout

## Phase 1: Database & Model

- [x] 1.1 Crear migración Alembic para tabla `Pago` con campos: id, pedido_id (FK), mp_payment_id, mp_status, external_reference, idempotency_key, created_at, updated_at, deleted_at
- [x] 1.2 Crear modelo SQLModel `Pago` en `backend/app/modules/pagos/model.py`
- [x] 1.3 Agregar variables de entorno MP_ACCESS_TOKEN, MP_PUBLIC_KEY, MP_NOTIFICATION_URL a .env.example

## Phase 2: Backend Module Implementation

- [x] 2.1 Crear schemas Pydantic en `backend/app/modules/pagos/schemas.py` (PagoCreate, PagoResponse, WebhookPayload)
- [x] 2.2 Crear repository en `backend/app/modules/pagos/repository.py` con métodos: create, get_by_pedido_id, get_by_idempotency_key, update_status
- [x] 2.3 Crear service en `backend/app/modules/pagos/service.py` con lógica de negocio: crear_pago, procesar_webhook, consultar_pago
- [x] 2.4 Crear router en `backend/app/modules/pagos/router.py` con endpoints: POST /crear, POST /webhook, GET /{pedido_id}
- [x] 2.5 Registrar router en `backend/app/main.py` con prefijo /api/v1/pagos
- [x] 2.6 Modificar `backend/app/modules/pedidos/service.py` para agregar transición automática PENDIENTE → CONFIRMADO cuando pago es aprobado

## Phase 3: Frontend Implementation

- [x] 3.1 Crear paymentStore Zustand en `frontend/src/features/cart/stores/paymentStore.ts` con estados: idle, processing, approved, rejected, error
- [x] 3.2 Crear componente CheckoutForm en `frontend/src/features/cart/components/CheckoutForm.tsx` usando checkout redirection (init_point)
- [x] 3.3 Crear componente PaymentStatus en `frontend/src/features/cart/components/PaymentStatus.tsx`
- [x] 3.4 Integrar componentes en el flujo de checkout (componentes creados, listos para usar)

## Phase 4: Testing

- [ ] 4.1 Escribir tests pytest para módulo pagos: crear_pago, procesar_webhook, consultar_pago
- [ ] 4.2 Escribir tests para transición automática de FSM
- [ ] 4.3 Verificar cobertura >60%

## Phase 5: Integration & Verification

- [ ] 5.1 Verificar que POST /api/v1/pagos/crear retorna mp_payment_id y status
- [ ] 5.2 Verificar que POST /api/v1/pagos/webhook procesa notificaciones y responde HTTP 200
- [ ] 5.3 Verificar que GET /api/v1/pagos/{pedido_id} retorna estado del pago
- [ ] 5.4 Verificar transición automática PENDIENTE → CONFIRMADO tras pago aprobado
- [ ] 5.5 Verificar idempotency_key previene cobros duplicados