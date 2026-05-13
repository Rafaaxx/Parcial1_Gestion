## ADDED Requirements

### Requirement: ValidationError exception maps to HTTP 422

The system MUST provide a `ValidationError` exception class that:
- Inherits from `Exception` or HTTPException
- Automatically maps to HTTP status code 422
- Accepts a `detail` parameter for the error message
- Accepts an optional `errors` parameter for field-level validation details (list of dicts with `field` and `message`)

#### Scenario: ValidationError raises 422 with details
- **WHEN** code raises `ValidationError(detail="Invalid data", errors=[{"field": "email", "message": "Invalid format"}])`
- **THEN** the response MUST return HTTP 422 with RFC 7807 format including the errors array

### Requirement: UnauthorizedError exception maps to HTTP 401

The system MUST provide an `UnauthorizedError` exception class that:
- Automatically maps to HTTP status code 401
- Accepts a `detail` parameter for the error message
- Is used when authentication fails or is missing

#### Scenario: UnauthorizedError raises 401
- **WHEN** code raises `UnauthorizedError(detail="Invalid or expired token")`
- **THEN** the response MUST return HTTP 401 with RFC 7807 format

### Requirement: ForbiddenError exception maps to HTTP 403

The system MUST provide a `ForbiddenError` exception class that:
- Automatically maps to HTTP status code 403
- Accepts a `detail` parameter for the error message
- Is used when authenticated user lacks permission for the action

#### Scenario: ForbiddenError raises 403
- **WHEN** code raises `ForbiddenError(detail="Insufficient permissions")`
- **THEN** the response MUST return HTTP 403 with RFC 7807 format

### Requirement: NotFoundError exception maps to HTTP 404

The system MUST provide a `NotFoundError` exception class that:
- Automatically maps to HTTP status code 404
- Accepts a `detail` parameter for the error message
- Accepts an optional `resource_type` parameter to identify what was not found

#### Scenario: NotFoundError raises 404
- **WHEN** code raises `NotFoundError(detail="Product not found", resource_type="product")`
- **THEN** the response MUST return HTTP 404 with RFC 7807 format

### Requirement: ConflictError exception maps to HTTP 409

The system MUST provide a `ConflictError` exception class that:
- Automatically maps to HTTP status code 409
- Accepts a `detail` parameter for the error message
- Is used when a resource conflict occurs (duplicate, state violation)

#### Scenario: ConflictError raises 409 for duplicate email
- **WHEN** code raises `ConflictError(detail="Email already registered")`
- **THEN** the response MUST return HTTP 409 with RFC 7807 format

### Requirement: TooManyRequestsError exception maps to HTTP 429

The system MUST provide a `TooManyRequestsError` exception class that:
- Automatically maps to HTTP status code 429
- Accepts a `detail` parameter for the error message
- Accepts an optional `retry_after` parameter for retry guidance
- Is used when rate limiting is exceeded

#### Scenario: TooManyRequestsError raises 429
- **WHEN** code raises `TooManyRequestsError(detail="Rate limit exceeded", retry_after=60)`
- **THEN** the response MUST return HTTP 429 with RFC 7807 format and appropriate headers