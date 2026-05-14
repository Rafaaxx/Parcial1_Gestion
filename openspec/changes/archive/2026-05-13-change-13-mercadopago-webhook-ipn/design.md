# Design: change-13-mercadopago-webhook-ipn

## Arquitectura

### Componentes Principales

| Componente | Responsabilidad | Archivo |
|------------|-----------------|---------|
| **WebhookRouter** | Recibe POST /api/v1/pagos/webhook, valida firma, responde 200 inmediato | `app/modules/pagos/router.py` (extensión) |
| **MercadoPagoClient** | Wrapper sobre SDK MP para consultar estado de pago | `app/modules/pagos/mp_client.py` |
| **PagoService** | Lógica de procesamiento: validar, actualizar pago, transicionar pedido | `app/modules/pagos/service.py` (extensión) |
| **PagoRepository** | Acceso a tabla Pago para UPDATE de mp_status | `app/repositories/pago_repository.py` |
| **PedidoService** | Avanza estado PENDIENTE → CONFIRMADO con decremento de stock | `app/modules/pedidos/service.py` (extensión) |
| **UnitOfWork** | Gestiona transacción atómica: UPDATE Pago + UPDATE Pedido + INSERT Historial | `app/uow.py` (extensión) |

### Patrones de Diseño

- **Idempotency**: Webhook duplicado con mismo `mp_payment_id` se detecta y se ignora — ya fue procesado
- **External Call First**: Siempre consultar API MP antes de actualizar BD — no confiar ciegamente en datos del webhook
- **Unit of Work**: Actualizaciones de Pago y Pedido en una sola transacción — atomicidad garantizada
- **State Machine (FSM)**: La transición PENDIENTE → CONFIRMADO se valida contra el mapa de transiciones de CHANGE-10

### Flujo de Datos

```
MercadoPago
    │
    │ POST /api/v1/pagos/webhook
    │ { topic: "payment", id: "1234567890" }
    ▼
WebhookRouter
    │
    ├─► Extraer mp_payment_id del body o query params
    │
    ├─► Validar firma X-Signature
    │       ├─► Inválida → HTTP 403, log, return
    │       └─► Válida → continuar
    │
    │ ⚡ RESPUESTA HTTP 200 INMEDIATA (antes de cualquier procesamiento async)
    │
    ▼
MercadoPagoClient
    │
    └─► GET /v1/payments/{mp_payment_id} vía SDK MP
            │
            ▼
PagoService.procesar_webhook()
    │
    ├─► Buscar Pago por mp_payment_id
    │       ├─► No existe → log error, return (no hace nada)
    │       └─► Existe → continuar
    │
    ├─► Verificar idempotencia: ¿Ya fue procesado este status?
    │       ├─► Mismo status que ya está registrado → log info "already processed", return
    │       └─► Status diferente → continuar
    │
    ├─► Abrir UnitOfWork
    │
    │   UoW.__aenter__()
    │       ├─► Buscar Pedido por pago.pedido_id
    │       ├─► Validar estado actual del pedido (debe ser PENDIENTE)
    │       └─► Si mp_status = approved:
    │               ├─► PedidoService.avanzar_estado(uow, pedido, CONFIRMADO)
    │               │       ├─► Validar transición en FSM
    │               │       ├─► Decrementar stock atómico (SELECT FOR UPDATE)
    │               │       └─► INSERT HistorialEstadoPedido (estado_desde=PENDIENTE)
    │               └─► UPDATE Pago SET mp_status = 'approved'
    │       └─► Si mp_status = rejected/pending/in_process:
    │               └─► UPDATE Pago SET mp_status = [status]
    │
    │   UoW.__aexit__() → commit()
    │
    ▼
Respuesta: void (ya se respondió 200 antes)
```

## Modelo de Datos

### Tabla Pago (existente, ver CHANGE-12)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | PK |
| pedido_id | BIGINT | FK → Pedido |
| monto | DECIMAL(10,2) | Monto del pago |
| mp_payment_id | BIGINT | UQ — ID del pago en MercadoPago |
| mp_status | VARCHAR(30) | pending / approved / rejected / in_process / cancelled |
| mp_status_detail | VARCHAR(50) | Detalle del estado (chdoc, accredited, etc.) |
| external_reference | VARCHAR(100) | UQ — UUID del Pedido |
| idempotency_key | VARCHAR(100) | UQ — UUID generado por backend |
| creado_en | TIMESTAMPTZ | Timestamp de creación |
| actualizado_en | TIMESTAMPTZ | Auto-update |

### Tabla Pedido (existente, ver CHANGE-09)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | PK |
| usuario_id | BIGINT | FK → Usuario |
| estado_codigo | VARCHAR(20) | FK → EstadoPedido |
| total | DECIMAL(10,2) | Total del pedido |
| ... | ... | ... |

