## ADDED Requirements

### Requirement: Rate limiting protects API from excessive requests per IP

The system SHALL enforce rate limits on API requests based on client IP address, rejecting requests exceeding configured thresholds with a 429 Too Many Requests response.

#### Scenario: Login endpoint rate limit (5 requests per 15 minutes)
- **WHEN** a client from IP 192.168.1.100 sends 6 requests to POST /api/v1/auth/login within 15 minutes
- **THEN** the first 5 requests complete successfully, and the 6th request returns 429 with `X-RateLimit-Remaining: 0` and `Retry-After: 900`

#### Scenario: General API rate limit (10 requests per 10 seconds)
- **WHEN** a client from IP 192.168.1.101 sends 11 requests to GET /api/v1/productos within 10 seconds
- **THEN** the first 10 requests complete successfully, and the 11th request returns 429 with appropriate retry headers

#### Scenario: Different IPs have independent limits
- **WHEN** two clients from different IPs (192.168.1.100 and 192.168.1.101) send requests simultaneously
- **THEN** each client's request count is tracked separately, and rate limits apply per IP, not globally

#### Scenario: Rate limit counter resets after window expires
- **WHEN** a client reaches its rate limit at time T, then waits 15 minutes until time T+900s
- **THEN** the client can make new requests and the counter resets to 0

### Requirement: Rate limit status is communicated via headers

The system SHALL include standard HTTP rate limit headers in all API responses to inform clients of their quota status.

#### Scenario: Response includes rate limit headers
- **WHEN** a client receives any API response
- **THEN** the response includes headers: `X-RateLimit-Limit: <limit>`, `X-RateLimit-Remaining: <remaining>`, `X-RateLimit-Reset: <unix_timestamp>`

#### Scenario: Retry-After header is included in 429 response
- **WHEN** a client's request is rate limited (429)
- **THEN** the response includes `Retry-After: <seconds>` indicating when to retry

### Requirement: Rate limit response follows RFC 7807 error format

The system SHALL return rate limit exceeded errors in RFC 7807 Problem Details format, consistent with other API errors.

#### Scenario: 429 response body format
- **WHEN** a client exceeds rate limits and receives 429
- **THEN** the response body contains: `{"type": "...", "title": "Too Many Requests", "status": 429, "detail": "...", "timestamp": "...", "instance": "..."}`

### Requirement: Rate limits are configurable per endpoint family

The system SHALL support different rate limit thresholds for different endpoint families (auth, general, admin).

#### Scenario: Apply decorator with custom limits
- **WHEN** a route handler is decorated with `@limiter.limit("5/15 minutes")` for login
- **THEN** that endpoint enforces the specified 5-per-15-minute limit, independent of other endpoints

#### Scenario: Default limit applies to unmarked endpoints
- **WHEN** an endpoint has no rate limit decorator
- **THEN** it inherits the default rate limit (10 requests per 10 seconds)

### Requirement: Rate limiting can be disabled for testing

The system SHALL provide a mechanism to disable rate limiting via environment variable for non-production environments.

#### Scenario: Disable rate limiting in test environment
- **WHEN** `RATE_LIMIT_ENABLED=false` in environment
- **THEN** all rate limiting middleware is bypassed and requests are not limited

#### Scenario: Rate limiting enabled by default in production
- **WHEN** `RATE_LIMIT_ENABLED` is not set or set to `true`
- **THEN** rate limiting middleware is active and enforces all configured limits
