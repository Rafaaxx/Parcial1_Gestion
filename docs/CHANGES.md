# Mapa de Changes — Food Store v5.0 (SDD)

## Visión General

Este documento describe el **orden de implementación completo** de Food Store, desglosado en **16 changes independientes pero secuencialmente dependientes**. Cada change corresponde a una funcionalidad atómica con sus artefactos SDD: `proposal.md`, `design.md` y `tasks.md`.

El mapa respeta las dependencias arquitectónicas de las capas (Router→Service→UoW→Repository→Model en backend; FSD en frontend) y agrupa por dominio: Infraestructura, Autenticación, Gestión de Datos, Operacional y Pagos.

**Total estimado**: ~250 horas de implementación (incluyendo testing y documentación).

---

## 🎯 Matriz de Dependencias

```
CHANGE-00 (Infraestructura Base) [4 sub-changes]
    ├── CHANGE-00a: Backend Setup + DB
    ├── CHANGE-00b: Frontend Setup + Zustand
    ├── CHANGE-00c: Configuración CORS + Rate Limiting
    └── CHANGE-00d: Seed Data + Tests Base
        │
        ├→ CHANGE-01: Auth (Login/Registro/JWT/Refresh) ✓ Depende de CHANGE-00
        │   │
        │   ├→ CHANGE-02: Navegación y Layout (UI roles) ✓ Depende de CHANGE-01
        │   │
        │   ├→ CHANGE-05: Gestión de Direcciones ✓ Depende de CHANGE-01
        │   │
        │   └→ CHANGE-03: Categorías (CRUD jerárquico) ✓ Depende de CHANGE-00b
        │       │
        │       └→ CHANGE-04: Ingredientes y Alergenos ✓ Depende de CHANGE-03
        │           │
        │           └→ CHANGE-06: Productos (CRUD + stock) ✓ Depende de CHANGE-04
        │               │
        │               ├→ CHANGE-07: Catálogo (listado público) ✓ Depende de CHANGE-06
        │               │   │
        │               │   └→ CHANGE-08: Carrito de Compras ✓ Depende de CHANGE-07 + CHANGE-01
        │               │       │
        │               │       └→ CHANGE-09: Crear Pedidos ✓ Depende de CHANGE-08 + CHANGE-05
        │               │           │
        │               │           ├→ CHANGE-10: Máquina de Estados (FSM) ✓ Depende de CHANGE-09
        │               │           │   │
        │               │           │   └→ CHANGE-11: Panel de Pedidos (Admin) ✓ Depende de CHANGE-10
        │               │           │
        │               │           └→ CHANGE-12: Integración MercadoPago ✓ Depende de CHANGE-09
        │               │               │
        │               │               └→ CHANGE-13: Webhook IPN ✓ Depende de CHANGE-12
        │               │
        │               └→ CHANGE-14: Panel de Admin (Dashboard) ✓ Depende de CHANGE-06
        │
        └→ CHANGE-15: Validación Global + Errores RFC7807 ✓ Depende de CHANGE-00
            └→ CHANGE-16: Testing + CI/CD ✓ Depende de todos
```

---

## 📋 Changes por Dominio

### DOMINIO 1: Infraestructura Base

#### CHANGE-00: Setup Inicial (4 sub-changes)

| Sub-Change | Nombre | Historias US | Duración |
|-----------|--------|-------------|----------|
| 00a | Backend Setup + DB | US-000, US-000a, US-000b | 15h |
| 00b | Frontend Setup + Zustand | US-000c, US-000e | 12h |
| 00c | CORS + Rate Limiting | US-000a, US-073 | 8h |
| 00d | Seed Data + Patrones Base | US-000d, US-068, US-074 | 5h |

**Dependencias**: Ninguna
**Criterios de éxito**:
- ✅ Swagger UI accesible en `/docs`
- ✅ Zustand stores implementados y tipados
- ✅ BaseRepository[T] genérico funcionando
- ✅ UnitOfWork como context manager
- ✅ Seed data cargado correctamente

---