### Tabla HistorialEstadoPedido (existente, ver CHANGE-10)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | PK |
| pedido_id | BIGINT | FK → Pedido |
| estado_desde | VARCHAR(20) | FK → EstadoPedido (NULL en primer registro) |
| estado_hacia | VARCHAR(20) | FK → EstadoPedido |
| observaciones | TEXT | nullable |
| creado_en | TIMESTAMPTZ | Auto |
| usuario_id | BIGINT | FK → Usuario (NULL si SISTEMA) |

## APIs

### Endpoint: POST /api/v1/pagos/webhook

**Autenticación**: Ninguna (público) — se valida firma X-Signature en headers

**Request Headers**:
```
X-Signature: <signature>
X-Request-Id: <request_id>
```

**Request Body (form-urlencoded o JSON)**:
```json
{
  "topic": "payment",
  "id": "1234567890"
}
```

**Response**: HTTP 200 (inmediato, antes de procesamiento)
```json
{ "status": "ok" }
```

**Flujo interno asíncrono**:
1. Validar firma
2. Responder 200 inmediatamente
3. Consultar API MP
4. Procesar en UoW

**Códigos de error**:
- HTTP 403: Firma inválida
- HTTP 400: Payload malformado

## Validación de Firma X-Signature

MercadoPago firma las notificaciones con el algoritmo MD5 o SHA256 según configuración. El proceso de validación:

1. Concatenar `v1` + `{id_del_pago}` + `{access_token_mp}`
2. Generar hash SHA256 (o MD5 según config del portal MP)
3. Comparar con el valor de `X-Signature` header

```python
def validar_firma_webhook(mp_payment_id: str, signature: str, generated_signature: str) -> bool:
    """Valida que la firma del webhook proviene de MercadoPago."""
    return signature == generated_signature
```

**Nota**: La validación real usa el secret de MP configurado en variables de entorno.

## Casos de Procesamiento

| mp_status | Acción |
|-----------|--------|
| `approved` | 1. UPDATE Pago SET mp_status='approved'<br>2. PedidoService.avanzar_estado(CONFIRMADO)<br>3. INSERT HistorialEstadoPedido<br>4. Decrementar stock |
| `pending` | 1. UPDATE Pago SET mp_status='pending'<br>2. Log info — pedido permanece PENDIENTE |
| `rejected` | 1. UPDATE Pago SET mp_status='rejected', mp_status_detail='cc_rejected_bad_filled_card'<br>2. Log warning — pedido permanece PENDIENTE |
| `in_process` | 1. UPDATE Pago SET mp_status='in_process'<br>2. Log info — pedido permanece PENDIENTE |
| `cancelled` | 1. UPDATE Pago SET mp_status='cancelled'<br>2. Log warning — pedido permanece PENDIENTE |

## Consideraciones de Seguridad

1. **Validar siempre con API de MP**: Nunca actualizar estado basándose solo en datos del webhook. Consultar `GET /v1/payments/{id}` para confirmar.
2. **Idempotencia**: Si el webhook llega múltiples veces (reintento de MP), el segundo procesamiento debe ser un no-op.
3. **Respuesta inmediata**: Responder HTTP 200 antes de procesar para evitar que MP reintente. El procesamiento real es asíncrono.
4. **Logs**: Registrar todos los webhooks recibidos con nivel INFO (para debugging y auditoría).
5. **Firma inválida**: Si la firma no valida, loguear como WARNING y retornar 403 — no procesar.

## Consideraciones (Trade-offs)

| Decisión | Alternativas | Justificación |
|----------|--------------|---------------|
| Responder 200 antes de procesar | Procesar primero, responder después | MercadoPago reintenta si no recibe 200 en <30s. Mitigado: procesamiento asíncrono post-respuesta. |
| Consultar API MP siempre | Confiar en body del webhook | Más seguro contra ataques de spoofing. Un atacante no puede falsificar el estado real de MP. |
| Idempotencia por mp_payment_id | Por idempotency_key | mp_payment_id es único en tabla Pago (UQ). Si llega el mismo payment dos veces, es duplicado. |

## Notas de Implementación

- El SDK `mercadopago` de Python ya está instalado (CHANGE-12)
- El módulo `pagos` ya existe — este change extiende `service.py` y `router.py`
- La tabla `Pago` ya existe con todos los campos necesarios
- El `UnitOfWork` ya tiene `pagos` y `pedidos` — solo agregar `productos` para decremento de stock
- La FSM del pedido (CHANGE-10) ya valida transiciones y decrementa stock automáticamente

---

**Generado**: 2026-05-13 | **Change**: change-13-mercadopago-webhook-ipn | **Metodología**: SDD