## ADDED Requirements

### Requirement: Configuration is loaded from environment variables
The system SHALL read configuration from environment variables (or `.env` file) using Pydantic BaseSettings, with validation and defaults.

#### Scenario: Environment variables are loaded
- **WHEN** FastAPI app starts
- **THEN** system loads DATABASE_URL, JWT_SECRET_KEY, DEBUG, ALLOWED_HOSTS, and other settings from the environment

#### Scenario: .env file is used in development
- **WHEN** a `.env` file exists in the project root
- **THEN** system loads variables from the `.env` file (via python-dotenv)

#### Scenario: System environment variables override .env
- **WHEN** a variable is set both in `.env` and as a system environment variable
- **THEN** the system environment variable takes precedence

---

### Requirement: Required configuration fails early
The system SHALL validate that all required configuration variables are present at app startup; missing required vars cause the app to exit with a clear error message.

#### Scenario: Missing required DATABASE_URL
- **WHEN** DATABASE_URL is not set
- **THEN** app startup fails immediately with error: "DATABASE_URL is required"

#### Scenario: Missing required JWT_SECRET_KEY
- **WHEN** JWT_SECRET_KEY is not set
- **THEN** app startup fails immediately with error: "JWT_SECRET_KEY is required"

---

### Requirement: Configuration has sensible defaults
The system SHALL provide default values for non-critical settings (e.g., DEBUG=false, LOG_LEVEL="INFO", ALLOWED_HOSTS=["localhost"]).

#### Scenario: Optional variables use defaults
- **WHEN** an optional variable like DEBUG is not set
- **THEN** system uses DEBUG=false by default

---

### Requirement: Configuration is validated with Pydantic
The system SHALL use Pydantic BaseSettings to validate configuration types and ranges (e.g., DATABASE_URL is a valid PostgreSQL URL, PORT is an integer between 1 and 65535).

#### Scenario: Invalid DATABASE_URL format
- **WHEN** DATABASE_URL is set to an invalid value (e.g., "not-a-url")
- **THEN** app startup fails with a validation error

#### Scenario: Invalid PORT number
- **WHEN** PORT is set to a non-integer or out-of-range value
- **THEN** app startup fails with a validation error

---

### Requirement: Sensitive configuration is protected
The system SHALL treat secrets (JWT_SECRET_KEY, database password) as sensitive; they must not be logged or printed in error messages.

#### Scenario: Secrets are not logged
- **WHEN** logging configuration at startup
- **THEN** sensitive values like JWT_SECRET_KEY are masked or omitted

---

### Requirement: .env.example provides a template
The system SHALL include a `.env.example` file listing all required and optional configuration variables with descriptions.

#### Scenario: Developer uses .env.example
- **WHEN** a new developer clones the repo
- **THEN** they copy `.env.example` to `.env` and fill in their local values

---
