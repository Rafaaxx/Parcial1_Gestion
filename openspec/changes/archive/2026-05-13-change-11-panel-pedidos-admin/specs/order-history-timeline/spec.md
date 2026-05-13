# order-history-timeline Specification

## Purpose
Visualización Timeline del historial de transiciones de estado de pedidos — muestra la secuencia de estados con timestamps y actor responsable.

## ADDED Requirements

### Requirement: HistorialTimeline — Visualización Vertical

El sistema SHALL mostrar el historial de estados como una línea vertical con nodos representando cada transición.

#### Scenario: Timeline con múltiples transiciones
- **GIVEN** pedido con historial: PENDIENTE→CONFIRMADO (2026-01-15 10:30, actor=Admin), CONFIRMADO→EN_PREPARACION (2026-01-15 11:15, actor=Pedidos)
- **WHEN** se renderiza el HistorialTimeline
- **THEN** muestra:
  - Nodo 1: PENDIENTE → CONFIRMADO (10:30 - Admin)
  - Línea conectiva
  - Nodo 2: CONFIRMADO → EN_PREPARACION (11:15 - Pedidos)

#### Scenario: Primer estado (inicial) sin transición entrante
- **GIVEN** pedido acabdo de crear con solo estado inicial PENDIENTE (sin historial aún)
- **WHEN** se renderiza el timeline
- **THEN** muestra nodo único: "PENDIENTE (estado inicial)"

---

### Requirement: HistorialTimeline — Formato de Timestamp

Cada nodo del timeline SHALL incluir el timestamp de la transición en formato legible.

#### Scenario: Formato de fecha y hora
- **GIVEN** transición creada el 15 de enero de 2026 a las 10:30:45
- **WHEN** se muestra en el timeline
- **THEN** muestra "15/01/2026 10:30" (formato argentino, 24hs)

#### Scenario: Mostrar actor de la transición
- **GIVEN** transición ejecutada por usuario con email "admin@foodstore.com"
- **WHEN** se muestra el nodo
- **THEN** incluye el nombre/email del actor: "CONFIRMADO (por: admin@foodstore.com)"

#### Scenario: Transición automática (sistema)
- **GIVEN** transición ejecutada automáticamente por el sistema (ej: por webhook de pago)
- **WHEN** se muestra el nodo
- **THEN** muestra "Sistema" como actor

---

### Requirement: HistorialTimeline — Estados Posibles

El timeline SHALL representar correctamente los 6 estados del FSM de pedidos.

#### Scenario: Timeline completo del flujo feliz
- **GIVEN** pedido que transitó: PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO
- **WHEN** se renderiza el timeline
- **THEN** muestra los 5 nodos en orden cronológico, cada uno con su timestamp y actor

#### Scenario: Timeline con cancelación
- **GIVEN** pedido que transitó: PENDIENTE → CONFIRMADO → CANCELADO
- **WHEN** se renderiza el timeline
- **THEN** muestra: PENDIENTE → CONFIRMADO → CANCELADO (con icono de X indicando terminación)

---

### Requirement: HistorialTimeline — Estados Vacíos

El sistema SHALL manejar el caso donde no hay historial (pedido nuevo).

#### Scenario: Sin transiciones
- **GIVEN** pedido acabdo de crear (menos de 1 minuto)
- **WHEN** se renderiza el timeline
- **THEN** muestra mensaje: "Este pedido aún no tiene transiciones de estado"

---

### Requirement: HistorialTimeline — Responsive Design

El timeline SHALL adaptarse correctamente a diferentes tamaños de pantalla.

#### Scenario: Mobile ( < 640px )
- **GIVEN** pantalla de celular
- **WHEN** se renderiza el timeline
- **THEN** los nodos se muestran en diseño vertical compacto, texto truncado si es necesario

#### Scenario: Desktop ( >= 1024px )
- **GIVEN** pantalla de escritorio
- **WHEN** se renderiza el timeline
- **THEN** diseño espaciado, toda la información visible sin truncamiento