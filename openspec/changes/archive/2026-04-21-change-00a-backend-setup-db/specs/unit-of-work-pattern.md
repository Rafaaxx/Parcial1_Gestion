## ADDED Requirements

### Requirement: UnitOfWork is an async context manager
The system SHALL implement UnitOfWork (`async with UnitOfWork(session) as uow:`) that groups multiple repository operations into a single atomic transaction.

#### Scenario: Context manager setup
- **WHEN** `async with UnitOfWork(session) as uow:` is entered
- **THEN** system creates a transaction context that encompasses all operations inside the block

#### Scenario: Context manager commit
- **WHEN** the context manager exits successfully (no exception)
- **THEN** system automatically commits the transaction

#### Scenario: Context manager rollback
- **WHEN** an exception is raised inside the context manager
- **THEN** system automatically rolls back all changes (no partial updates)

---

### Requirement: UnitOfWork exposes multiple repositories
The system SHALL provide access to all repositories through the UoW instance (e.g., `uow.users`, `uow.orders`, `uow.details`).

#### Scenario: Repository access
- **WHEN** code accesses `await uow.users.create(user_data)`
- **THEN** the operation executes within the current transaction context

#### Scenario: Multiple repositories in one transaction
- **WHEN** code creates orders and order details within the same UoW block
- **THEN** both operations succeed or both are rolled back atomically

---

### Requirement: UnitOfWork supports explicit commit/rollback
The system SHALL provide `await uow.commit()` and `await uow.rollback()` methods for manual control when needed (though automatic on context exit is preferred).

#### Scenario: Manual commit
- **WHEN** `await uow.commit()` is called
- **THEN** system commits the current transaction

#### Scenario: Manual rollback
- **WHEN** `await uow.rollback()` is called
- **THEN** system rolls back all changes

---

### Requirement: UnitOfWork is used for critical multi-entity transactions
The system SHALL require UoW for operations that modify multiple tables atomically (e.g., order creation, payment confirmation).

#### Scenario: Order creation uses UoW
- **WHEN** creating an order with items, the code uses `async with UnitOfWork(session) as uow:`
- **THEN** creating the order, adding items, and recording history all succeed or all fail together

---
