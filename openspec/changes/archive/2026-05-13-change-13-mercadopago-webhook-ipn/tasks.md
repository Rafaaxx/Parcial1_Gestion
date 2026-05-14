# Tasks: change-13-mercadopago-webhook-ipn

Lista de tareas atómicas para implementar `change-13-mercadopago-webhook-ipn`.

**Reglas:**
- Cada tarea < 3 horas
- Prohibido tocar repo remoto (CERO push/pull/merge)
- Tests requieren PostgreSQL real

---

## Fase 1: Configuración y Cliente MP

### Tarea 1: Extender mp_client.py con consulta de estado
- **Archivo**: `app/modules/pagos/mp_client.py`
- **Acción**: Agregar método `get_payment_status(mp_payment_id: str) -> dict` que consulta `GET /v1/payments/{id}` vía SDK MP
- **Validación**: Test que mockea SDK y verifica que se llama a la API correcta
- **Tiempo estimado**: 1h

### Tarea 2: Agregar validación de firma webhook
- **Archivo**: `app/modules/pagos/mp_client.py`
- **Acción**: Crear función `validar_firma_webhook(mp_payment_id, x_signature, x_request_id) -> bool` usando SHA256
- **Validación**: Test con firma válida e inválida
- **Tiempo estimado**: 1h

---

## Fase 2: Extender Repository de Pago

### Tarea 3: Agregar método get_by_mp_payment_id
- **Archivo**: `app/repositories/pago_repository.py`
- **Acción**: Crear método `get_by_mp_payment_id(mp_payment_id: int) -> Pago | None`
- **Validación**: Query correcta con filtro por mp_payment_id
- **Tiempo estimado**: 30min

### Tarea 4: Agregar método update_mp_status
- **Archivo**: `app/repositories/pago_repository.py`
- **Acción**: Crear método `update_mp_status(pago_id: int, status: str, status_detail: str | None) -> Pago`
- **Validación**: UPDATE correcto y retorna entidad actualizada
- **Tiempo estimado**: 30min

---

## Fase 3: Extender Unit of Work

### Tarea 5: Agregar property productos al UoW
- **Archivo**: `app/uow.py`
- **Acción**: Agregar `productos: ProductoRepository` al `UnitOfWork` (necesario para decremento de stock)
- **Validación**: `uow.productos` retorna ProductoRepository
- **Tiempo estimado**: 30min

---

## Fase 4: Extender Servicio de Pago

### Tarea 6: Crear método procesar_webhook
- **Archivo**: `app/modules/pagos/service.py`
- **Acción**: Implementar `procesar_webhook(uow: UnitOfWork, mp_payment_id: int) -> None`:
  1. Buscar Pago por mp_payment_id (Tarea 3)
  2. Verificar idempotencia (si ya fue procesado → return)
  3. Consultar API MP para obtener estado real (Tarea 1)
  4. Abrir UoW dentro del método (o recibirlo como parámetro)
  5. UPDATE Pago con nuevo status
  6. Si approved y pedido.estado = PENDIENTE → avanzar a CONFIRMADO
- **Validación**: Tests con mock de MP Client — approved, rejected, pending, duplicado
- **Tiempo estimado**: 3h

### Tarea 7: Integrar FSM en procesamiento
- **Archivo**: `app/modules/pagos/service.py`
- **Acción**: Al procesar `approved`, llamar a `PedidoService` para avanzar estado con decremento de stock
- **Validación**: Test que verifica que se llama a FSM y se decrementa stock
- **Tiempo estimado**: 1h

---

## Fase 5: Endpoint Webhook en Router

### Tarea 8: Crear endpoint POST /pagos/webhook
- **Archivo**: `app/modules/pagos/router.py`
- **Acción**: Implementar endpoint:
  ```python
  @router.post("/webhook")
  async def webhook_mp(request: Request):
      # 1. Extraer topic e id del body
      # 2. Validar firma X-Signature
      # 3. Responder HTTP 200 inmediatamente
      # 4. En background/async: procesar_webhook()
  ```
- **Validación**: Endpoint responde 200 en <100ms, procesamiento es asíncrono
- **Tiempo estimado**: 2h

### Tarea 9: Registrar router en main.py
- **Archivo**: `app/main.py`
- **Acción**: Verificar que router de pagos está registrado con prefijo `/api/v1/pagos`
- **Validación**: Swagger UI muestra `POST /api/v1/pagos/webhook`
- **Tiempo estimado**: 15min

