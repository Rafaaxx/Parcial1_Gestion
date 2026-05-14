## Why

El sistema Food Store necesita un panel administrativo completo para que los administradores puedan gestionar usuarios, visualizar métricas de negocio y tener acceso total al catálogo y pedidos. Actualmente, los endpoints de gestión de catálogo y pedidos están distribuidos entre los roles STOCK y PEDIDOS, pero no existe un panel unificado que permita al ADMIN gestionar todos los aspectos del sistema ni visualizar métricas de negocio para la toma de decisiones.

## What Changes

### Nuevas capacidades (Backend)

1. **Métricas y KPIs del sistema**
   - Endpoint de resumen: total ventas, pedidos por estado, usuarios registrados, productos más vendidos
   - Endpoint de ventas por período (día/semana/mes)
   - Endpoint de top productos con filtro de fechas
   - Endpoint de distribución de pedidos por estado (pie chart)

2. **Gestión de usuarios (Admin)**
   - Listado paginado de usuarios con búsqueda y filtros por rol
   - Edición de datos y roles de usuario
   - Activación/desactivación de usuarios (soft delete de acceso)
   - Validación: no permitir degradar último ADMIN del sistema

3. **Acceso completo de Admin**
   - Admin puede acceder a todos los endpoints de catálogo (productos, categorías, ingredientes)
   - Admin puede acceder a todos los endpoints de gestión de pedidos

### Nuevas capacidades (Frontend)

1. **Dashboard de métricas**
   - KPIs visuales: total ventas, pedidos, usuarios activos
   - Gráfico de líneas: evolución de ventas por período
   - Gráfico de barras: top productos más vendidos
   - Gráfico circular: distribución de pedidos por estado

2. **Gestión de usuarios**
   - Tabla de usuarios con paginación, búsqueda y filtros
   - Modal de edición de usuario y roles
   - Toggle de activar/desactivar usuario

3. **Acceso rápido al catálogo y pedidos**
   - Integración con las páginas existentes de gestión (reutilizar componentes)

## Capabilities

### New Capabilities

- `admin-metrics-api`: Endpoints de métricas y KPIs del sistema
- `admin-users-crud`: CRUD de usuarios para administradores
- `admin-dashboard-ui`: Dashboard visual con métricas y gráficos
- `admin-role-guard`: Guard de roles que permite ADMIN acceder a todo

### Modified Capabilities

- `auth-jwt-rbac`: Ampliar guard de roles para permitir acceso completo de ADMIN a catálogo y pedidos
- Reutilizar specs existentes: `order-pedidos-crud` (sin cambios en requisitos, solo acceso), `product-crud`, `categorias`, `ingredientes`

## Impact

### Backend
- Nuevos endpoints bajo `/api/v1/admin/`
- Modificación de middleware de roles: ADMIN tiene acceso a STOCK y PEDIDOS
- Nuevas queries de agregación para métricas

### Frontend
- Nueva página `/admin/dashboard` con gráficos
- Nueva página `/admin/usuarios` para gestión de usuarios
- Reutilización de componentes existentes de OrdersTable, ProductTable, CategoryTable

### Base de datos
- Campo `activo` en tabla `Usuario` (añadir si no existe)
- Posibles índices para optimizar queries de métricas

## Rollback Plan

1. Revertir cambios de middleware de roles
2. Eliminar endpoints de métricas
3. Deshabilitar páginas frontend del dashboard
4. Migración: añadir columna con valor por defecto true para `activo`