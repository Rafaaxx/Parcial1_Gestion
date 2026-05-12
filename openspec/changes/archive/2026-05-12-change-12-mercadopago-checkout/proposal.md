# Proposal: change-12-mercadopago-checkout

## Intent

Implementar la integración completa con MercadoPago Checkout API para permitir a los clientes pagar sus pedidos con tarjeta de crédito/débito, Rapipago, Pago Fácil y Cuenta MercadoPago. El módulo debe manejar tokenización PCI-compliant en el frontend, procesamiento asíncrono de pagos vía webhook IPN, y transición automática del pedido a CONFIRMADO cuando el pago es aprobado.

**Por qué este cambio es necesario**: El proyecto Food Store actualmente no tiene ningún módulo de pagos implementado. Según la especificación técnica (Integrador.txt), el sistema debe procesar pagos integrados con MercadoPago para cumplir con los objetivos OBJ-01 (Cliente) y OBJ-06 (Sistema).

## Scope

### In Scope
- Backend: Módulo `pagos/` con modelo, schemas Pydantic, repository, service, router
- Database: Tabla `Pago` con migración Alembic (mp_payment_id, estado, idempotency_key, external_reference)
- API REST: Endpoints POST /api/v1/pagos/crear, POST /api/v1/pagos/webhook, GET /api/v1/pagos/{pedido_id}
- Webhook IPN: Procesamiento de notificaciones asíncronas de MercadoPago
- Idempotency: Generación y validación de keys para evitar pagos duplicados
- FSM Integration: Transición automática PENDIENTE → CONFIRMADO tras pago aprobado
- Frontend: paymentStore Zustand, componentes de checkout con SDK React
- Tests: pytest para módulo pagos (>60% cobertura)
- Config: Variables de entorno MP_ACCESS_TOKEN, MP_PUBLIC_KEY, MP_NOTIFICATION_URL

### Out of Scope
- Proceso de退款 (reembolsos) —postergado
- Notificaciones email al cliente —ya existe en otro módulo
- Pagos con billeteras digitales externas (PayPal, etc.) —solo MercadoPago
- Historial de pagos detallado en UI —MVP solo estado actual

## Capabilities

### New Capabilities
- `mp-checkout-backend`: Backend completo del módulo pagos con endpoints, service, repository
- `mp-checkout-webhook`: Procesamiento de notificaciones IPN de MercadoPago
- `mp-checkout-frontend`: PaymentStore y componentes de checkout en frontend

### Modified Capabilities
- `order-pedidos-crud`: Se agrega transición automática de estado por pago aprobado (PENDIENTE → CONFIRMADO)

## Approach

1. **Backend**: Crear módulo `app/modules/pagos/` siguiendo el patrón de módulos existentes (pedidos, auth). Usar SDK `mercadopago` 2.3.0+ con idempotency_key UUID en cada request.
2. **Database**: Nueva migración Alembic para tabla `Pago` con FK a `pedidos`, campos para mp_payment_id, estado (pending/approved/rejected/cancelled), timestamps.
3. **Webhook**: Endpoint público que valida firma de MercadoPago, consulta API para confirmar estado real (nunca confiar solo en datos del webhook), actualiza tabla Pago y avanza FSM del pedido.
4. **Frontend**: Crear paymentStore Zustand (status, mpPaymentId, statusDetail, error) y componentes de checkout que usan @mercadopago/sdk-react para tokenización PCI-compliant.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/modules/pagos/` | New | Módulo completo: model.py, schemas.py, repository.py, service.py, router.py |
| `backend/app/modules/pedidos/service.py` | Modified | Agregar transición automática por pago aprobado |
| `backend/alembic/versions/` | New | Migración para tabla Pago |
| `backend/tests/test_pagos.py` | New | Tests unitarios para módulo pagos |
| `frontend/src/features/cart/stores/` | New | paymentStore.ts Zustand |
| `frontend/src/features/cart/components/` | New | CheckoutForm, PaymentStatus |
| `.env.example` | Modified | Agregar variables MP_ACCESS_TOKEN, MP_PUBLIC_KEY, MP_NOTIFICATION_URL |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| MP API cambio durante desarrollo | Low | Abstraer SDK en service con adapter pattern |
| Webhook duplicado por retry MP | Medium | Validar idempotency_key antes de procesar |
| Transición FSM falla por bug | Medium | Tests exhaustivos de FSM con pytest |
| Keys de test no funcionan | Low | Documentar en README config de entorno sandbox |

## Rollback Plan

1. Ejecutar downgrade de migración Alembic para tabla Pago
2. Eliminar carpeta `backend/app/modules/pagos/`
3. Revertir cambios en `backend/app/modules/pedidos/service.py` (quitar transición automática)
4. Eliminar `frontend/src/features/cart/stores/paymentStore.ts`
5. Eliminar componentes de checkout del frontend
6. Eliminar tests de pagos

## Dependencies

- `mercadopago>=2.3.0` en backend/requirements.txt
- `@mercadopago/sdk-react` en frontend/package.json
- Seed data de formas de pago ya existe (ver `seed.py`)
- Variables de entorno configuradas en .env

## Success Criteria

- [ ] POST /api/v1/pagos/crear retorna mp_payment_id y status
- [ ] POST /api/v1/pagos/webhook procesa notificaciones IPN y responde HTTP 200 inmediatamente
- [ ] GET /api/v1/pagos/{pedido_id} retorna estado del pago con validaciones de propiedad
- [ ] Pedido transiciona PENDIENTE → CONFIRMADO automáticamente tras pago aprobado
- [ ] paymentStore Zustand manage estado: idle/processing/approved/rejected/error
- [ ] Checkout con SDK React tokeniza datos de tarjeta (nunca pasan por servidor)
- [ ] Idempotency key previene cobros duplicados
- [ ] Tests pytest con cobertura >60% para módulo pagos
- [ ] No hay datos de tarjeta en logs ni requests al backend (PCI SAQ-A)