#### CHANGE-01: Autenticación y Autorización (Auth)

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-01-auth-jwt-rbac` |
| **Historias US** | US-001, US-002, US-003, US-004, US-005, US-006, US-073 |
| **Funcionalidad** | Registro, Login, JWT, Refresh Token, Logout, RBAC (4 roles) |
| **Dependencias** | CHANGE-00 |
| **Duración estimada** | 20h |

**Modelo de datos**:
- Usuario (email UQ, password_hash)
- Rol (ADMIN, STOCK, PEDIDOS, CLIENT)
- UsuarioRol (M:M pivot)
- RefreshToken (token_hash UQ, expires_at, revoked_at)

**Endpoints**:
- POST /api/v1/auth/register → 201 + tokens
- POST /api/v1/auth/login → 200 + tokens (rate limited 5/15min)
- POST /api/v1/auth/refresh → 200 + new tokens
- POST /api/v1/auth/logout → 204

**Criterios de éxito**:
- ✅ JWT access token (30 min) + refresh token (7 días)
- ✅ Refresh token rotation en cada refresco
- ✅ Rate limiting en login (5/15 min por IP)
- ✅ Tests: registro duplicado, login fallido, refresh válido/expirado

---

#### CHANGE-02: Navegación y Layout Base

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-02-navigation-layout-rbac` |
| **Historias US** | US-075, US-076, US-066, US-067 |
| **Funcionalidad** | Navbar/Sidebar por rol, route guards, interceptor 401 automático |
| **Dependencias** | CHANGE-01 |
| **Duración estimada** | 15h |

**Componentes Frontend**:
- Navbar adaptado por rol
- Sidebar con navegación contextual
- ProtectedRoute HOC
- Axios interceptor con refresh automático
- Error boundary y toast system

**Criterios de éxito**:
- ✅ TOKEN expirado → refresh automático sin re-login
- ✅ Refresh falla → redirige a login
- ✅ Menú solo muestra opciones de rol actual
- ✅ Rutas privadas protegidas

---

### DOMINIO 2: Gestión de Catálogo

#### CHANGE-03: Categorías Jerárquicas

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-03-categories-hierarchical` |
| **Historias US** | US-007, US-008, US-009, US-010 |
| **Funcionalidad** | CRUD categorías padre-hijo, validación de ciclos, soft delete |
| **Dependencias** | CHANGE-01 |
| **Duración estimada** | 12h |

**Endpoints**:
- POST /api/v1/categorias (ADMIN/STOCK)
- GET /api/v1/categorias (público) → árbol anidado
- PUT /api/v1/categorias/{id} (ADMIN/STOCK)
- DELETE /api/v1/categorias/{id} (ADMIN/STOCK, soft delete)

**Criterios de éxito**:
- ✅ CTE recursivo para listar árbol completo
- ✅ Validación: no permitir ciclos (A padre de B y B padre de A)
- ✅ Soft delete con validación: no eliminar si tiene productos activos

---

#### CHANGE-04: Ingredientes y Alergenos

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-04-ingredients-allergens` |
| **Historias US** | US-011, US-012, US-013, US-014 |
| **Funcionalidad** | CRUD ingredientes, flag es_alergeno, soft delete |
| **Dependencias** | CHANGE-01 |
| **Duración estimada** | 8h |

**Endpoints**:
- POST /api/v1/ingredientes (ADMIN/STOCK)
- GET /api/v1/ingredientes (público, con filtro es_alergeno)
- PUT /api/v1/ingredientes/{id} (ADMIN/STOCK)
- DELETE /api/v1/ingredientes/{id} (ADMIN/STOCK, soft delete)

**Criterios de éxito**:
- ✅ Campo es_alergeno booleano
- ✅ Nombre único
- ✅ Soft delete con persistencia en productos históricos

---

