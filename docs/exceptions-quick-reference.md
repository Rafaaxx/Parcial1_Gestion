# Quick Reference: Custom Exceptions

Guía rápida para usar las excepciones personalizadas del proyecto Food Store.

## Imports

```python
from app.exceptions import (
    AppException,
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    DatabaseError,
)
```

## Lanzar una Excepción

### ValidationError (422 - Unprocessable Entity)

```python
# Validación de datos de entrada
raise ValidationError(
    message="El nombre del producto es requerido",
    detail={"errors": [{"field": "nombre", "message": "Campo requerido"}]}
)
```

### NotFoundError (404 - Not Found)

```python
# Recurso no encontrado
raise NotFoundError(
    message="El producto no existe",
    resource="Producto"
)
# -> detail: {"resource": "Producto"}
```

### ConflictError (409 - Conflict)

```python
# Conflicto de datos (ej: duplicado)
raise ConflictError(
    message="Ya existe un producto con ese nombre",
    detail={"field": "nombre", "value": "Pizza Margherita"}
)
```

### UnauthorizedError (401 - Unauthorized)

```python
# Autenticación fallida
raise UnauthorizedError("Token de acceso inválido")
```

### ForbiddenError (403 - Forbidden)

```python
# Permisos insuficientes
raise ForbiddenError("No tienes permiso para eliminar productos")
```

### RateLimitError (429 - Too Many Requests)

```python
# Límite de requests excedido
raise RateLimitError(
    message="Demasiadas solicitudes",
    retry_after=900  # segundos
)
```

### DatabaseError (500 - Internal Server Error)

```python
# Error de base de datos
raise DatabaseError(
    message="Error al guardar el pedido",
    detail={"operation": "insert", "table": "pedidos"}
)
```

### AppException genérica

```python
# Para otros casos
raise AppException(
    message="Algo salió mal",
    status_code=400,
    error_code="CUSTOM_ERROR",
    detail={"extra": "información"}
)
```

## Respuesta JSON (RFC 7807)

Todas las excepciones devuelven formato RFC 7807:

```json
{
  "type": "https://api.foodstore.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "El nombre del producto es requerido",
  "timestamp": "2026-05-13T12:00:00Z",
  "instance": "/api/v1/productos",
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "errors": [
    {"field": "nombre", "message": "Campo requerido"}
  ]
}
```

## Request ID

Cada request tiene un `X-Request-ID` header automatico. Acceder desde request:

```python
from fastapi import Request

@router.get("/endpoint")
async def endpoint(request: Request):
    request_id = request.state.request_id  # UUID automático
    return {"request_id": request_id}
```

## Sanitización de Input

Para prevenir XSS en datos del usuario:

```python
from app.sanitization import sanitize_string, sanitize_dict

# Sanitizar un string
safe_input = sanitize_string(user_input)

# Sanitizar un dict recursivamente
safe_data = sanitize_dict({"nombre": user_input, "bio": user_bio})
```

## Testing

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validation_error_response():
    response = client.post("/api/v1/productos", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["title"] == "Validation Error"
    assert data["type"].startswith("https://api.foodstore.com/errors/")
```

## Estado de Implementación

| Excepción | Handler | Tests |
|-----------|---------|-------|
| ValidationError | ✅ | ✅ |
| NotFoundError | ✅ | ✅ |
| ConflictError | ✅ | ✅ |
| UnauthorizedError | ✅ | ✅ |
| ForbiddenError | ✅ | ✅ |
| RateLimitError | ✅ | ✅ |
| DatabaseError | ✅ | - |
| RequestValidationError (Pydantic) | ✅ | ✅ |

## Ubicación de Archivos

- Excepciones: `backend/app/exceptions.py`
- Handlers: `backend/app/handlers.py`
- Sanitización: `backend/app/sanitization.py`
- Middleware Request ID: `backend/app/middleware/request_id.py`
- Tests: `backend/tests/test_error_handling/`