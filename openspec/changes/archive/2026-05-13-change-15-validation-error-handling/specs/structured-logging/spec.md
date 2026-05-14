## ADDED Requirements

### Requirement: Error 500 logs include request context

When a 500 error occurs, the system MUST log the following context:
- Timestamp (ISO 8601 format)
- Request method and path
- Request ID (correlation ID)
- User ID (if authenticated)
- Query parameters (sanitized of sensitive data)
- Stack trace
- Request body (only in development mode, never in production)

#### Scenario: 500 error logs full context in development
- **WHEN** a 500 error occurs and DEBUG=True
- **THEN** the log entry MUST include: timestamp, method, path, request_id, user_id, stack trace, and request body

#### Scenario: 500 error logs minimal context in production
- **WHEN** a 500 error occurs and DEBUG=False (production)
- **THEN** the log entry MUST include: timestamp, method, path, request_id, user_id, stack trace, but NOT request body

### Requirement: Structured logging format for errors

All error logs MUST be output in a structured format (JSON) that allows easy parsing by log aggregation systems. The structure MUST include:
- `level`: Log level (ERROR, WARNING, INFO)
- `timestamp`: ISO 8601 datetime
- `message`: Human-readable message
- `request_id`: Correlation ID
- `user_id`: User ID if authenticated (nullable)
- `path`: Request path
- `method`: HTTP method
- `extra`: Additional context-specific fields

#### Scenario: Error log is valid JSON
- **WHEN** an error is logged
- **THEN** the output MUST be parseable as valid JSON

### Requirement: Request ID available throughout request lifecycle

The system MUST make the request ID available to all code executed within a request context, so it can be included in all log entries for that request. This is typically implemented via `contextvars` in Python.

#### Scenario: Request ID propagates to service layer
- **WHEN** an endpoint calls a service method that logs
- **THEN** the service log MUST include the same request_id as the endpoint log

### Requirement: 4xx errors logged at WARNING level

The system MUST log client errors (4xx) at WARNING level, including the error details but NOT the full stack trace.

#### Scenario: 404 error logged at WARNING
- **WHEN** a NotFoundError is raised
- **THEN** the log entry MUST be at WARNING level and include the error details

### Requirement: Sensitive data excluded from logs

The system MUST NEVER log:
- Passwords or password hashes
- JWT access or refresh tokens
- Credit card numbers or payment tokens
- API keys or secrets
- Full request bodies in production

#### Scenario: Password not in logs
- **WHEN** a login request is processed
- **THEN** the password field MUST NOT appear in any log entry