#### CHANGE-06: Productos CRUD y Stock

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-06-products-crud-stock` |
| **Historias US** | US-015, US-016, US-017, US-020, US-021, US-022 |
| **Funcionalidad** | CRUD productos, asociación N:M cat/ing, stock atomicidad |
| **Dependencias** | CHANGE-04, CHANGE-03, CHANGE-01 |
| **Duración estimada** | 18h |

**Modelos**:
- Producto (nombre, descripción, precio NUMERIC(10,2), stock_cantidad, disponible, imagen)
- ProductoCategoria (N:M)
- ProductoIngrediente (N:M con es_removible flag)

**Endpoints**:
- POST /api/v1/productos (ADMIN/STOCK)
- GET /api/v1/productos/{id} (detalle con ingredientes y categorías)
- PUT /api/v1/productos/{id} (ADMIN/STOCK)
- PATCH /api/v1/productos/{id}/stock (ADMIN/STOCK, atomicidad SELECT FOR UPDATE)
- DELETE /api/v1/productos/{id} (ADMIN/STOCK, soft delete)

**Criterios de éxito**:
- ✅ Precio como NUMERIC (nunca float)
- ✅ Stock atomicidad con SELECT FOR UPDATE
- ✅ Asociaciones M:M correctas
- ✅ Campo disponible independiente del stock

---

#### CHANGE-07: Catálogo Público

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-07-catalog-listing-search` |
| **Historias US** | US-018, US-019, US-023 |
| **Funcionalidad** | Listado paginado, búsqueda, filtros, solo productos disponibles |
| **Dependencias** | CHANGE-06 |
| **Duración estimada** | 12h |

**Endpoints**:
- GET /api/v1/productos (público, paginado, filtros: categoría, nombre, precio)
- GET /api/v1/productos/{id} (detalle público)

**Query params**:
- `skip=0&limit=20` (paginación)
- `categoria=5` (filtro)
- `busqueda=pizza` (búsqueda ILIKE)
- `precio_desde=100&precio_hasta=500` (rango)

**Criterios de éxito**:
- ✅ Solo productos disponibles=true y deleted_at IS NULL
- ✅ Búsqueda con ILIKE
- ✅ Filtro por categoría (incluyendo subcategorías)
- ✅ No revelar stock exacto (solo si > 0)
- ✅ Respuesta incluye total para paginación

---

#### CHANGE-05: Direcciones de Entrega

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-05-delivery-addresses` |
| **Historias US** | US-024, US-025, US-026, US-027, US-028 |
| **Funcionalidad** | CRUD direcciones por usuario, dirección principal, ownership |
| **Dependencias** | CHANGE-01 |
| **Duración estimada** | 10h |

**Endpoints**:
- POST /api/v1/direcciones (usuario autenticado)
- GET /api/v1/direcciones (solo propias)
- PUT /api/v1/direcciones/{id} (solo propias)
- DELETE /api/v1/direcciones/{id} (solo propias)
- PATCH /api/v1/direcciones/{id}/principal (marcar como principal)

**Validaciones**:
- ✅ Usuario solo ve/edita sus direcciones
- ✅ Una dirección principal por usuario
- ✅ Al marcar nueva principal, la anterior se desmarca

---

### DOMINIO 3: Carrito y Pedidos

#### CHANGE-08: Carrito de Compras

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-08-shopping-cart` |
| **Historias US** | US-029, US-030, US-031, US-032, US-033, US-034 |
| **Funcionalidad** | Carrito client-side persistente, personalización, cálculo totales |
| **Dependencias** | CHANGE-07, CHANGE-01 |
| **Duración estimada** | 10h |

**Store Zustand (cartStore)**:
- items: CartItem[] { productoId, producto, cantidad, personalizacion[] }
- Actions: addItem(), removeItem(), updateQuantity(), clearCart()
- Selectores: totalItems(), subtotal(), costoEnvio(), total()
- Persistencia: localStorage

**Reglas de negocio**:
- ✅ Personalización solo de ingredientes removibles (es_removible=true)
- ✅ Si producto ya en carrito → incrementar cantidad (no duplicar)
- ✅ Costo envío flat rate $50 (v1)
- ✅ Persiste en cierre navegador, refresh, logout/login

---