---

## Fase 6: Tests de Integración

### Tarea 10: Fixture de webhook
- **Archivo**: `tests/conftest.py`
- **Acción**: Crear fixture `webhook_mp_approved()` que retorna payload de webhook MP (approved)
- **Validación**: Fixture genera payload consistente con formato real de MP
- **Tiempo estimado**: 30min

### Tarea 11: Tests de integración webhook
- **Archivo**: `tests/integration/test_pagos_webhook.py` (nuevo)
- **Acción**: Tests:
  - Webhook approved → pedido avanza a CONFIRMADO, stock decrementa
  - Webhook rejected → pago actualizado, pedido permanece PENDIENTE
  - Webhook duplicate → segundo llamado es no-op (idempotencia)
  - Firma inválida → HTTP 403, no se procesa
  - Pago no existe → log error, no crash
- **Validación**: Todos los tests pasan con PostgreSQL
- **Tiempo estimado**: 3h

---

## Fase 7: Verificación y Logging

### Tarea 12: Agregar logging estructurado
- **Archivo**: `app/modules/pagos/service.py`, `app/modules/pagos/router.py`
- **Acción**: Agregar logs:
  - `INFO`: Webhook recibido con topic={}, id={}
  - `INFO`: Procesando pago mp_id={}, status={}
  - `INFO`: Pago idempotente, ya procesado - status={}
  - `WARNING`: Firma inválida en webhook
  - `ERROR`: Pago no encontrado para mp_id={}
- **Validación**: Logs aparecen en output de pytest con formato correcto
- **Tiempo estimado**: 30min

### Tarea 13: Test manual end-to-end
- **Acción**: Simular webhook real con curl o Postman
- **Validación**:
  1. Crear pedido (estado PENDIENTE)
  2. Crear pago asociado
  3. Enviar webhook con topic=payment, id={mp_payment_id}
  4. Verificar que pedido avanza a CONFIRMADO
  5. Verificar que stock decrementó
- **Tiempo estimado**: 30min

---

## Resumen de Tareas

| # | Tarea | Archivo | Tiempo |
|---|-------|---------|--------|
| 1 | mp_client: get_payment_status() | `app/modules/pagos/mp_client.py` | 1h |
| 2 | mp_client: validar_firma_webhook() | `app/modules/pagos/mp_client.py` | 1h |
| 3 | PagoRepository: get_by_mp_payment_id() | `app/repositories/pago_repository.py` | 30min |
| 4 | PagoRepository: update_mp_status() | `app/repositories/pago_repository.py` | 30min |
| 5 | UoW: agregar property productos | `app/uow.py` | 30min |
| 6 | PagoService: procesar_webhook() | `app/modules/pagos/service.py` | 3h |
| 7 | PagoService: integrar FSM | `app/modules/pagos/service.py` | 1h |
| 8 | Router: endpoint /webhook | `app/modules/pagos/router.py` | 2h |
| 9 | main.py: verificar registro | `app/main.py` | 15min |
| 10 | Fixture webhook | `tests/conftest.py` | 30min |
| 11 | Tests integración | `tests/integration/test_pagos_webhook.py` | 3h |
| 12 | Logging estructurado | `app/modules/pagos/*.py` | 30min |
| 13 | Test manual end-to-end | — | 30min |
| | **TOTAL** | | **~16h** |

---

## Dependencias

- CHANGE-12: Tabla Pago, SDK MercadoPago, endpoint crear pago
- CHANGE-10: FSM de pedidos, decremento de stock
- CHANGE-09: Modelo Pedido, UnitOfWork base

## Notas de Implementación

1. **Respuesta inmediata**: El endpoint DEBE responder 200 antes de procesar. El procesamiento se hace en background task de FastAPI (`asyncio.create_task`).
2. **Idempotencia**: Verificar `pago.mp_status` antes de procesar. Si ya está `approved` y llega de nuevo `approved`, es no-op.
3. **API MP real**: Consultar siempre la API de MP para obtener el estado real. No confiar en el body del webhook.
4. **FSM ya existe**: La transición PENDIENTE → CONFIRMADO con decremento de stock ya está implementada en CHANGE-10. Reusar.
5. **MercadoPago SDK**: Usar `mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)` para consultas.

---

**Generado**: 2026-05-13 | **Change**: change-13-mercadopago-webhook-ipn | **Metodología**: SDD