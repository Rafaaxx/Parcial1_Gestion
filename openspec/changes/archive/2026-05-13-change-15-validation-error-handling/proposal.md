## Why

El proyecto actualmente carece de un manejo de errores estandarizado. Cada endpoint puede devolver errores en formatos distintos, lo cual dificulta el debugging y el manejo en el frontend. Además, no existe una capa de validación y sanitización centralizada para todos los inputs, lo que representa un riesgo de seguridad (XSS, SQL injection potencial si se usan query builders incorrectamente). Implementar RFC 7807 y un middleware global asegurará consistencia, mejor logging y protección básica contra inputs maliciosos.

## What Changes

- **Nueva capability**: Middleware de manejo de errores global que captura todas las excepciones y las formatea según RFC 7807
- **Nueva capability**: Sistema de excepciones personalizadas (ValidationError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, TooManyRequests)
- **Nueva capability**: Pipe/decorador de validación de inputs usando Pydantic (backend ya tiene Pydantic instalado)
- **Nueva capability**: Logging centralizado de errores 500 con trazabilidad (timestamps, path, user_id si está autenticado)
- **Nueva capability**: Sanitización de inputs de texto para prevenir XSS
- **Modificación**: Todos los endpoints existentes migrarán al nuevo formato de errores
- **BREAKING**: El formato de respuesta de error cambiará de `{ message: string }` a formato RFC 7807 estructurado

## Capabilities

### New Capabilities

- `error-handling-middleware`: Middleware global FastAPI que captura todas las excepciones HTTP y de negocio, formateándolas según RFC 7807 con campos: type, title, status, detail, errors[], timestamp, instance
- `custom-exceptions`: Conjunto de excepciones personalizadas que mapean directamente a códigos HTTP (400, 401, 403, 404, 409, 429)
- `input-validation-pydantic`: Validación centralizada de todos los request bodies y query params usando schemas Pydantic existentes en el proyecto
- `input-sanitization`: Decorador/functions para sanitizar strings contra XSS (escape de caracteres HTML)
- `structured-logging`: Logging estructurado para errores 500 que incluye: timestamp ISO8601, path, method, user_id (si existe), request_id, stack trace

### Modified Capabilities

-Ninguna. Todos los endpoints actuales migrarán al nuevo formato de errores sin cambiar su comportamiento.

## Impact

**Affected Modules (Backend)**:
- `backend/app/api/v1/` — Todos los routers requieren actualización de manejo de errores
- `backend/app/core/exceptions.py` — Nuevo archivo para excepciones personalizadas
- `backend/app/core/middleware/` — Nuevo middleware de manejo de errores
- `backend/app/schemas/` — Posible extensión de schemas de error existentes

**Affected Modules (Frontend)**:
- `frontend/src/api/` — Actualizar tipos de error para manejar formato RFC 7807
- `frontend/src/hooks/` — Actualizar error handling en useApiGeneric y wrappers

**Dependencies**:
- Pydantic (ya instalado) — para validación de schemas
- Python `html` module — para sanitización XSS
- Logging configurado (ya existe en backend/.env)

**Testing**:
- Tests de integración para verificar formato de errores en cada tipo de excepción
- Tests unitarios para sanitización de inputs