#### CHANGE-09: Creación de Pedidos

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-09-order-creation-uow` |
| **Historias US** | US-035, US-036, US-037, US-038 |
| **Funcionalidad** | POST /pedidos, Unit of Work atomicidad, snapshots, validaciones |
| **Dependencias** | CHANGE-08, CHANGE-05, CHANGE-01 |
| **Duración estimada** | 16h |

**Modelo Pedido**:
- usuario_id, estado_codigo (PENDIENTE inicial), total, costo_envio
- forma_pago_codigo, direccion_id
- Snapshots: nombre_snapshot, precio_snapshot, direccion_snapshot

**Flujo UoW**:
1. Valida dirección pertenece al usuario
2. Valida forma de pago existe
3. Para c/ item: valida stock suficiente (SELECT FOR UPDATE)
4. Crea Pedido + DetallePedidos + HistorialEstadoPedido
5. **Atomicidad**: TODO o NADA (rollback si falla cualquier paso)

**Criterios de éxito**:
- ✅ Stock insuficiente → rollback completo (sin pedido parcial)
- ✅ Snapshots inmutables al crear
- ✅ Primer historial con estado_desde=NULL
- ✅ Tests: pedido exitoso, stock insuficiente (rollback)

---

#### CHANGE-10: Máquina de Estados (FSM)

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-10-order-state-machine` |
| **Historias US** | US-039, US-040, US-041, US-042, US-043, US-044 |
| **Funcionalidad** | FSM 6 estados, validación estricta, decrement/restore stock |
| **Dependencias** | CHANGE-09, CHANGE-01 |
| **Duración estimada** | 18h |

**Estados**:
```
PENDIENTE ──[pago aprobado]──→ CONFIRMADO ──[gestión]──→ EN_PREPARACIÓN
                   ↓                 ↓                          ↓
                CANCELADO ←───────────────── [solo ADMIN]
                    ↓                                             ↓
                [terminal]                                  EN_CAMINO → ENTREGADO
                                                               ↓        ↓
                                                          [solo PEDIDOS] [terminal]
```

**Validaciones**:
- ✅ Solo transiciones en el mapa (sin saltos)
- ✅ Estados terminales (ENTREGADO, CANCELADO) sin transiciones salientes
- ✅ Al CONFIRMADO: decrementa stock todos los items (atómico)
- ✅ Al cancelar CONFIRMADO/EN_PREP: restaura stock (atómico)
- ✅ Historial append-only (solo INSERT, nunca UPDATE)

**Endpoints**:
- PATCH /api/v1/pedidos/{id}/estado { nuevo_estado, observacion? }
- DELETE /api/v1/pedidos/{id} (cancela, solo PENDIENTE/CONFIRMADO)

---

#### CHANGE-11: Panel de Gestión de Pedidos

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-11-order-management-admin` |
| **Historias US** | US-049, US-050, US-051, US-052 |
| **Funcionalidad** | Tabla pedidos, filtros, detalle modal, historial timeline |
| **Dependencias** | CHANGE-10, CHANGE-01 |
| **Duración estimada** | 14h |

**Componentes Frontend**:
- OrdersTable (columnas: ID, Cliente, Estado, Total, Fecha)
- OrderFilters (dropdowns: Estado, Rango fechas)
- OrderDetail modal (tabs: Resumen, Líneas, Historial, Pago)
- HistorialTimeline (visual de transiciones)
- StateTransitionButtons (contextuales por rol/estado)

**Hooks TanStack Query**:
- useOrders(filters, pagination)
- useOrderDetail(orderId)

**Criterios de éxito**:
- ✅ CLIENT ve solo sus pedidos
- ✅ ADMIN/PEDIDOS ven todos
- ✅ Filtros por estado y fecha funcionan
- ✅ Historial visible con timestamps y usuario responsable

---

### DOMINIO 4: Pagos e Integración

#### CHANGE-12: Integración MercadoPago

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-12-mercadopago-checkout` |
| **Historias US** | US-045, US-046, US-047, US-048 |
| **Funcionalidad** | SDK MP tokenización, crear pago, tabla Pago, idempotency_key |
| **Dependencias** | CHANGE-09, CHANGE-01, CHANGE-00 |
| **Duración estimada** | 16h |

