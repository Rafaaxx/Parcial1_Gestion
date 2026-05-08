## Why

Security and robustness are fundamental to any production API. CHANGE-00c establishes the critical middleware layer for **Cross-Origin Resource Sharing (CORS)** and **rate limiting**, protecting the backend from common threats (unauthorized cross-origin requests, brute-force attacks, abuse) while enabling the frontend to communicate securely with the API.

Without these protections, the Food Store API would be vulnerable to:
- Cross-origin attacks from malicious domains
- Brute-force login attempts (already designed in CHANGE-01 auth but not enforced here)
- DoS attacks through unbounded request volume
- Accidental client-side misconfigurations causing failures

## What Changes

- **CORS Middleware**: Whitelist specific origins (frontend domains), allow credentials, expose headers for pagination
- **Rate Limiting Middleware**: Enforce request quotas per IP address (5/15min for login endpoint, 10/10sec for general API)
- **Rate Limit Headers**: Return `X-RateLimit-*` headers to clients for transparency
- **Error Responses**: 429 Too Many Requests with retry-after guidance
- **Configuration**: Externalize CORS domains and rate limits to environment variables for flexibility across environments

## Capabilities

### New Capabilities
- `api-rate-limiting`: Rate limiting by IP address with configurable windows (general: 10req/10sec, login: 5req/15min) and 429 response handling
- `api-cors-protection`: CORS middleware with whitelist validation, credential handling, and exposed headers

### Modified Capabilities
- `api-infrastructure`: Integrate rate limiting and CORS into the base API middleware stack (modifies existing middleware chain from CHANGE-00a)

## Impact

- **Backend**: FastAPI middleware added to `src/core/middleware/`
- **API**: All endpoints return CORS headers; authentication endpoints include rate limit tracking
- **Environment**: New vars: `CORS_ORIGINS`, `RATE_LIMIT_ENABLED`, `RATE_LIMIT_STORAGE` (Redis or in-memory)
- **Frontend**: No breaking changes; existing CORS headers will allow credentials and preflight requests
- **Dependencies**: `slowapi` or `python-ratelimit` (TBD in design)
- **Testing**: Middleware unit tests, integration tests for CORS preflight, rate limit exhaustion scenarios
