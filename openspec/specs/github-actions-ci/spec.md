# github-actions-ci Specification

## Purpose
TBD - created by archiving change change-16-testing-cicd. Update Purpose after archive.
## Requirements
### Requirement: GitHub Actions workflow para CI/CD

El sistema SHALL tener un workflow de GitHub Actions que corra en cada push y pull request.

#### Scenario: Push a main dispara workflow
- **GIVEN** un commit hecho a la rama main
- **WHEN** el push ocurre
- **THEN** GitHub Actions debe ejecutar el workflow completo

#### Scenario: Pull request dispara workflow
- **GIVEN** una nueva pull request abierta
- **WHEN** la PR es creada o actualizada
- **THEN** GitHub Actions debe ejecutar el workflow

#### Scenario: Workflow falla si tests fallan
- **GIVEN** los tests de pytest fallan
- **WHEN** el workflow se ejecuta
- **THEN** el job de tests debe fallar y el workflow debe fallar

### Requirement: Jobs separados para lint, test y coverage

El workflow SHALL tener jobs separados para mejor visibilidad de errores.

#### Scenario: Job de lint corre primero
- **GIVEN** el workflow comienza
- **WHEN** se ejecuta el job de lint
- **THEN** debe correr flake8, black, isort en el backend

#### Scenario: Job de tests corre después de lint
- **GIVEN** el job de lint pasa exitosamente
- **WHEN** se ejecuta el job de tests
- **THEN** debe correr pytest con la configuración de coverage

#### Scenario: Job de coverage es informativo
- **GIVEN** los tests pasan
- **WHEN** se ejecuta el job de coverage
- **THEN** debe generar el reporte pero no fallar si coverage < 60%

### Requirement: Coverage gate en PRs

El sistema SHALL bloquear la fusión de PRs si el coverage baja del 60%.

#### Scenario: PR con coverage >= 60% puede fusionarse
- **GIVEN** un PR donde el coverage es 65%
- **WHEN** el workflow termina
- **THEN** debe mostrar cobertura en los checks y permitir fusión

#### Scenario: PR con coverage < 60% no puede fusionarse
- **GIVEN** un PR donde el coverage es 45%
- **WHEN** el workflow termina
- **THEN** debe fallar y mostrar mensaje de coverage mínimo no alcanzado

### Requirement: Artefactos de tests сохраняются

El sistema SHALL guardar los resultados de tests y coverage como artefactos.

#### Scenario: Artefactos disponibles después del workflow
- **GIVEN** el workflow se ejecutó exitosamente
- **WHEN** se descargan los artefactos
- **THEN** deben incluir: test-results.xml, coverage-report/

### Requirement: Matriz de Python versions

El sistema SHALL probar con múltiples versiones de Python.

#### Scenario: Tests correr en Python 3.11 y 3.12
- **GIVEN** la matriz de versiones configurada
- **WHEN** el workflow corre
- **THEN** debe ejecutar los tests en Python 3.11 y 3.12