**Modelo Pago**:
- pedido_id, monto, mp_payment_id (UQ, nullable)
- mp_status (pending/approved/rejected/in_process)
- external_reference (UUID del pedido), idempotency_key (UQ UUID)

**Flow**:
1. Frontend: SDK MP tokeniza tarjeta → card_token
2. Frontend: POST /api/v1/pagos/crear { pedido_id, card_token }
3. Backend: genera idempotency_key UUID
4. Backend: llama API MP con card_token + idempotency_key
5. Backend: crea registro Pago + retorna mp_payment_id y status
6. Frontend: muestra estado (procesando, aprobado, rechazado)

**Criterios de éxito**:
- ✅ PCI SAQ-A: datos de tarjeta NUNCA pasan por nuestro servidor
- ✅ idempotency_key evita cobros duplicados
- ✅ Tests: pago exitoso, tarjeta rechazada, token inválido

---

#### CHANGE-13: Webhook IPN (MercadoPago)

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-13-mercadopago-webhook-ipn` |
| **Historias US** | US-046 (parte 2) |
| **Funcionalidad** | POST /pagos/webhook, validar firma, confirmar status, auto-transicionar pedido |
| **Dependencias** | CHANGE-12, CHANGE-10 |
| **Duración estimada** | 14h |

**Flujo**:
1. MP envía webhook IPN → topic=payment, resource_id={mp_payment_id}
2. Backend valida firma X-Signature
3. Backend consulta API MP para confirmar status real
4. Backend obtiene pedido_id del payment.external_reference
5. Si status=approved y pedido.estado=PENDIENTE:
   - Abre UoW
   - Actualiza tabla Pago
   - Transiciona pedido → CONFIRMADO (vía FSM, decrementa stock)
6. Responde HTTP 200 inmediatamente

**Validaciones**:
- ✅ Firma X-Signature validada
- ✅ Idempotency: webhook duplicado → no procesa dos veces
- ✅ No confiar solo en webhook (consultar API MP)
- ✅ Respuesta 200 inmediata (evitar reintentos MP)

**Criterios de éxito**:
- ✅ Tests: webhook aprobado, rechazado, firma inválida, duplicado

---

### DOMINIO 5: Panel Administrativo

#### CHANGE-14: Panel de Administración (Dashboard)

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-14-admin-dashboard` |
| **Historias US** | US-053, US-054, US-055, US-056, US-057, US-058 |
| **Funcionalidad** | KPIs, gráficos, CRUD categorías/productos/usuarios, stock |
| **Dependencias** | CHANGE-10, CHANGE-06, CHANGE-02 |
| **Duración estimada** | 20h |

**Páginas**:
- `/admin/dashboard` → KPIs + gráficos
- `/admin/categorias` → tabla CRUD
- `/admin/productos` → tabla CRUD
- `/admin/usuarios` → tabla CRUD + assign roles
- `/admin/stock` → tabla editable stock

**KPIs**:
- Total órdenes, ingresos totales, clientes activos
- Distribución por estado (pie chart)
- Ventas por día (line chart)
- Top productos (bar chart)

**Endpoints**:
- GET /api/v1/admin/metricas → KPIs
- GET /api/v1/admin/ventas-por-dia → datos gráficos

---

### DOMINIO 6: Calidad y Documentación

