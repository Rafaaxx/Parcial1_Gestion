## ADDED Requirements

### Requirement: Configuración de pytest-cov

El sistema SHALL tener pytest-cov configurado para generar reportes de coverage.

#### Scenario: Coverage configurado en pytest.ini
- **GIVEN** pytest.ini con configuración de coverage
- **WHEN** pytest se ejecuta con --cov
- **THEN** debe generar un reporte de coverage

#### Scenario: Coverage excludes test files
- **GIVEN** la configuración de coverage
- **WHEN** se genera el reporte
- **THEN** debe excluir archivos en директории tests/

### Requirement: Reporte de coverage en formato HTML

El sistema SHALL generar un reporte de coverage en formato HTML.

#### Scenario: Reporte HTML generado
- **GIVEN** pytest-cov configurado
- **WHEN** se ejecuta con --cov-report=html
- **THEN** debe crear un directorio htmlcov/ con el reporte

#### Scenario: Reporte accesible en GitHub
- **GIVEN** el workflow de CI corre
- **WHEN** termina exitosamente
- **THEN** el reporte HTML debe estar disponible como artefacto

### Requirement: Coverage mínimo 60% en módulos críticos

El sistema SHALL alcanzar al menos 60% de coverage en módulos críticos (auth, pedidos, pagos).

#### Scenario: Coverage de auth >= 60%
- **GIVEN** los tests de auth implementados
- **WHEN** se mide el coverage de app/api/v1/auth/
- **THEN** debe ser >= 60%

#### Scenario: Coverage de pedidos >= 60%
- **GIVEN** los tests de pedidos implementados
- **WHEN** se mide el coverage de app/api/v1/pedidos/
- **THEN** debe ser >= 60%

#### Scenario: Coverage de pagos >= 60%
- **GIVEN** los tests de pagos implementados
- **WHEN** se mide el coverage de app/api/v1/pagos/
- **THEN** debe ser >= 60%

### Requirement: Badge de coverage en README

El sistema SHALL mostrar un badge con el coverage actual.

#### Scenario: Badge de coverage en README.md
- **GIVEN** el proyecto tiene un badge de coverage
- **WHEN** se visualiza el README
- **THEN** debe mostrar el porcentaje de coverage actual

### Requirement: Coverage por módulo

El sistema SHALL mostrar el coverage desglosado por módulo.

#### Scenario: Reporte muestra breakdown por archivo
- **GIVEN** el reporte de coverage se genera
- **WHEN** se revisa el reporte
- **THEN** debe mostrar el coverage individual de cada módulo (auth, pedidos, pagos, etc.)