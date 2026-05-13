# Proposal: change-13-mercadopago-webhook-ipn

## Problema / Oportunidad

MercadoPago notifica de forma asíncrona el resultado del pago vía webhook IPN. El sistema necesita procesar estas notificaciones de manera segura, idempotente y atómica: validar la firma, consultar el estado real en la API de MP, y automáticamente transicionar el pedido según corresponda (aprobado → CONFIRMADO, rechazado → permanece PENDIENTE).

## Solución Propuesta

Implementar el endpoint `POST /api/v1/pagos/webhook` que:
1. Recibe la notificación IPN de MercadoPago (`topic=payment`, `resource_id`)
2. Valida la firma `X-Signature` para garantizar autenticidad
3. Consulta la API de MercadoPago para confirmar el estado real (nunca confiar ciegamente en el webhook)
4. Abre una transacción UoW atómica para actualizar el pago y transicionar el pedido si corresponde
5. Responde HTTP 200 inmediatamente para evitar reintentos de MP

## Alcance

- [ ] Incluir:
  - Endpoint `POST /api/v1/pagos/webhook` (público, validar firma)
  - Validación de firma X-Signature de MercadoPago
  - Consulta a API MP para estado real (nunca confiar solo en webhook)
  - Actualización atómica de tabla Pago dentro de UoW
  - Transición automática PENDIENTE → CONFIRMADO si `mp_status = approved`
  - Decremento atómico de stock al confirmar (vía FSM)
  - Idempotencia: webhook duplicado → no procesa dos veces
  - Logging detallado para debugging
- [ ] Excluir:
  - Frontend (manejo del estado post-pago se hizo en CHANGE-12)
  - Procesamiento de退款 (reembolsos) — fuera de scope
  - Manejo de suscripciones recurrentes — fuera de scope

## Impacto

- **Backend**: Nuevo endpoint webhook + lógica de dominio en módulo pagos
- **DB**: Tabla Pago existente — solo UPDATE del campo `mp_status`
- **Riesgo**: MercadoPago reintenta webhook si no respondemos 200 rápido — mitigar con respuesta inmediata
- **Riesgo**: Race conditions con múltiples webhooks del mismo pago — mitigar con idempotency_key y lock
- **Riesgo**: Decremento de stock dos veces (si webhook llega múltiples veces) — mitigar con validaciones en FSM

## Historias de Usuario Vinculadas

- **US-046** (parte 2): Como Sistema, quiero recibir y procesar webhooks de MercadoPago para confirmar pagos automáticamente y avanzar el pedido a CONFIRMADO.

## Dependencias

- CHANGE-12 (MercadoPago Checkout) — tabla Pago, SDK MP, endpoint crear pago
- CHANGE-10 (FSM Pedidos) — transición automática PENDIENTE → CONFIRMADO con decremento de stock
- CHANGE-09 (Creación de Pedidos) — tabla Pedido, modelo de dominio

## Reglas de Negocio Aplicadas

- RN-PA02: Cada pago tiene idempotency_key único; webhook duplicado se ignora
- RN-PA03: Responder HTTP 200 inmediatamente para evitar reintentos de MP
- RN-PA04: Siempre verificar el estado real consultando la API de MercadoPago
- RN-PA05: Pago "approved" → transición automática PENDIENTE → CONFIRMADO + decremento de stock
- RN-PA06: Pago "rejected" → pedido permanece PENDIENTE
- RN-PA07: Pago "pending"/"in_process" → se actualiza estado del pago pero pedido sigue PENDIENTE
- RN-FS03: Al confirmar, decrementar atómicamente el stock de cada producto
- RN-FS07: HistorialEstadoPedido es append-only (solo INSERT, nunca UPDATE/DELETE)

---

**Generado**: 2026-05-13 | **Change**: change-13-mercadopago-webhook-ipn | **Metodología**: SDD