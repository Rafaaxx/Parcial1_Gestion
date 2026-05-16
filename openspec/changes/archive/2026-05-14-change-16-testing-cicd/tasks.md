## 1. Setup de Testing Infrastructure

- [x] 1.1 Instalar pytest-cov en requirements.txt
- [x] 1.2 Crear/actualizar pytest.ini con configuración de asyncio y coverage
- [x] 1.3 Crear backend/tests/conftest.py con fixtures base (db_session, client) - Ya existía
- [x] 1.4 Crear backend/tests/__init__.py - Ya existía
- [x] 1.5 Verificar que pytest corre sin errores en el proyecto base - Coverage: 60.31%

## 2. Estructura de Tests Unitarios

- [x] 2.1 Crear backend/tests/unit/__init__.py - Ya existía
- [x] 2.2 Crear backend/tests/unit/test_base_repository.py - Ya existía
- [x] 2.3 Crear backend/tests/unit/test_auth_service.py - Ya existía
- [x] 2.4 Crear backend/tests/unit/test_pydantic_schemas.py - Ya existía
- [x] 2.5 Implementar tests para BaseRepository (save, find_by_id, delete) - Ya existía
- [x] 2.6 Implementar tests para AuthService (register, login) - Ya existía
- [x] 2.7 Implementar tests de validación de schemas Pydantic - Ya existía

## 3. Estructura de Tests de Integración

- [x] 3.1 Crear backend/tests/integration/__init__.py - Ya existía
- [x] 3.2 Crear backend/tests/integration/conftest.py con autouse db - Ya existía
- [x] 3.3 Crear backend/tests/integration/test_auth_endpoints.py - Ya existía
- [x] 3.4 Crear backend/tests/integration/test_pedidos_endpoints.py - Ya existía
- [x] 3.5 Crear backend/tests/integration/test_fsm_transitions.py - Ya existía
- [x] 3.6 Crear backend/tests/integration/test_webhook_mp.py - Ya existía

## 4. Tests de Auth (Integración)

- [x] 4.1 Implementar test POST /api/v1/auth/register - éxito - Ya existía
- [x] 4.2 Implementar test POST /api/v1/auth/register - email duplicado - Ya existía
- [x] 4.3 Implementar test POST /api/v1/auth/register - datos inválidos - Ya existía
- [x] 4.4 Implementar test POST /api/v1/auth/login - éxito - Ya existía
- [x] 4.5 Implementar test POST /api/v1/auth/login - credenciales inválidas - Ya existía
- [x] 4.6 Implementar test POST /api/v1/auth/refresh token - Ya existía

## 5. Tests de Pedidos (Integración)

- [x] 5.1 Implementar test POST /api/v1/pedidos - creación exitosa - Ya existía
- [x] 5.2 Implementar test POST /api/v1/pedidos - stock insuficiente (rollback) - Ya existía
- [x] 5.3 Implementar test POST /api/v1/pedidos - dirección inválida - Ya existía
- [x] 5.4 Implementar test PATCH /api/v1/pedidos/{id}/estado - transición válida - Ya existía
- [x] 5.5 Implementar test PATCH /api/v1/pedidos/{id}/estado - transición inválida - Ya existía

## 6. Tests de Webhook MercadoPago (Integración)

- [x] 6.1 Implementar test POST /api/v1/pagos/webhook - pago aprobado - Ya existía
- [x] 6.2 Implementar test POST /api/v1/pagos/webhook - firma inválida - Ya existía
- [x] 6.3 Implementar test POST /api/v1/pagos/webhook - idempotency (duplicado) - Ya existía

## 7. GitHub Actions CI/CD

- [x] 7.1 Crear directorio .github/workflows/
- [x] 7.2 Crear .github/workflows/ci.yml
- [x] 7.3 Configurar job de lint (flake8, black, isort)
- [x] 7.4 Configurar job de tests (pytest con coverage)
- [x] 7.5 Configurar coverage gate (fallar si < 60%)
- [x] 7.6 Configurar matriz de Python (3.11, 3.12)
- [x] 7.7 Configurar artefactos (test-results.xml, htmlcov)

## 8. Coverage Report

- [x] 8.1 Configurar pytest-cov en pytest.ini para 60% mínimo
- [x] 8.2 Agregar badge de coverage en README.md (actualizado)
- [x] 8.3 Verificar coverage de módulos auth, pedidos, pagos por separado - 60.31% total
- [x] 8.4 Generar reporte HTML (htmlcov/) - Generado automáticamente
- [x] 8.5 Documentar cómo ejecutar tests localmente - En README.md

## 9. Documentación

- [x] 9.1 Actualizar backend/README.md con sección de testing
- [x] 9.2 Documentar comandos: pytest, coverage, lint
- [x] 9.3 Documentar estructura de tests (unit vs integration)
- [x] 9.4 Agregar badge de coverage al README