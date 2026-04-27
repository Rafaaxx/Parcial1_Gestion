## ADDED Requirements

### Requirement: BaseRepository[T] is generic and type-safe
The system SHALL define `BaseRepository[T]` as a generic class that accepts any SQLModel as a type parameter, ensuring type-safe CRUD operations.

#### Scenario: Repository is parameterized with a model
- **WHEN** a repository is defined as `class UserRepository(BaseRepository[User])`
- **THEN** all methods return `User` or `List[User]` with full IDE type hints

#### Scenario: Concrete repository inherits generic methods
- **WHEN** UserRepository is instantiated
- **THEN** it inherits find(), list(), create(), update(), delete(), soft_delete() methods without re-implementation

---

### Requirement: find() retrieves a single record by ID
The system SHALL provide `async def find(id: int) -> T | None` that queries the database for a single record, excluding soft-deleted rows.

#### Scenario: Record exists
- **WHEN** `await repository.find(id=5)` is called
- **THEN** system returns the record with ID 5 (if deleted_at IS NULL)

#### Scenario: Record does not exist
- **WHEN** `await repository.find(id=999)` is called
- **THEN** system returns None

#### Scenario: Soft-deleted record is invisible
- **WHEN** `await repository.find(id=5)` is called and the record has deleted_at NOT NULL
- **THEN** system returns None (as if the record doesn't exist)

---

### Requirement: list() retrieves paginated records
The system SHALL provide `async def list(skip: int = 0, limit: int = 20) -> (List[T], int)` that returns paginated records and total count, excluding soft-deleted rows.

#### Scenario: Pagination succeeds
- **WHEN** `await repository.list(skip=20, limit=10)` is called
- **THEN** system returns records 20–29 and the total count of all active records

#### Scenario: Total count includes soft-deleted check
- **WHEN** total count is calculated
- **THEN** system counts only non-deleted rows

---

### Requirement: create() inserts a record
The system SHALL provide `async def create(obj: T) -> T` that inserts a new record and returns it with auto-generated ID and timestamps.

#### Scenario: Record is created
- **WHEN** `await repository.create(user_data)` is called
- **THEN** system inserts the record, auto-generates ID, sets created_at and updated_at, and returns the object

---

### Requirement: update() modifies an existing record
The system SHALL provide `async def update(id: int, obj: T) -> T` that updates a record and refreshes its updated_at timestamp.

#### Scenario: Record is updated
- **WHEN** `await repository.update(id=5, new_data)` is called
- **THEN** system updates the record, increments updated_at, and returns the updated object

#### Scenario: Cannot update soft-deleted record
- **WHEN** attempting to update a soft-deleted record
- **THEN** system raises NotFoundError or returns None

---

### Requirement: delete() performs hard deletion
The system SHALL provide `async def delete(id: int) -> None` that performs hard deletion (removes the row completely).

#### Scenario: Record is hard-deleted
- **WHEN** `await repository.delete(id=5)` is called
- **THEN** system removes the row from the database (used for test cleanup, rarely in production)

---

### Requirement: soft_delete() marks a record as deleted
The system SHALL provide `async def soft_delete(id: int) -> None` that sets the deleted_at timestamp instead of removing the row.

#### Scenario: Record is soft-deleted
- **WHEN** `await repository.soft_delete(id=5)` is called
- **THEN** system sets deleted_at to the current timestamp; the record is invisible to find() and list() until restored

#### Scenario: Soft-deleted record can be restored
- **WHEN** the deleted_at column is set to NULL
- **THEN** the record becomes visible again

---

### Requirement: Custom repositories extend BaseRepository
The system SHALL allow service-specific repositories to inherit from BaseRepository and add custom query methods.

#### Scenario: Custom query method
- **WHEN** `CategoryRepository` defines `async def find_by_parent(parent_id: int) -> List[Category]`
- **THEN** the method can be called and inherits the session/database connection from the base class

---
