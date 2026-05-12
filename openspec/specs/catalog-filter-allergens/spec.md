# Specification: catalog-filter-allergens

Filter products by excluding ingredients marked as allergens.

---

## ADDED Requirements

### Requirement: Exclude products by allergen ingredient ID
The system SHALL support excluding products that contain specific ingredient IDs (typically allergens). Multiple ingredient IDs can be excluded at once.

#### Scenario: Exclude single allergen
- **WHEN** client calls `GET /api/v1/productos?excluirAlergenos=5`
- **THEN** system returns products that do NOT contain ingredient ID 5
- **AND** any product associated with ingredient 5 via ProductoIngrediente is excluded

#### Scenario: Exclude multiple allergens
- **WHEN** client calls `GET /api/v1/productos?excluirAlergenos=1,3,7`
- **THEN** system returns products that do NOT contain any of ingredients 1, 3, or 7
- **AND** a product is excluded if it contains ANY of those ingredients

#### Scenario: Exclude allergens with other filters
- **WHEN** client calls `GET /api/v1/productos?busqueda=pizza&excluirAlergenos=5,8&categoria=2`
- **THEN** system applies all filters (search AND allergen exclusion AND category) in AND logic
- **AND** returns only products that match all criteria

#### Scenario: Invalid allergen ID format
- **WHEN** client calls `GET /api/v1/productos?excluirAlergenos=abc,xyz`
- **THEN** system silently ignores invalid IDs or returns HTTP 400 with clear error message
- **AND** does not crash or return 500

#### Scenario: Allergen ID does not exist
- **WHEN** client calls `GET /api/v1/productos?excluirAlergenos=99999`
- **THEN** system treats it as valid (no products contain ingredient 99999)
- **AND** returns all available products (no exclusion applied)

---

### Requirement: Allergen information in product detail
The system SHALL include allergen information in product detail responses so users know what ingredients (allergens) are present.

#### Scenario: Product detail includes ingredients with allergen flag
- **WHEN** client calls `GET /api/v1/productos/{id}`
- **THEN** response includes `ingredientes: IngredienteDetail[]`
- **AND** each ingredient includes `id`, `nombre`, `es_alergeno: boolean`

#### Scenario: User can identify allergens in detail view
- **WHEN** user views product detail for a pizza
- **THEN** ingredients list shows items marked as allergens (e.g., "Peanuts - ⚠️ ALLERGEN")
- **AND** user can make an informed decision before adding to cart

---

### Requirement: Public endpoint (no authentication)
The system SHALL allow unauthenticated access to allergen filter.

#### Scenario: Anonymous client uses allergen filter
- **WHEN** anonymous client calls `GET /api/v1/productos?excluirAlergenos=5`
- **THEN** system returns HTTP 200 with filtered results
- **AND** no 401 or 403 error is raised
