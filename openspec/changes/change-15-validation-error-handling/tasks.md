## 1. Custom Exceptions Module

- [ ] 1.1 Create `backend/app/core/exceptions.py` with base `AppException` class
- [ ] 1.2 Implement `ValidationError` exception class (HTTP 422)
- [ ] 1.3 Implement `UnauthorizedError` exception class (HTTP 401)
- [ ] 1.4 Implement `ForbiddenError` exception class (HTTP 403)
- [ ] 1.5 Implement `NotFoundError` exception class (HTTP 404)
- [ ] 1.6 Implement `ConflictError` exception class (HTTP 409)
- [ ] 1.7 Implement `TooManyRequestsError` exception class (HTTP 429)
- [ ] 1.8 Create `__init__.py` exports in `backend/app/core/`

## 2. Request ID Middleware

- [ ] 2.1 Create `backend/app/core/middleware/request_id.py`
- [ ] 2.2 Implement middleware that generates UUID for each request
- [ ] 2.3 Add middleware to inject `X-Request-ID` response header
- [ ] 2.4 Use `contextvars` to make request_id available globally
- [ ] 2.5 Create `__init__.py` in `backend/app/core/middleware/`

## 3. Exception Handlers

- [ ] 3.1 Create `backend/app/core/handlers.py`
- [ ] 3.2 Implement RFC 7807 response formatter function
- [ ] 3.3 Create handler for `ValidationError` (422)
- [ ] 3.4 Create handler for `UnauthorizedError` (401)
- [ ] 3.5 Create handler for `ForbiddenError` (403)
- [ ] 3.6 Create handler for `NotFoundError` (404)
- [ ] 3.7 Create handler for `ConflictError` (409)
- [ ] 3.8 Create handler for `TooManyRequestsError` (429)
- [ ] 3.9 Create generic handler for uncaught exceptions (500)
- [ ] 3.10 Create handler for `RequestValidationError` (Pydantic request validation)
- [ ] 3.11 Create handler for `HTTPStatusError` (Starlette native errors)

## 4. Integration with FastAPI App

- [ ] 4.1 Update `backend/app/main.py` to import exception handlers
- [ ] 4.2 Register all exception handlers using `app.add_exception_handler()`
- [ ] 4.3 Add request_id middleware to app middleware stack
- [ ] 4.4 Test that main.py imports work without circular dependencies

## 5. Input Sanitization

- [ ] 5.1 Create `backend/app/core/sanitization.py`
- [ ] 5.2 Implement `escape_html()` function using Python's `html` module
- [ ] 5.3 Create `sanitize_string()` wrapper with None handling
- [ ] 5.4 Create `sanitize_dict()` to recursively sanitize string values
- [ ] 5.5 Add optional decorator for Pydantic model field auto-sanitization
- [ ] 5.6 Create `__init__.py` exports in `backend/app/core/`

## 6. Structured Logging

- [ ] 6.1 Create or update `backend/app/core/logging_config.py`
- [ ] 6.2 Configure JSON formatter for error logs
- [ ] 6.3 Implement log filter to exclude sensitive data (passwords, tokens)
- [ ] 6.4 Update error handlers to use structured logging
- [ ] 6.5 Ensure request_id is included in all log entries

## 7. Pydantic Request Validation Enhancement

- [ ] 7.1 Verify global Pydantic validation is already working (should be default in FastAPI)
- [ ] 7.2 Add custom response model for validation errors to ensure RFC 7807 format
- [ ] 7.3 Test that query parameter validation returns 422 with proper format
- [ ] 7.4 Test that path parameter validation returns 422 with proper format

## 8. Backend Tests

- [ ] 8.1 Create `backend/tests/test_error_handling/test_custom_exceptions.py`
- [ ] 8.2 Write tests for each custom exception type
- [ ] 8.3 Create `backend/tests/test_error_handling/test_exception_handlers.py`
- [ ] 8.4 Write tests verifying RFC 7807 format for each HTTP status
- [ ] 8.5 Create `backend/tests/test_error_handling/test_sanitization.py`
- [ ] 8.6 Write tests for XSS escaping function
- [ ] 8.7 Create `backend/tests/test_error_handling/test_request_id.py`
- [ ] 8.8 Write tests verifying request_id propagation
- [ ] 8.9 Run all tests and ensure > 70% coverage on new modules

## 9. Frontend Updates (Optional - Do if time permits)

- [ ] 9.1 Update `frontend/src/types/api.ts` to include RFC 7807 error type
- [ ] 9.2 Create `frontend/src/utils/errorParser.ts` utility
- [ ] 9.3 Update `frontend/src/api/axios.ts` to handle new error format
- [ ] 9.4 Test error handling in key user flows (login, register, checkout)

## 10. Documentation & Cleanup

- [ ] 10.1 Add docstrings to all new modules and functions
- [ ] 10.2 Run flake8 and black to ensure code style
- [ ] 10.3 Run mypy for type checking
- [ ] 10.4 Update backend/README.md if needed
- [ ] 10.5 Create a quick reference guide for using custom exceptions