# 📚 Skills Instaladas para Food Store v5.0

## Resumen

Se han instalado **7 skills especializadas** en el proyecto para soportar la arquitectura de Food Store. Las skills están disponibles en `.agents/skills/` y se cargan automáticamente al trabajar en cambios relevantes.

---

## 🎯 Skills por Dominio

### 1. **Arquitectura y Patrones**

#### `architecture-patterns` (13.2K installs)
**Fuente**: `wshobson/agents@architecture-patterns`  
**Propósito**: Proporciona patrones de arquitectura, decisiones de diseño, y mejores prácticas estructurales.  
**Cuándo usar**: 
- Al diseñar la estructura de un nuevo module
- Al tomar decisiones arquitectónicas (monolítica vs modular, etc.)
- Al revisar la organización de capas (Router → Service → UoW → Repository)

---

### 2. **FastAPI**

#### `fastapi-templates` (14.4K installs)
**Fuente**: `wshobson/agents@fastapi-templates`  
**Propósito**: Templates, patrones y mejores prácticas específicas de FastAPI.  
**Cuándo usar**:
- CHANGE-00a: Setup FastAPI, middlewares, dependency injection
- CHANGE-01: Endpoints de auth
- Cualquier implementación de rutas REST

---

### 3. **Database & ORM**

#### `sqlalchemy-alembic-expert-best-practices-code-review` (580 installs)
**Fuente**: `wispbit-ai/skills@sqlalchemy-alembic-expert-best-practices-code-review`  
**Propósito**: Experto en SQLAlchemy 2.0, Alembic migrations, y mejores prácticas de BD.  
**Cuándo usar**:
- CHANGE-00a: Configuración de SQLAlchemy async, Alembic setup
- Cualquier cambio que requiera modelos ORM nuevos
- Code review de schemas y migrations
- Problemas con relaciones N:M, queries complejas (como CTEs en CHANGE-03)

---

### 4. **Python - Calidad y Mejores Prácticas**

#### `python-expert-best-practices-code-review` (347 installs)
**Fuente**: `wispbit-ai/skills@python-expert-best-practices-code-review`  
**Propósito**: Experto en Python, SOLID, type hints, testing, y mejores prácticas.  
**Cuándo usar**:
- Code review de cualquier módulo Python
- Diseño de arquitectura Python (SOLID principles)
- Testing y coverage
- Type hints y mypy

#### `python-code-review` (358 installs)
**Fuente**: `existential-birds/beagle@python-code-review`  
**Propósito**: Code review especializado en Python con enfoque en calidad y errores comunes.  
**Cuándo usar**:
- Revisión de código antes de merge
- Identificar anti-patterns y deuda técnica
- Sugerencias de refactoring

---

### 5. **APIs y Documentación**

#### `openapi-specification-v2` (398 installs)
**Fuente**: `hairyf/skills@openapi-specification-v2`  
**Propósito**: OpenAPI 3.0 specification, Swagger, y documentación de APIs.  
**Cuándo usar**:
- Documentación de endpoints REST
- Validación de esquemas OpenAPI
- Generación de clientes SDK desde specs
- CHANGE-00a: Setup de `/docs` y `/redoc`

---

### 6. **Discovery & Extensión**

#### `find-skills` (incluida)
**Fuente**: Interna del proyecto  
**Propósito**: Descubrir e instalar nuevas skills del ecosistema.  
**Cuándo usar**:
- Necesitamos una skill para un nuevo dominio (ej: testing con pytest, Docker, etc.)

---

## 🚀 Cómo Usar las Skills

### Opción 1: Automático (Recomendado)
Las skills se cargan automáticamente cuando detectan que es relevante. Por ejemplo:
- Si mencionas "FastAPI", se carga `fastapi-templates`
- Si pides "code review", se cargan las skills de review
- Si trabajas en migrations, se carga `sqlalchemy-alembic-expert-best-practices-code-review`

### Opción 2: Manual
Cargá una skill explícitamente en cualquier momento:
```
/load architecture-patterns
/load python-expert-best-practices-code-review
```

### Opción 3: Búsqueda
Descubrí nuevas skills:
```
/find-skills [query]
```

Ejemplos:
- `/find-skills pytest testing` → Busca skills de testing
- `/find-skills docker containerization` → Busca skills de Docker
- `/find-skills ci/cd github actions` → Busca skills de CI/CD

---

## 📊 Mapeo Skills ↔ Changes

| Change | Skills Aplicables |
|--------|------------------|
| **CHANGE-00a** (Backend Setup) | fastapi-templates, sqlalchemy-alembic, architecture-patterns, openapi-specification-v2 |
| **CHANGE-00b** (Frontend Setup) | (frontend, no skills instaladas aún) |
| **CHANGE-00c** (CORS + Rate Limiting) | fastapi-templates, architecture-patterns |
| **CHANGE-01** (Auth JWT) | fastapi-templates, python-expert-best-practices |
| **CHANGE-02-06** (Navegación, Categorías, Ingredientes, Direcciones, Productos) | fastapi-templates, sqlalchemy-alembic, python-expert-best-practices |
| **CHANGE-07-11** (Catálogo, Carrito, Pedidos, FSM, Admin) | fastapi-templates, sqlalchemy-alembic, python-expert-best-practices |
| **CHANGE-12-13** (MercadoPago + Webhook) | fastapi-templates, python-expert-best-practices, openapi-specification-v2 |
| **CHANGE-14** (Dashboard Admin) | fastapi-templates, python-expert-best-practices |
| **CHANGE-15-16** (Validación global, Testing CI/CD) | python-expert-best-practices, python-code-review |

---

## 🔍 Búsquedas Realizadas

Se ejecutaron las siguientes búsquedas de skills:

1. **Clean Architecture Python**: 13.2K instalaciones encontradas
   - ✅ `wshobson/agents@architecture-patterns` (instalada)

2. **FastAPI**: 14.4K instalaciones encontradas
   - ✅ `wshobson/agents@fastapi-templates` (instalada)

3. **SQLAlchemy + Alembic**: 580 instalaciones encontradas
   - ✅ `wispbit-ai/skills@sqlalchemy-alembic-expert-best-practices-code-review` (instalada)

4. **Python Best Practices**: 347 instalaciones encontradas
   - ✅ `wispbit-ai/skills@python-expert-best-practices-code-review` (instalada)

5. **Python Code Review**: 358 instalaciones encontradas
   - ✅ `existential-birds/beagle@python-code-review` (instalada)

6. **OpenAPI**: 398 instalaciones encontradas
   - ✅ `hairyf/skills@openapi-specification-v2` (instalada)

---

## 📝 Próximos Pasos

### Si necesitamos más skills:
- **Testing (pytest)**: `npx skills find pytest testing python`
- **Docker/Containers**: `npx skills find docker containerization`
- **CI/CD (GitHub Actions)**: `npx skills find ci/cd github actions`
- **React Frontend**: `npx skills find react typescript`
- **Performance Optimization**: `npx skills find fastapi performance optimization`

### Instalación de nuevas skills:
```bash
npx skills add <owner/repo@skill> -y
```

---

## ✅ Status

- ✅ 7 skills especializadas instaladas
- ✅ Cobertura total de dominio: Arquitectura, FastAPI, ORM, Python, APIs
- ✅ Listas para usar en CHANGE-00a y adelante
- 🔶 Pueden agregarse skills de testing/pytest si se necesita TDD estricto
- 🔶 Pueden agregarse skills de React/frontend cuando comience CHANGE-00b

---

**Generado**: 2026-04-21 | **Proyecto**: Food Store v5.0 SDD
