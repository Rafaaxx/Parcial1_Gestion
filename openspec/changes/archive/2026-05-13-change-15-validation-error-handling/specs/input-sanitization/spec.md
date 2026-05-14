## ADDED Requirements

### Requirement: String inputs sanitized against XSS

The system MUST provide a utility function that escapes HTML entities in string inputs to prevent XSS attacks. This function MUST be available for use in all layers (routers, services).

#### Scenario: HTML tags in string are escaped
- **WHEN** a user input contains `<script>alert('xss')</script>`
- **THEN** the sanitization function MUST convert it to `&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;`

#### Scenario: Special characters are escaped
- **WHEN** a user input contains `"><img src=x onerror=alert(1)>`
- **THEN** the sanitization function MUST escape all special HTML characters

### Requirement: String sanitization available as decorator

The system SHOULD provide a decorator that automatically sanitizes string fields in Pydantic models before validation, ensuring all incoming text is safe.

#### Scenario: Decorator sanitizes input before validation
- **WHEN** a request body contains a field with XSS payload and the model uses the sanitization decorator
- **THEN** the field value MUST be sanitized before any validation occurs

### Requirement: Sanitization applied to user-generated content

The system MUST apply sanitization to:
- Text fields in request bodies (name, description, address, etc.)
- Query parameters that accept string values
- Any input that will be included in responses back to clients

#### Scenario: Name field with XSS is sanitized
- **WHEN** a user updates their name to `<b>John</b>`
- **THEN** when the name is returned in responses, it MUST be escaped to `&lt;b&gt;John&lt;/b&gt;`

### Requirement: Database inputs sanitized

The system MUST ensure that inputs stored in the database are sanitized. While ORM (SQLModel/SQLAlchemy) with parameterized queries provides SQL injection protection, string content that might be rendered in HTML MUST be sanitized.

#### Scenario: Description saved as sanitized
- **WHEN** a product description contains `<script>alert('test')</script>`
- **THEN** the stored value MUST have HTML entities escaped