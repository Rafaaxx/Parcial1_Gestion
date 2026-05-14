## Context

El backend de Food Store actualmente no tiene un sistema centralizado de manejo de errores. Cada endpoint puede lanzar excepciones que se traducen a respuestas HTTP de manera inconsistente. El frontend recibe errores con formato variado, dificultando el manejo uniforme. Además, no existe validación centralizada de inputs más allá de lo que Pydantic ya hace en los schemas existentes.

**Estado actual**:
- FastAPI maneja errores HTTP nativos y validaciones Pydantic
- No hay middleware de excepciones global personalizado
- Errores 500 exponen stack traces en desarrollo
- No hay sanitización de strings contra XSS
- Logging existe pero no está estructurado para errores

**Stakeholders**: Desarrolladores backend, equipo frontend, QA

## Goals / Non-Goals

**Goals:**
- Implementar formato RFC 7807 en todas las respuestas de error del backend
- Crear excepciones personalizadas que mapeen directamente a códigos HTTP
- Agregar middleware global de manejo de errores
- Implementar sanitización de inputs de texto
- Logging estructurado para errores 500 con request context

**Non-Goals:**
- No se implementará validación de negocio (esa va en los services)
- No se modifica el comportamiento de los endpoints, solo el formato de errores
- No se implementa autenticación de webhooks (ya existe en change-12)
- No se cambia la estructura de la base de datos
- No se implementa rate limiting adicional (ya existe en change-00c)

## Decisions

### D1: Usar FastAPI exception_handler en lugar de Starlette middleware

**Alternativas consideradas**:
- Starlette custom middleware (más bajo nivel)
- Decoradores por endpoint (repetitivo, no escalable)

**Rationale**: FastAPI tiene integrado el sistema de exception_handlers que permite mapear excepciones específicas a respuestas HTTP específicas. Es más declarativo y menos invasivo que un middleware completo. Además, se integra naturalmente con el sistema de dependencias y lifespan.

### D2: Formato RFC 7807 con campo "errors" para validaciones

**Alternativas consideradas**:
- Formato simple `{ statusCode, message }` (propuesto originalmente en US-068)
- Solo field-level errors sin campo "errors" array

**Rationale**: RFC 7807 permite un array `errors[]` para validaciones detalladas por campo. Esto es más rico que el formato simple y permite al frontend mostrar errores específicos al lado de cada campo del formulario. El campo `detail` se usa para errores generales.

### D3: Usar library `html` de Python para sanitización XSS

**Alternativas consideradas**:
- `bleach` (más completo pero más pesado)
- Regex manual (propenso a errores)

**Rationale**: La library estándar `html` con `escape()` es suficiente para sanitización básica de XSS en strings. No requiere dependencias adicionales y cubre el caso de uso de inputs de usuario que se renderizan en respuestas JSON (no HTML directo). Para casos complejos se puede extender después.

### D4: Logging estructurado con formato JSON

**Alternativas consideradas**:
- Logging textual con formato personalizado
- Integración con sistema de logging de FastAPI

**Rationale**: FastAPI usa Python logging estándar. Vamos a configurar un handler que outputee JSON para errores 500, manteniendo logs legibles para desarrollo y JSON para producción. Esto permite integración con sistemas de monitoreo.

### D5: Request ID obligatorio para trazabilidad

**Alternativas consideradas**:
- Request ID opcional
- Solo usar correlation ID de headers

**Rationale**: Para debugging efectivo, cada request debe tener un ID único. Usaremos un middleware que genera un UUID al inicio de cada request y lo expone en el header `X-Request-ID`. Esto permite correlacionar logs de errores con requests específicos.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| **R1: Breaking change en formato de errores** | Alto | Frontend necesita actualizar tipos de error. Se provee guía de migración. |
| **R2: Performance por sanitización en cada input** | Bajo | Solo sanitizar strings, no apply a todo el objeto. Espera mínima (<1ms). |
| **R3: Pérdida de información de errores en producción** | Medio | Mantener verbose logging en DEBUG=True, simplificar en producción. |
| **R4: Excepciones no mapeadas quedan como 500** | Bajo | catches genérico para cualquier Exception, pero con mensaje genérico al cliente. |

## Migration Plan

1. **Fase 1**: Crear archivo `backend/app/core/exceptions.py` con todas las excepciones personalizadas
2. **Fase 2**: Crear archivo `backend/app/core/handlers.py` con exception handlers para FastAPI
3. **Fase 3**: Registrar handlers en `backend/app/main.py`
4. **Fase 4**: Agregar request_id middleware
5. **Fase 5**: Crear utility de sanitización en `backend/app/core/sanitization.py`
6. **Fase 6**: Actualizar logging configuration en `backend/app/core/logging_config.py`
7. **Fase 7**: Tests de integración verificando formato de errores
8. **Fase 8**: Documentar cambio para frontend

**Rollback**: Si hay errores en producción, el middleware de errores puede deshabilitarse comentando su registro en main.py, revertiendo al comportamiento por defecto de FastAPI (aunque sin formato RFC 7807).

## Open Questions

- **Q1**: ¿El frontend quiere mostrar los campos `type` y `title` del RFC 7807 al usuario final, o solo el `detail`?
- **Q2**: ¿Se debe incluir el campo `instance` (path del request) en producción o es información sensible?
- **Q3**: ¿Hay algún sistema de monitoreo (Sentry, DataDog) ya integrado que necesitemos configurar para errores 500?

## Technical Implementation Preview

```
backend/app/core/
├── exceptions.py        # Custom exceptions (ValidationError, etc.)
├── handlers.py          # Exception handlers mapping
├── middleware/
│   └── request_id.py    # Request ID middleware
├── sanitization.py      # XSS escape utilities
└── logging_config.py    # Structured logging setup

backend/app/main.py      # Registrar exception handlers
```

Formato de respuesta de error:
```json
{
  "type": "https://api.foodstore.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Error de validación en los datos ingresados",
  "errors": [
    { "field": "email", "message": "Email inválido" },
    { "field": "password", "message": "Debe tener al menos 8 caracteres" }
  ],
  "timestamp": "2026-05-13T14:30:00Z",
  "instance": "/api/v1/auth/register",
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```