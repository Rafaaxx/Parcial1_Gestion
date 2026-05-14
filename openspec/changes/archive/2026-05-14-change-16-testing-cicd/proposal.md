## Why

El proyecto Food Store ha crecido significativamente con 15 cambios implementados (desde auth hasta dashboard admin). Sin embargo, la cobertura de tests es mínima y no hay integración continua. Esto representa un riesgo para la estabilidad del sistema, especialmente considerando que el flujo de pedidos (creación, FSM, webhooks) es crítico para el negocio.

**¿Por qué ahora?** Con 15 módulos completados, es imprescindible establecer una base de tests automatizados y CI/CD antes de que el proyecto crezca más. El objetivo es alcanzar >60% de cobertura en módulos críticos (auth, pedidos, pagos).

## What Changes

- **Backend Unit Tests**: Tests unitarios para BaseRepository, Services, validación de schemas Pydantic
- **Backend Integration Tests**: Tests de endpoints con SQLite in-memory (auth, pedidos, pagos)
- **Critical Flows Tests**: Crear pedido (UoW), Máquina de Estados (FSM), Webhook MercadoPago
- **Frontend Tests**: Tests básicos de componentes críticos (opcional, coverage muy bajo)
- **GitHub Actions CI/CD**: Workflow que corre tests en cada push y PR, falla si coverage < 60%
- **Coverage Report**: Generación de reportes de cobertura con pytest-cov
- **Test Fixtures**: Conftest con tablas, datos de prueba, autouse fixtures

## Capabilities

### New Capabilities
- `backend-unit-tests`: Tests unitarios para repositorios, servicios y validación
- `backend-integration-tests`: Tests de integración con SQLite in-memory
- `github-actions-ci`: Pipeline de CI/CD en GitHub Actions
- `test-coverage-report`: Configuración y generación de reportes de cobertura

### Modified Capabilities
- Ninguno — el CHANGE-16 no modifica requisitos de specs existentes

## Impact

- **Backend**: Nuevos archivos en `backend/tests/` (unit/, integration/)
- **GitHub**: Nuevo workflow `.github/workflows/ci.yml`
- **Configuración**: `pytest.ini`, `conftest.py` actualizado
- **Documentación**: README.md con sección de testing actualizada

**Rollback**: Si los tests fallan, se puede hacer rollback del workflow de CI sin afectar el código en producción.