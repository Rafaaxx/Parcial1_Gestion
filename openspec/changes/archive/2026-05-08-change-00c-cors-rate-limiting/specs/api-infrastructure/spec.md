## MODIFIED Requirements

### Requirement: Middleware stack includes CORS and rate limiting

The system's middleware pipeline SHALL include CORS and rate limiting middleware in the correct order: CORS first (to handle preflight), then rate limiting.

#### Scenario: CORS preflight does not require authentication
- **WHEN** browser sends OPTIONS preflight request
- **THEN** CORS middleware responds immediately without requiring authentication or rate limit checks

#### Scenario: Rate limiting applies after CORS to all regular requests
- **WHEN** client sends a regular request (POST, GET, PUT, etc.)
- **THEN** CORS headers are applied, then rate limiting is checked, then route handler is called

#### Scenario: Middleware order is: CORS → Auth → RateLimit → Route
- **WHEN** a valid request passes through the middleware stack
- **THEN** each middleware layer processes and passes control to the next layer in the correct order

### Requirement: Settings module exposes CORS and rate limit configuration

The system's Pydantic Settings class SHALL include configuration fields for CORS origins and rate limit settings.

#### Scenario: CORS origins from environment
- **WHEN** the application initializes
- **THEN** it reads CORS_ORIGINS environment variable and populates `settings.cors_origins: list[str]`

#### Scenario: Rate limit configuration from environment
- **WHEN** the application initializes
- **THEN** it reads RATE_LIMIT_ENABLED, RATE_LIMIT_WINDOW_SECONDS, and rate limit thresholds from environment variables

#### Scenario: Settings are validated at startup
- **WHEN** invalid CORS configuration (e.g., empty origins list in production)
- **THEN** the system logs a warning but continues (allows dev flexibility)

### Requirement: API infrastructure supports easy middleware registration

The system's FastAPI app initialization code SHALL provide a clean interface to register CORS and rate limit middleware.

#### Scenario: CORS middleware is registered early in app creation
- **WHEN** the app starts
- **THEN** CORSMiddleware is registered before all other middleware

#### Scenario: Rate limiting middleware is registered after auth
- **WHEN** the app starts
- **THEN** rate limiting middleware is registered after authentication middleware

#### Scenario: Middleware can be toggled via settings
- **WHEN** `RATE_LIMIT_ENABLED=false` is set
- **THEN** the rate limiting middleware is not registered, and all requests bypass the rate limiter
