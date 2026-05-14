## ADDED Requirements

### Requirement: Global Pydantic validation pipe processes all request bodies

The system MUST use FastAPI's dependency injection to ensure all request bodies are validated against their Pydantic schemas before reaching the endpoint handler. This MUST happen automatically for all endpoints without explicit per-endpoint configuration.

#### Scenario: Invalid request body returns 422
- **WHEN** a POST request sends a body that fails Pydantic validation
- **THEN** the request MUST be rejected with HTTP 422 before reaching the endpoint logic

#### Scenario: Valid request body passes validation
- **WHEN** a request sends a body that satisfies all Pydantic constraints
- **THEN** the request MUST proceed to the endpoint handler with the parsed data

### Requirement: Query parameters validated with Pydantic

The system MUST support validation of query parameters using Pydantic models via FastAPI's `Query` dependencies. Invalid query params MUST return HTTP 422.

#### Scenario: Invalid query parameter returns 422
- **WHEN** a GET request includes a query parameter that fails validation (e.g., non-integer where integer expected)
- **THEN** the response MUST return HTTP 422 with RFC 7807 format explaining the validation error

### Requirement: Path parameters validated with Pydantic

The system MUST support validation of path parameters using Pydantic models via FastAPI's `Path` dependencies. Invalid path params MUST return HTTP 422.

#### Scenario: Invalid path parameter type returns 422
- **WHEN** a request accesses `/api/v1/productos/abc` where ID must be integer
- **THEN** the response MUST return HTTP 422 with error message indicating invalid ID format

### Requirement: Custom validation logic in Pydantic validators

The system MUST allow custom validation logic defined within Pydantic models using the `@field_validator` decorator. This validation MUST execute as part of the standard validation flow.

#### Scenario: Custom validator rejects invalid email domain
- **WHEN** a user registers with email from a blocked domain, and a custom validator checks for this
- **THEN** Pydantic MUST raise a validation error that results in HTTP 422

### Requirement: All numeric inputs validated as numbers

The system MUST reject non-numeric values for fields defined as numeric types (int, float) in Pydantic schemas. This MUST return HTTP 400 (bad request) rather than a validation error.

#### Scenario: Non-numeric value in numeric field
- **WHEN** a request includes `precio="abc"` where the schema expects a numeric type
- **THEN** the response MUST return HTTP 400 with appropriate error message