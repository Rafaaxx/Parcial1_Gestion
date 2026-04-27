## ADDED Requirements

### Requirement: SQLModel base model provides common columns
The system SHALL define a `BaseModel` that all domain models inherit from, providing automatic `created_at`, `updated_at`, and `deleted_at` columns.

#### Scenario: Automatic timestamps
- **WHEN** a model inherits from BaseModel
- **THEN** the model automatically includes `created_at` (auto-set at insert) and `updated_at` (auto-updated on modification)

#### Scenario: Soft delete column
- **WHEN** a model inherits from BaseModel
- **THEN** the model automatically includes `deleted_at: Optional[datetime]` (NULL if active, timestamp if deleted)

---

### Requirement: Model definitions are both ORM and Pydantic schemas
The system SHALL use SQLModel to define models that simultaneously serve as SQLAlchemy ORM models and Pydantic request/response schemas.

#### Scenario: Database persistence
- **WHEN** a developer defines `class User(BaseModel, table=True)`
- **THEN** SQLAlchemy creates a corresponding database table

#### Scenario: Request validation
- **WHEN** a route handler receives `user: User`
- **THEN** Pydantic validates incoming JSON against the User model schema

#### Scenario: Response serialization
- **WHEN** a route handler returns a User object
- **THEN** Pydantic serializes it to JSON automatically

---

### Requirement: Model relationships are typed and lazy-loaded
The system SHALL support SQLAlchemy relationships (1:N, N:M) with proper type hints for IDE support and lazy/eager loading strategies.

#### Scenario: One-to-many relationship
- **WHEN** a model defines `orders: List["Order"] = Relationship(back_populates="user")`
- **THEN** the relationship is accessible as `user.orders` and properly typed

#### Scenario: Many-to-many relationship
- **WHEN** models define N:M via a junction table
- **THEN** accessing the relationship loads related objects efficiently

---
