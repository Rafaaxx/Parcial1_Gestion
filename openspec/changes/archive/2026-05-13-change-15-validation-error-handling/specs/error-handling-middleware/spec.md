## ADDED Requirements

### Requirement: Global exception handler returns RFC 7807 format

The system MUST capture all HTTP exceptions and business exceptions raised in any endpoint and return a response in RFC 7807 format with the following fields:
- `type`: URI reference identifying the error type (e.g., `https://api.foodstore.com/errors/validation-error`)
- `title`: Short human-readable summary of the error
- `status`: HTTP status code as integer
- `detail`: Human-readable explanation specific to this occurrence
- `errors`: (optional) Array of field-level validation errors, each with `field` and `message`
- `timestamp`: ISO 8601 datetime of when the error occurred
- `instance`: The path of the request that caused the error
- `requestId`: Unique identifier for the request

#### Scenario: Validation error returns RFC 7807 with field errors
- **WHEN** a Pydantic validation fails on a request body
- **THEN** the response MUST return HTTP 422 with RFC 7807 format containing the array of field errors in the `errors` key

#### Scenario: Not found error returns RFC 7807
- **WHEN** an endpoint raises NotFoundError for a resource
- **THEN** the response MUST return HTTP 404 with RFC 7807 format

#### Scenario: Unauthorized error returns RFC 7807
- **WHEN** an endpoint raises UnauthorizedError due to missing or invalid token
- **THEN** the response MUST return HTTP 401 with RFC 7807 format

### Requirement: Production mode hides implementation details

In production mode (ENVIRONMENT=production), the response MUST NOT expose:
- Python stack traces
- Internal file paths
- Database error messages
- Library-specific error details

The response MUST return a generic message like "An internal error occurred" while logging the full details server-side.

#### Scenario: 500 error in production
- **WHEN** an unhandled exception occurs and ENVIRONMENT=production
- **THEN** the response MUST return HTTP 500 with generic message, hiding stack trace

### Requirement: Request ID injected in all responses

The system MUST generate a unique request ID (UUID v4) at the start of every request and include it in:
- Response headers (`X-Request-ID`)
- Error response body (`requestId` field)
- Log entries for that request

#### Scenario: Request ID present in successful response
- **WHEN** a request completes successfully
- **THEN** the response MUST include `X-Request-ID` header with the generated UUID

#### Scenario: Request ID present in error response
- **WHEN** an error occurs during request processing
- **THEN** the error response MUST include `requestId` matching the original request

### Requirement: Error handler catches all unhandled exceptions

The global exception handler MUST catch any exception that is not explicitly handled, including:
- Generic `Exception`
- KeyboardInterrupt
- SystemExit

For these uncaught exceptions, the handler MUST return HTTP 500 and log the full traceback.

#### Scenario: Unhandled exception returns 500
- **WHEN** a ValueError is raised in a service without a custom exception handler
- **THEN** the response MUST return HTTP 500 with RFC 7807 format