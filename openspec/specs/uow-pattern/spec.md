# Delta Specs — UoW Pattern

UnitOfWork pattern que expone múltiples repositorios bajo un contexto transaccional único.

---

## Capability: UnitOfWork exposes multiple repositories

### Description
El `UnitOfWork` expone propiedades para acceder a cada repositorio dentro del mismo contexto transaccional. Cada propiedad inicializa lazy el repositorio correspondiente si no existe.

### Dependencies
- Repository pattern

### Requirements
| ID | Req | Source |
|----|-----|--------|
| REQ-UOW-01 | SHALL exponer `uow.ingredientes` como property que retorna `IngredienteRepository` | CHANGE-02 |
| REQ-UOW-02 | SHALL exponer `uow.direcciones` como property que retorna `DireccionRepository` | CHANGE-05 |

### Scenarios

#### UOW-01: Acceso a repositorios via UoW
- **WHEN** código accede a `uow.ingredientes`
- **THEN** retorna instancia de `IngredienteRepository` dentro del contexto transaccional actual

#### UOW-02: Acceso a direcciones via UoW (CHANGE-05)
- **WHEN** código accede a `uow.direcciones`
- **THEN** retorna instancia de `DireccionRepository` dentro del contexto transaccional actual
