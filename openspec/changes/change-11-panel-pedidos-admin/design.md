# CHANGE-11: Panel de Gestión de Pedidos — Technical Design

## Context

El proyecto Food Store ya tiene implementado el módulo de pedidos a nivel backend (CHANGE-09 y CHANGE-10):
- Endpoints REST para crear, listar, ver detalle, cambiar estado, y cancelar pedidos
- FSM (Finite State Machine) para transiciones de estado con validación
- Frontend básico: AdminOrders.tsx con tabla de pedidos y paginación

Sin embargo, faltan capacidades críticas para que el equipo de pedidos opere efectivamente:
- No hay filtros por estado o fecha
- No hay búsqueda por cliente
- No hay modal de detalle con tabs
- No hay visualización timeline del historial

Este change extiende el módulo de pedidos existente con UI completa.

## Goals / Non-Goals

**Goals:**
1. Agregar filtros por estado, rango de fechas, y búsqueda por cliente al listado de pedidos
2. Crear modal de detalle con tabs: Resumen, Líneas, Historial, Pago
3. Implementar HistorialTimeline visual para transiciones de estado
4. Agregar botones de transición de estado contextuales según rol y estado actual
5. Mantener compatibilidad con vistas de CLIENT (sus propios pedidos)

**Non-Goals:**
- No se implementará exportación a PDF/Excel (futuro change)
- No se implementará notificaciones en tiempo real (WebSocket) — fuera de scope
- No se modifica la lógica de negocio del FSM (ya implementado en CHANGE-10)
- No se crean nuevos endpoints backend — solo se extiende existentes

## Decisions

### D1: Filtros en backend vs frontend

**Opción A**: Filtros en backend (query params)
- ✅ Ventajas: paginación correcta con filtros, menos datos transferidos
- ❌ Desventajas: más llamadas al servidor al cambiar filtros

**Opción B**: Filtros en frontend (Filter UI pero todos los datos cargados)
- ❌ Ventajas: respuesta instantánea
- ❌ Desventajas: ineficiente con muchos pedidos, paginación incorrecta

**Decisión**: Opción A — filtros en backend via query params. El endpoint existente ya soporta paginación, se agregan filtros como query params adicionales.

**Alternativa considerada**: Usar TanStack Query con keepPreviousData para UX fluida — se implementará en frontend.

---

### D2: Modal de detalle — diseño de tabs

**Opción A**: 4 tabs separados en modal
- ✅ Ventajas: organizado, cada tab tiene responsabilidad única
- ❌ Desventajas: más código, más componentes

**Opción B**: Scroll vertical con secciones
- ❌ Ventajas: más simple
- ❌ Desventajas: difícil de navegar con mucho contenido

**Decisión**: Opción A — 4 tabs. Facilita la navegación y mantiene cada sección enfocada.

**Tabs definidos**:
1. **Resumen**: ID, cliente, estado, total, fecha, dirección, notas
2. **Líneas**: Tabla con productos, cantidades, precios snapshot, personalizaciones
3. **Historial**: Timeline visual de transiciones con timestamps y actores
4. **Pago**: Estado de pago, método, ID de transacción (si existe)

---

### D3: HistorialTimeline — implementación

**Opción A**: Componente timeline personalizado con Tailwind
- ✅ Ventajas: control total sobre styling, puede seguir design system
- ❌ Desventajas: más código

**Opción B**: Usar librería externa (ej: react-chrono)
- ❌ Ventajas: rápido
- ❌ Desventajas: dependencia extra,可能的 styled不一致

**Decisión**: Opción A — componente personalizado. Mantiene consistencia con el design system del proyecto.

**Diseño del timeline**:
```
● PENDIENTE ──→ CONFIRMADO ──→ EN_PREPARACIÓN ──→ EN_CAMINO ──→ ENTREGADO
   12:30          14:15            15:45             16:30
   (Cliente)      (Admin)         (Pedidos)        (Pedidos)
```

---

### D4: StateTransitionButtons — contexto por rol

**Lógica de visibilidad**:
- CLIENT: solo puede ver su propio pedido, ningún botón de transición
- PEDIDOS: puede transicionar CONFIRMADO → EN_PREP, EN_PREP → EN_CAMINO, EN_CAMINO → ENTREGADO
- ADMIN: puede transicionar cualquier transición + cancelar desde cualquier estado

**Decisión**: Implementar función `getTransicionesDisponibles(estado, roles)` que retorna array de transiciones permitidas. Ya existe parcialmente en el código actual (se migra a feature de pedidos).

---

### D5: Estructura de archivos frontend

**Pattern**: Feature-Sliced Design
```
frontend/src/features/pedidos/
├── api.ts              # endpoints axios
├── types.ts            # tipos TypeScript (ya existe)
├── hooks/
│   └── index.ts        # usePedidos, useTransicionEstado, etc (ya existe)
└── components/
    ├── OrderFilters.tsx        # NUEVO: filtros y búsqueda
    ├── OrderDetailModal.tsx    # NUEVO: modal con tabs
    ├── HistorialTimeline.tsx  # NUEVO: timeline visual
    └── OrdersTable.tsx        # MEJORAR: agregar columna cliente
```

**Decisión**: Crear subcarpeta `components/` dentro de `features/pedidos/` para organizar los nuevos componentes.

---

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| **R1**: Filtros con muchas opciones pueden degradar performance | Medio | Agregar índices en BD si es necesario; limitar resultados a 1000 |
| **R2**: Modal de detalle puede requerir muchos datos (N+1) | Medio | Agregar endpoint optimizado para detalle o usar include en servicio |
| **R3**: Timeline vacío si el pedido no tiene historial | Bajo | Mostrar mensaje "Sin transiciones" en el timeline |
| **R4**: Diferentes roles ven diferentes botones | Bajo | Probar con usuarios de cada rol |

---

## Migration Plan

1. **Backend** (Día 1):
   - Agregar query params al router: `estado`, `desde`, `hasta`, `busqueda`
   - Modificar service para aplicar filtros
   - Probar con curl/Postman

2. **Frontend - Filtros** (Día 2):
   - Crear componente OrderFilters.tsx
   - Integrar con TanStack Query
   - Probar con datos reales

3. **Frontend - Modal y Tabs** (Día 3):
   - Crear OrderDetailModal.tsx
   - Crear tabs: Resumen, Líneas, Historial, Pago
   - Integrar con API existente

4. **Frontend - Timeline** (Día 4):
   - Crear HistorialTimeline.tsx
   - Estilizar según diseño decided
   - Probar con pedidos que tienen historial

5. **Testing y polish** (Día 5):
   - Probar con diferentes roles
   - Ajustar estilos responsive
   - Verificar accesibilidad

**Rollback**: Si hay problemas, el backend sigue funcionando — los cambios son enhancement, no breaking change.

---

## Open Questions

1. **Q1**: ¿El nombre del cliente debe incluirse en la respuesta del listado? Actualmente `PedidoRead` no tiene `usuario_id` para mostrar. Verificar si se necesita agregar campo `cliente_nombre` al schema.

2. **Q2**: ¿La búsqueda por cliente usa LIKE parcial o exacto? Probablemente LIKE `%texto%` en email o nombre.

3. **Q3**: ¿El tab de "Pago" debe mostrar información del módulo de pagos (CHANGE-12)? Este change es independiente — el tab mostrará lo que exista (puede estar vacío si CHANGE-12 no está implementado).

4. **Q4**: ¿Los filtros deben ser persistentes en URL (query params del router)? Sí, para facilitar compartir enlaces.