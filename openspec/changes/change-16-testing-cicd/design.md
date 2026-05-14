## Context

Food Store tiene 15 cambios completados con功能 completa (auth, pedidos, pagos, admin), pero la cobertura de tests es mínima. El proyecto usa:
- Backend: FastAPI + SQLModel + PostgreSQL con patrón feature-first (Router → Service → UoW → Repository → Model)
- Testing actual: pytest 7.4 configurado pero sin tests implementados
- Frontend: React + TypeScript + Vite

El objetivo es establecer una base de testing que permita:
1. Detectar regresiones automáticamente
2. Documentar el comportamiento esperado
3. Facilitar refactors seguros

## Goals / Non-Goals

**Goals:**
- Lograr >60% de cobertura en módulos críticos (auth, pedidos, pagos)
- Setup de CI/CD con GitHub Actions que corra tests en cada push/PR
- Tests de integración con SQLite in-memory (no requiere PostgreSQL real)
- Coverage report accesible en PRs

**Non-Goals:**
- Tests de frontend (coverage muy bajo, prioritario backend)
- Tests end-to-end con Playwright/Cypress
- Test coverage en código legacy que no sea crítico

## Decisions

### 1. SQLite in-memory para tests de integración

**Decisión**: Usar SQLite in-memory en lugar de PostgreSQL para tests de integración.

**Alternativas consideradas**:
- PostgreSQL real con Docker — más realista pero más lento y complejo de setup
- pytest-xdist para tests paralelos — no prioritario

**Rationale**: SQLite in-memory es más rápido y no requiere setup externo. Los tests verifican lógica de negocio, no diferencias entre SQLite y PostgreSQL.

### 2. Coverage goal 60%

**Decisión**: Establecer 60% como mínimo de coverage.

**Alternativas consideradas**:
- 80% — muy ambicioso para primer iteration
- 40% — demasiado bajo para valore real

**Rationale**: 60% es un objetivo alcanzable que cubre la mayoría de los casos de uso críticos sin requerir tests exhaustivos de cada línea.

### 3. Estructura de tests por módulo

**Decisión**: Crear `backend/tests/unit/` y `backend/tests/integration/` separados.

**Rationale**: Separa tests rápidos (unit) de los más lentos (integration). Permite ejecutar solo unit en desarrollo rápido.

### 4. GitHub Actions con job separado para coverage

**Decisión**: Crear workflow con jobs separados (lint + test + coverage).

**Rationale**: Jobs separados permiten ver qué falló más rápido y el job de coverage es opcional (no bloqueante).

## Risks / Trade-offs

- [Riesgo] Tests que funcionan con SQLite pero fallan en PostgreSQL → **Mitigación**: Usar solo features compatibles con ambos (no dialect-specific queries)
- [Riesgo] Coverage artificial (tests que solo ejercitan código sin validar) → **Mitigación**: Enfocar en casos de uso reales de las user stories
- [Riesgo] Tests demasiado lentos que bloquen CI → **Mitigación**: SQLite in-memory es rápido; mantener < 5 min total

## Migration Plan

1. **Setup inicial** (1 hora):
   - Crear `pytest.ini` con configuración
   - Crear `conftest.py` con fixtures base
   - Instalar `pytest-cov`

2. **Unit tests** (8 horas):
   - BaseRepository
   - Services de auth, pedidos, productos
   - Validación de schemas Pydantic

3. **Integration tests** (8 horas):
   - Endpoints de auth (registro, login, refresh)
   - Creación de pedidos (UoW)
   - Máquina de Estados (FSM)
   - Webhook MercadoPago

4. **CI/CD** (4 horas):
   - Crear `.github/workflows/ci.yml`
   - Configurar coverage gate en PRs
   - Actualizar README.md

**Rollback**: Si CI falla, el código no se fusiona. No hay impacto en producción.