#### CHANGE-15: Validación Global y Manejo de Errores

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-15-validation-error-handling` |
| **Historias US** | US-068, US-074 |
| **Funcionalidad** | RFC 7807 errors, middleware global, logging, sanitización |
| **Dependencias** | CHANGE-00 |
| **Duración estimada** | 12h |

**Formato RFC 7807**:
```json
{
  "type": "https://api.foodstore.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Invalid input data",
  "errors": [
    { "field": "email", "message": "Invalid email format" }
  ],
  "timestamp": "2026-03-31T10:15:30Z",
  "instance": "/api/v1/auth/register"
}
```

**Excepciones personalizadas**:
- ValidationError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, TooManyRequests

**Middleware**:
- Captura todas las excepciones
- Formatea según RFC 7807
- Loguea errores 500 (no 4xx)
- Oculta detalles en producción

---

#### CHANGE-16: Testing y CI/CD

| Campo | Valor |
|-------|-------|
| **Nombre** | `change-16-testing-cicd` |
| **Historias US** | Implícito (calidad) |
| **Funcionalidad** | pytest, coverage, GitHub Actions, README, docs |
| **Dependencias** | Todos |
| **Duración estimada** | 16h |

**Testing**:
- Unit tests: BaseRepository, Services, validation
- Integration tests: endpoints con BD en memoria
- Critical flows: crear pedido (UoW), FSM, webhook
- Coverage goal: > 60% en auth, pedidos, pagos

**CI/CD**:
- GitHub Actions: run tests en cada push + PRs
- Falla si coverage < 60%
- Reporte de cobertura

**Documentación**:
- README.md (setup, stack, testing)
- Swagger UI (/docs)
- Guía de desarrollo
- Instrucciones deploy

---

## 📊 Tabla de Duración por Change

| # | Change | Horas | Dependencias |
|--|--------|-------|-------------|
| 1 | CHANGE-00 (4 sub) | 40h | Ninguna |
| 2 | CHANGE-01 | 20h | CHANGE-00 |
| 3 | CHANGE-02 | 15h | CHANGE-01 |
| 4 | CHANGE-03 | 12h | CHANGE-00 + CHANGE-01 |
| 5 | CHANGE-04 | 8h | CHANGE-03 + CHANGE-01 |
| 6 | CHANGE-05 | 10h | CHANGE-01 |
| 7 | CHANGE-06 | 18h | CHANGE-04 + CHANGE-03 + CHANGE-01 |
| 8 | CHANGE-07 | 12h | CHANGE-06 |
| 9 | CHANGE-08 | 10h | CHANGE-07 + CHANGE-01 |
| 10 | CHANGE-09 | 16h | CHANGE-08 + CHANGE-05 + CHANGE-00d |
| 11 | CHANGE-10 | 18h | CHANGE-09 + CHANGE-01 |
| 12 | CHANGE-11 | 14h | CHANGE-10 + CHANGE-01 |
| 13 | CHANGE-12 | 16h | CHANGE-09 + CHANGE-01 + CHANGE-00 |
| 14 | CHANGE-13 | 14h | CHANGE-12 + CHANGE-10 |
| 15 | CHANGE-14 | 20h | CHANGE-10 + CHANGE-06 + CHANGE-02 |
| 16 | CHANGE-15 | 12h | CHANGE-00 |
| 17 | CHANGE-16 | 16h | Todos |
| | **TOTAL** | **251h** | |

---

## ✅ Criterios de Completitud por Change

Para marcar como **completado y archivado**:

- ✅ **Proposal.md**: Describe QUÉ se construye y POR QUÉ (vinculado a US)
- ✅ **Design.md**: Describe CÓMO técnicamente (modelos, endpoints, schemas)
- ✅ **Tasks.md**: Checklist atómica (cada tarea < 3 horas)
- ✅ **Código implementado**: Todas las tareas completadas
- ✅ **Tests**: Cobertura mínima 70% de módulos nuevos
- ✅ **Git commits**: Atómicos, conventional commits
- ✅ **Sin deuda técnica**: Code review pasado

---

## 🚀 Próximos Pasos

1. **Revisar este mapa**: ¿Está de acuerdo con el orden? ¿Falta algún change?
2. **Aprobar el mapa**: Una vez acordado, NO cambia sin impacto en arquitectura
3. **Iniciar CHANGE-00**: `/opsx:propose change-00a-backend-setup-db`

---

**Generado**: 2026-03-31 | **Especificación**: Food Store v5.0 | **Metodología**: SDD
