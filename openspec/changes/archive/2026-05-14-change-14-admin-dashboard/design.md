## Context

El proyecto Food Store actualmente tiene un sistema RBAC con 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT) donde ADMIN tiene acceso total a nivel de datos pero los endpoints de gestión están segregados por rol. No existe un panel de administración unificado ni endpoints de métricas para visualización de negocio.

**Estado actual:**
- Endpoints de catálogo (`/api/v1/productos`, `/api/v1/categorias`, `/api/v1/ingredientes`) accesibles para ADMIN y STOCK
- Endpoints de pedidos (`/api/v1/pedidos`) accesibles para ADMIN y PEDIDOS
- No existen endpoints de métricas
- Frontend tiene páginas de gestión distribuidas (no hay dashboard centralizado)

**Restricciones:**
- Mantener arquitectura de capas: Router → Service → UoW → Repository → Model
- Reutilizar componentes frontend existentes (OrdersTable, ProductTable, CategoryTable)
- No modificar el esquema de base de datos existente (solo añadir campo `activo` si no existe)

## Goals / Non-Goals

**Goals:**
1. Crear backend de métricas con 4 endpoints principales para KPIs
2. Crear backend de gestión de usuarios con CRUD completo
3. Implementar guard de roles unificado donde ADMIN tiene acceso implícito a STOCK y PEDIDOS
4. Crear frontend de dashboard con gráficos usando Recharts
5. Crear frontend de gestión de usuarios con tabla, búsqueda y edición

**Non-Goals:**
- No implementar gestión de configuración del sistema (US-060) - queda fuera de alcance
- No modificar lógica de autenticación existente (solo ampliar access control)
- No crear nuevos componentes de tabla desde cero (reutilizar existentes)

## Decisions

### D1: Estructura de endpoints de métricas

**Decisión:** Crear prefijo `/api/v1/admin/metricas` para todos los endpoints de KPIs.

**Alternativas consideradas:**
-分散 en `/api/v1/metrics/*` - ❌ No sigue convención de dominio
- `/api/v1/dashboard/metricas` - ❌ "dashboard" es concepto frontend

**Justificación:** El prefijo `admin` agrupa funcionalidad administrativa y es coherente con otros cambios de admin (gestion de usuarios).

---

### D2: Diseño de guard de roles

**Decisión:** Modificar el middleware de verificación de roles para que ADMIN pueda acceder a cualquier endpoint marcado con `@Roles('ADMIN', 'STOCK')` o `@Roles('ADMIN', 'PEDIDOS')`.

**Alternativas consideradas:**
- Duplicar todos los endpoints para ADMIN - ❌ Genera código duplicado
- Crear un nuevo rol combinado ADMIN_STOCK_PEDIDOS - ❌ Rompe el modelo de 4 roles fijos

**Justificación:** El ADMIN necesita acceso total sin duplicar lógica. El middleware verificará: `if user.has_role('ADMIN') -> allow`.

---

### D3: Campo `activo` en Usuario

**Decisión:** Añadir columna `activo` BOOLEAN con DEFAULT TRUE a la tabla `usuarios`.

**Alternativas:**
- Usar `deleted_at` para desactivar - ❌ Confundiría con soft delete real
- Crear tabla separada `usuarios_inactivos` - ❌ Compleja relación

**Justificación:** Campo simple y semánticamente claro. El login verificará `activo=true`.

---

### D4: Queries de métricas - agregación en DB vs aplicación

**Decisión:** Ejecutar todas las agregaciones (SUM, COUNT, GROUP BY) en PostgreSQL, no en Python.

**Alternativas:**
- Traer datos crudos y agregar en Python - ❌ Transferencia innecesaria de datos

**Justificación:** PostgreSQL es óptimo para agregaciones. Queries simples con `DATE_TRUNC`, `SUM`, `COUNT`.

---

### D5: Gráficos frontend - Recharts

**Decisión:** Usar librería Recharts existente en el proyecto.

**Alternativas:**
- Chart.js - ❌ No está instalado, requiere nueva dependencia
- Vis.js - ❌ Menos específico para React

**Justificación:** Simplifica dependencias. Mantiene consistencia con el stack.

---

### D6: Componentes de tabla reutilizados

**Decisión:** Crear un componente `AdminTable<T>` genérico que envuelva las tablas existentes.

**Alternativas:**
- Copiar componentes existentes - ❌ Duplicación de código
- Modificar tablas existentes para modo admin - ❌ Afecta funcionalidad existente

**Justificación:** Wrapper liviano que añade funcionalidad de búsqueda/filtros sin modificar componentes base.

---

## Risks / Trade-offs

| Risk | Impacto | Probabilidad | Mitigation |
|------|---------|--------------|------------|
| R1: Queries de métricas lentas con mucho histórico | Alto | Media | Añadir índices en `pedidos.creado_en`, `pedidos.estado_codigo` |
| R2: Usuarios con múltiples roles complejos | Medio | Baja | Documentar que ADMIN puede tener roles adicionales pero el primero es suficiente |
| R3: Dashboard con datos vacíos al inicio | Bajo | Alta | Incluir datos de seed con pedidos de ejemplo |

---

## Migration Plan

### Backend
1. **Migración DB**: Añadir columna `activo` a `usuarios` (nullable, luego NOT NULL con default)
2. **Endpoints métricas**: Crear nuevo router `admin/metricas.py`
3. **Endpoints usuarios**: Extender `admin/usuarios.py` (o crear nuevo)
4. **Middleware roles**: Modificar `requires_roles` para incluir lógica ADMIN implícito

### Frontend
1. **Dashboard**: Nueva página `/admin/dashboard` con componente Charts
2. **Usuarios**: Nueva página `/admin/usuarios` con tabla y modal
3. **Menú**: Añadir enlace al dashboard en el sidebar de ADMIN

### Rollback
1. Revertir middleware de roles (quitar lógica ADMIN implícito)
2. Eliminar router de métricas
3. Eliminar páginas frontend (routes y componentes)
4. Eliminar columna `activo` (migración reversible)