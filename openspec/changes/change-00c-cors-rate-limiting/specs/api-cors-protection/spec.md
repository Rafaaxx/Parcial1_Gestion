## ADDED Requirements

### Requirement: CORS middleware validates origin on cross-origin requests

The system SHALL verify that requests from cross-origin domains are from whitelisted origins and reject others with appropriate HTTP status.

#### Scenario: Allowed origin receives CORS headers
- **WHEN** a browser from `http://localhost:3000` sends a request to the API
- **THEN** the response includes `Access-Control-Allow-Origin: http://localhost:3000` and request completes normally

#### Scenario: Disallowed origin is rejected
- **WHEN** a browser from `http://attacker.com` sends a request to the API
- **THEN** the browser enforces CORS policy and blocks the response (no `Access-Control-Allow-Origin` header for that origin)

#### Scenario: OPTIONS preflight request is handled
- **WHEN** a browser sends an OPTIONS preflight request for a POST to `/api/v1/produtos`
- **THEN** the CORS middleware responds with 200, including all required CORS headers, without calling the route handler

### Requirement: CORS headers support credential-based authentication

The system SHALL configure CORS to allow credentials (cookies, Authorization headers) in cross-origin requests, enabling JWT-based auth from frontend.

#### Scenario: Credentials are included in cross-origin request
- **WHEN** frontend sends a request with `credentials: 'include'` and valid JWT in Authorization header
- **THEN** the API receives the header, processes it, and includes `Access-Control-Allow-Credentials: true` in response

#### Scenario: Preflight allows Authorization header
- **WHEN** a browser sends OPTIONS preflight requesting `Authorization` header
- **THEN** CORS middleware responds with `Access-Control-Allow-Headers: ..., Authorization, ...`

### Requirement: CORS origins are configurable via environment variable

The system SHALL allow administrators to specify allowed origins through environment configuration, enabling safe deployment across environments.

#### Scenario: Parse comma-separated origins from environment
- **WHEN** `CORS_ORIGINS=http://localhost:3000,https://foodstore.com,https://www.foodstore.com` is set
- **THEN** the CORS middleware accepts requests from all three origins and rejects others

#### Scenario: Default origins for development
- **WHEN** `CORS_ORIGINS` environment variable is not set
- **THEN** the system defaults to `http://localhost:3000` for safe development setup

#### Scenario: Production requires explicit configuration
- **WHEN** the system starts in production mode
- **THEN** CORS_ORIGINS must be set; if empty or wildcard `*`, log a security warning

### Requirement: CORS exposes necessary response headers for pagination and metadata

The system SHALL include important headers in the `Access-Control-Expose-Headers` list so frontend JavaScript can read them.

#### Scenario: Frontend reads pagination metadata
- **WHEN** frontend makes GET /api/v1/productos request with pagination
- **THEN** response includes `X-Total-Count` and `X-Page-Number` in Access-Control-Expose-Headers, allowing JavaScript to read them

#### Scenario: Frontend reads rate limit headers
- **WHEN** frontend receives an API response
- **THEN** response includes `X-RateLimit-*` headers in Access-Control-Expose-Headers, allowing JavaScript monitoring

### Requirement: CORS configuration handles HTTP and HTTPS variations

The system SHALL correctly recognize and differentiate between http:// and https:// variants of domains in the origins list.

#### Scenario: HTTP and HTTPS variants are distinct
- **WHEN** `CORS_ORIGINS=http://localhost:3000,https://foodstore.com` is set
- **THEN** requests from `http://localhost:3000` are allowed, but `https://localhost:3000` is not (and vice versa for foodstore.com)
