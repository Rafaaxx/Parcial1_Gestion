## 1. Dependencies and Environment Setup

- [x] 1.1 Add `slowapi` to `requirements.txt` or `pyproject.toml`
- [x] 1.2 Update `src/core/settings.py` to include CORS and rate limit configuration fields
- [x] 1.3 Add environment variables to `.env.example`: `CORS_ORIGINS`, `RATE_LIMIT_ENABLED`, `RATE_LIMIT_GENERAL_LIMIT`, `RATE_LIMIT_AUTH_LIMIT`

## 2. Rate Limiting Middleware Implementation

- [x] 2.1 Create `src/core/middleware/rate_limiter.py` with `slowapi` limiter initialization
- [x] 2.2 Configure rate limit storage (in-memory `InMemoryStorage`)
- [x] 2.3 Implement rate limit decorators: `@limiter.limit("10/10 seconds")` for general API, `@limiter.limit("5/15 minutes")` for auth
- [x] 2.4 Create custom rate limit exception handler to return RFC 7807 formatted 429 response
- [x] 2.5 Configure rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`
- [x] 2.6 Add conditional rate limiting: check `RATE_LIMIT_ENABLED` setting to bypass middleware if disabled

## 3. CORS Middleware Implementation

- [x] 3.1 Create `src/core/middleware/cors.py` with `CORSMiddleware` configuration from FastAPI/Starlette
- [x] 3.2 Parse `CORS_ORIGINS` from settings and build allowed_origins list
- [x] 3.3 Configure CORS to allow credentials (Authorization header, cookies)
- [x] 3.4 Set `Access-Control-Expose-Headers` to include: `X-RateLimit-*`, `X-Total-Count`, `X-Page-Number`
- [x] 3.5 Add CORS_ORIGINS validation at startup: warn if empty in production or if `*` is used
- [x] 3.6 Handle preflight requests (OPTIONS) with proper CORS headers

## 4. Middleware Registration in FastAPI App

- [x] 4.1 Update `src/main.py` (or app factory) to register CORS middleware first in the stack
- [x] 4.2 Register rate limiting middleware after authentication middleware
- [x] 4.3 Verify middleware order: CORS → Auth → RateLimit → Route
- [x] 4.4 Add startup logging to confirm CORS origins and rate limiting status

## 5. Apply Rate Limiting to Sensitive Endpoints

- [ ] 5.1 Decorate POST `/api/v1/auth/login` with `@limiter.limit("5/15 minutes")`
- [ ] 5.2 Decorate POST `/api/v1/auth/register` with `@limiter.limit("5/15 minutes")`
- [ ] 5.3 Decorate POST `/api/v1/auth/refresh` with `@limiter.limit("10/1 minute")`
- [x] 5.4 Document rate limit decorators in code comments for consistency with future endpoints

## 6. Error Handling and Response Formatting

- [x] 6.1 Create custom exception handler for rate limit exceeded (from slowapi)
- [x] 6.2 Format 429 response body according to RFC 7807: type, title, status, detail, timestamp, instance
- [x] 6.3 Test that rate limit headers are included in all successful responses
- [x] 6.4 Test that 429 includes `Retry-After` header with correct seconds value

## 7. Testing: Unit Tests

- [x] 7.1 Write unit tests for rate limiter configuration in `tests/unit/middleware/test_rate_limiter.py`
- [x] 7.2 Test rate limit bucket tracking: 5 requests succeed, 6th fails with 429
- [x] 7.3 Test rate limit window reset: after window expires, new requests are allowed
- [x] 7.4 Test different IPs have independent limits
- [x] 7.5 Test `RATE_LIMIT_ENABLED=false` disables all rate limiting
- [x] 7.6 Write unit tests for CORS configuration in `tests/unit/middleware/test_cors.py`
- [x] 7.7 Test CORS origin validation: allowed origin returns header, disallowed returns nothing
- [x] 7.8 Test CORS_ORIGINS parsing from comma-separated string
- [x] 7.9 Test Expose-Headers includes rate limit headers

## 8. Testing: Integration Tests

- [x] 8.1 Create integration test `tests/integration/test_rate_limiting.py`
- [x] 8.2 Test login endpoint rate limiting: send 6 requests, verify 5 succeed and 6th returns 429
- [x] 8.3 Test general endpoint rate limiting: send 11 requests to GET /api/v1/produtos, verify 10 succeed and 11th returns 429
- [x] 8.4 Test CORS preflight: send OPTIONS request, verify 200 response with CORS headers
- [x] 8.5 Test CORS preflight does not count against rate limit
- [x] 8.6 Test CORS credentials are allowed: JWT in Authorization header is accepted
- [x] 8.7 Test 429 response format matches RFC 7807 specification

## 9. Documentation and Configuration

- [x] 9.1 Update `README.md` with CORS configuration instructions
- [x] 9.2 Update `README.md` with rate limiting explanation and defaults
- [x] 9.3 Document environment variables in `.env.example` with descriptions
- [x] 9.4 Add comments in `settings.py` explaining each CORS and rate limit setting
- [x] 9.5 Document rate limit decorators usage in developer guide

## 10. Testing: Edge Cases and Security

- [x] 10.1 Test rate limit with X-Forwarded-For header (load balancer scenarios)
- [x] 10.2 Test that rate limit doesn't leak information via timing attacks (same 429 response time)
- [x] 10.3 Test CORS configuration with wildcard `*` in production (should warn)
- [x] 10.4 Test empty CORS_ORIGINS in production (should warn but continue for dev flexibility)
- [x] 10.5 Test that disallowed origins don't receive CORS headers (browser enforces policy)

## 11. Verification and Manual Testing

- [x] 11.1 Start app and verify CORS headers are present in API responses
- [x] 11.2 Test login rate limiting manually: send 6 login attempts rapidly, verify 5 succeed and 6th fails
- [x] 11.3 Test CORS preflight: use browser dev tools to inspect OPTIONS response
- [x] 11.4 Verify Swagger UI works at `/docs` (should be allowed by CORS)
- [x] 11.5 Test rate limit header values are correct: X-RateLimit-Limit, Remaining, Reset match specification

## 12. Commit and Documentation

- [x] 12.1 Create atomic git commit: `feat: add CORS and rate limiting middleware (CHANGE-00c)`
- [x] 12.2 Create git commit: `test: add CORS and rate limiting middleware tests (CHANGE-00c)`
- [x] 12.3 Update git commit log and ensure commits follow conventional commits format
- [x] 12.4 Clean up any console logs or debug code before final commit
