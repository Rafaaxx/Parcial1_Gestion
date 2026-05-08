## Context

Food Store backend (FastAPI + SQLAlchemy) currently has basic middleware from CHANGE-00a but lacks CORS and rate limiting protections. The frontend (React + Zustand) will make cross-origin requests. The API needs to enforce security boundaries and protect against abuse.

**Current State**:
- Middleware stack exists in `src/core/middleware/`
- No CORS configuration
- No rate limiting
- Environment configuration system is in place (Pydantic Settings)

**Constraints**:
- Must not break existing endpoints or authentication flow
- Rate limits must be configurable per endpoint
- Must support both stateless (IP-based) and stateful (Redis) tracking
- Response format must follow existing RFC 7807 error pattern (from CHANGE-15 design)

## Goals / Non-Goals

**Goals:**
- Prevent unauthorized cross-origin requests with CORS middleware
- Enforce rate limits per IP, with different thresholds for sensitive endpoints (login)
- Return clear rate limit status headers and 429 responses when exceeded
- Make CORS origins and rate limits configurable via environment variables
- Maintain stateless operation (IP-based) with optional Redis fallback
- Provide middleware for easy integration into existing FastAPI app

**Non-Goals:**
- User-based rate limiting (only IP-based for v1)
- Distributed rate limiting across multiple server instances (stateless single-instance for v1)
- Caching of CORS preflight responses (browser handles this)
- Custom rate limit strategies per user role (same limits for all)

## Decisions

### 1. Rate Limiting Library Choice: `slowapi` vs in-memory

**Decision**: Use `slowapi` (production-ready, async-friendly, StarletteLimiter port)

**Rationale**:
- `slowapi` integrates natively with FastAPI/Starlette via decorators
- Supports in-memory storage (v1) with Redis upgrade path (future)
- Provides `@limiter.limit()` decorator syntax, reducing boilerplate
- Well-tested, maintained by community

**Alternative (rejected)**:
- Roll custom in-memory: less testable, reinvents the wheel
- `pyrate-limiter`: overkill complexity for simple IP-based limits
- `aioredis` only: requires Redis, adds operational complexity for v1

### 2. CORS Origins Configuration

**Decision**: Externalize via `CORS_ORIGINS` environment variable (comma-separated), default to `localhost:3000` in dev

**Rationale**:
- Allows safe deployment across environments (dev, staging, prod) without code changes
- Prevents accidental exposure of API to unintended domains
- Follows 12-factor app principles

**Implementation**:
```python
# .env
CORS_ORIGINS=http://localhost:3000,https://foodstore.com,https://www.foodstore.com

# settings.py
cors_origins: list[str] = Field(
    default="http://localhost:3000".split(","),
    description="CORS allowed origins"
)
```

### 3. Rate Limit Storage: In-Memory (v1) with Redis Path

**Decision**: Use in-memory `InMemoryStorage` from `slowapi` for v1; document Redis migration for v2

**Rationale**:
- Single-instance Food Store API (no horizontal scaling planned for v1)
- Simpler operations, fewer dependencies
- Fast local storage lookups
- Documented path to Redis when needed (stateless multi-instance scaling)

**Trade-off**: Limits reset on app restart (acceptable for v1)

### 4. Rate Limit Tiers

**Decision**: Define tiers per endpoint family:

| Endpoint Family | Limit | Window |
|-----------------|-------|--------|
| Auth (login, register) | 5 requests | 15 minutes |
| General API | 10 requests | 10 seconds |
| Admin endpoints | 20 requests | 1 minute |

**Rationale**:
- Brute-force attacks typically slow (~5 guesses/15min)
- General API needs bursty traffic tolerance (rapid reads)
- Admin more trusted internally, less restrictive

**Implementation**: Decorator-based, applied at route level

### 5. Response Headers and 429 Behavior

**Decision**: Return RFC 7231 rate limit headers + RFC 7807 problem detail on 429

**Headers**:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
Retry-After: 300
```

**Body** (429 Too Many Requests):
```json
{
  "type": "https://api.foodstore.com/errors/rate-limit-exceeded",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Retry after 300 seconds.",
  "timestamp": "2026-03-31T10:15:30Z"
}
```

**Rationale**:
- Headers allow smart clients to retry intelligently
- RFC 7807 format consistent with app's error handling (CHANGE-15)
- Retry-After header HTTP standard

### 6. Middleware Integration Order

**Decision**: CORS runs FIRST (preflight response), then Auth, then Rate Limiting

```
Request → CORS (preflight) → Auth → RateLimit → Route → Response
                                                           ↓
                          Add CORS headers to response
```

**Rationale**:
- CORS preflight must not require auth (returns 403 otherwise)
- Auth middleware can identify users for logging
- Rate limit check happens after auth validation

## Risks / Trade-offs

**[Risk]** In-memory storage = limits lost on app restart
- **Mitigation**: Acceptable for v1; document Redis upgrade path for high-availability requirements

**[Risk]** IP-based rate limiting unreliable behind load balancers without X-Forwarded-For
- **Mitigation**: Configure `trust_proxy` in slowapi settings; forward X-Forwarded-For from load balancer

**[Risk]** CORS whitelist misconfiguration could allow unintended origins
- **Mitigation**: Validate `CORS_ORIGINS` at app startup; log warnings for ambiguous values (e.g., `*`)

**[Risk]** Rate limit tiers too restrictive or permissive
- **Mitigation**: Implement telemetry/logging to detect false positives; adjust via env vars at runtime

## Migration Plan

1. **Phase 1** (implementation): Add middleware classes, configure CORS/rate limit settings
2. **Phase 2** (testing): Unit tests for middleware, integration tests for CORS preflight + 429 responses
3. **Phase 3** (deployment):
   - Set `CORS_ORIGINS` to frontend URL in prod environment
   - Deploy with rate limiting enabled
   - Monitor 429 response rates; adjust thresholds if needed
4. **Phase 4** (optional): If scaling → migrate to Redis storage (documented in code)

## Open Questions

- [ ] Should rate limiting be disabled in test environments? (Decision: Yes, via `RATE_LIMIT_ENABLED` env var)
- [ ] Do we need different rate limits for different user roles (ADMIN vs CLIENT)? (Decision: Not in v1; future CHANGE-XX)
- [ ] Should rate limit data be persisted across deployments? (Decision: No, acceptable reset on restart)
