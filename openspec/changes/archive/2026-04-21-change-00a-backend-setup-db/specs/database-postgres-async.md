## ADDED Requirements

### Requirement: PostgreSQL connection is managed via SQLAlchemy 2.0 async engine
The system SHALL configure SQLAlchemy 2.0 with asyncpg driver to manage PostgreSQL connections asynchronously.

#### Scenario: Connection pool is created
- **WHEN** FastAPI app initializes
- **THEN** system creates a SQLAlchemy async engine with asyncpg://user:password@host/dbname

#### Scenario: Connection pool respects concurrency limits
- **WHEN** the pool reaches max_overflow + pool_size connections
- **THEN** subsequent requests wait for available connections (no spawning infinite connections)

#### Scenario: Connection lifecycle is managed
- **WHEN** a request completes
- **THEN** system releases the connection back to the pool for reuse

---

### Requirement: Database sessions are created per-request via dependency injection
The system SHALL create an async database session per HTTP request and automatically close it after the request completes, using FastAPI's dependency injection system.

#### Scenario: Session is injected into handlers
- **WHEN** a route handler declares `session: AsyncSession = Depends(get_db)`
- **THEN** FastAPI injects the current database session, and the session is closed after the handler returns

#### Scenario: Transactions are isolated per request
- **WHEN** two concurrent requests are processed
- **THEN** each request has its own database session and transaction, no cross-request leakage

---

### Requirement: Database uses PostgreSQL with ACID guarantees
The system SHALL use PostgreSQL as the primary database, ensuring ACID compliance for critical operations (orders, payments).

#### Scenario: Transaction isolation
- **WHEN** two transactions attempt conflicting updates
- **THEN** PostgreSQL ensures serializable isolation or raises an error (preventing lost updates)

---
