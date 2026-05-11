## ADDED Requirements

### Requirement: Axios HTTP Client Initialization
The system SHALL provide an initialized Axios instance with custom configuration, timeout, and base URL pointing to the backend API.

#### Scenario: API client connects to backend
- **WHEN** the frontend app starts
- **THEN** Axios is configured with `baseURL=http://localhost:8000/api/v1` (dev) and `http://api.foodstore.com/api/v1` (prod)

#### Scenario: Requests include timeout
- **WHEN** an HTTP request is made
- **THEN** it times out after 30 seconds if no response

### Requirement: Request Interceptor
The system SHALL intercept all outgoing requests to inject the JWT token into the Authorization header.

#### Scenario: Token is added to request header
- **WHEN** a request is made and auth store has a valid token
- **THEN** the request includes `Authorization: Bearer <token>` header

#### Scenario: No token means no auth header
- **WHEN** a request is made and auth store is empty
- **THEN** the request is sent without Authorization header

### Requirement: Response Interceptor
The system SHALL intercept all responses to handle errors uniformly and trigger token refresh on 401.

#### Scenario: Successful response passes through
- **WHEN** a response has status 200-299
- **THEN** the response is returned as-is to the caller

#### Scenario: Handle 401 Unauthorized (Token Expired)
- **WHEN** a response has status 401 and refresh token exists
- **THEN** the system calls `POST /auth/refresh` to get a new token, updates auth store, and retries the original request

#### Scenario: 401 with no refresh token
- **WHEN** a response has status 401 and refresh token is missing or expired
- **THEN** the system clears auth store and redirects to login page (see CHANGE-02 for navigation integration)

#### Scenario: Handle 5xx errors
- **WHEN** a response has status 500 or greater
- **THEN** the system logs the error and returns a user-friendly error message (see CHANGE-15 for RFC 7807 errors)

### Requirement: Error Response Format
The system SHALL provide a consistent error response format extracted from the API response.

#### Scenario: Extract error message from API response
- **WHEN** the API returns an error with `{ errors: [...] }` or `detail` field
- **THEN** the error object has a `message` field with user-friendly text

### Requirement: Request and Response Logging
The system SHALL log HTTP requests and responses for debugging in development mode.

#### Scenario: Log outgoing request
- **WHEN** an HTTP request is made and `VITE_DEBUG=true`
- **THEN** console logs: `[API] GET /productos method=GET url=...`

#### Scenario: Log incoming response
- **WHEN** a response arrives and `VITE_DEBUG=true`
- **THEN** console logs: `[API] 200 GET /productos duration=45ms`

### Requirement: Refresh Token Request Queue
The response interceptor SHALL implement a request queue pattern to handle concurrent 401 responses without multiple simultaneous refresh calls.

#### Scenario: Queue concurrent requests during token refresh
- **WHEN** multiple requests receive 401 simultaneously
- **THEN** only ONE refresh call is made (singleton `refreshPromise`)
- **THEN** all other 401 requests are queued via `failedQueue` array
- **THEN** when refresh succeeds, the queue is processed via `processQueue()` and all queued requests are retried with the new token

#### Scenario: Queue rejection on refresh failure
- **WHEN** token refresh fails
- **THEN** all queued requests are rejected with the original error
- **THEN** the auth store is cleared and user is redirected to login

### Requirement: Error Toast Integration
The HTTP interceptor SHALL display user-friendly toast notifications for API errors using the UI store.

#### Scenario: Show error toast on 4xx response
- **WHEN** a response has status 400-499 (excluding 401 which triggers refresh)
- **THEN** `useUIStore.getState().showToast()` is called with the error message

#### Scenario: Show error toast on 5xx response
- **WHEN** a response has status 500+
- **THEN** a generic "Error del servidor" toast is displayed

#### Scenario: getErrorMessage maps status codes
- **WHEN** an error response is received
- **THEN** `getErrorMessage(error)` returns a user-friendly message based on status code:
  - 400: "Solicitud inválida"
  - 403: "No tienes permisos para realizar esta acción"
  - 404: "Recurso no encontrado"
  - 409: "Conflicto — el recurso ya existe o tiene dependencias"
  - 422: "Datos inválidos"
  - 500+: "Error del servidor. Intenta de nuevo más tarde."
  - Otherwise: extracts message from `error.response?.data?.detail` or `error.message`
