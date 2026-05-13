# order-management-ui Specification

## Purpose
Panel de gestión de pedidos para ADMIN y PEDIDOS con filtros, búsqueda, y modal de detalle con tabs.

## ADDED Requirements

### Requirement: OrdersTable — Columna Cliente

La tabla de pedidos SHALL mostrar la información del cliente (nombre/email) en una columna dedicada para que el gestor identifique rápidamente quién hizo el pedido.

#### Scenario: Mostrar nombre del cliente en tabla
- **GIVEN** pedido con usuario_id=5 que tiene email="cliente@test.com" y nombre="Juan Pérez"
- **WHEN** AdminOrders renderiza la tabla de pedidos
- **THEN** la columna "Cliente" muestra "Juan Pérez (cliente@test.com)"

#### Scenario: Cliente sin nombre registrado
- **GIVEN** pedido con usuario_id=10 que solo tiene email="sinemail@test.com" sin nombre
- **WHEN** AdminOrders renderiza la tabla
- **THEN** la columna "Cliente" muestra solo el email "sinemail@test.com"

---

### Requirement: OrderFilters — Filtro por Estado

El sistema SHALL permitir filtrar pedidos por estado usando un dropdown con todos los estados posibles.

#### Scenario: Filtrar pedidos por estado CONFIRMADO
- **GIVEN** 10 pedidos en el sistema (3 CONFIRMADOS, 4 PENDIENTES, 3 ENTREGADOS)
- **WHEN** el usuario selecciona "CONFIRMADO" en el dropdown de estado
- **THEN** la tabla muestra solo los 3 pedidos con estado_codigo=CONFIRMADO
- **AND** la paginación muestra total=3

#### Scenario: Limpiar filtro de estado
- **GIVEN** filtro de estado aplicado (CONFIRMADO)
- **WHEN** el usuario hace click en "Limpiar" o selecciona "Todos los estados"
- **THEN** la tabla muestra todos los pedidos sin filtro

---

### Requirement: OrderFilters — Filtro por Rango de Fechas

El sistema SHALL permitir filtrar pedidos por rango de fechas (fecha de creación).

#### Scenario: Filtrar pedidos por rango de fechas
- **GIVEN** pedidos creados en diferentes fechas (2026-01-01, 2026-01-15, 2026-02-01, 2026-03-01)
- **WHEN** el usuario selecciona fecha_desde=2026-01-10 y fecha_hasta=2026-02-15
- **THEN** la tabla muestra solo los pedidos creados entre esas fechas

#### Scenario: Filtro de fecha sin rango (solo desde)
- **GIVEN** pedidos en diferentes fechas
- **WHEN** el usuario selecciona solo fecha_desde=2026-02-01 (sin fecha_hasta)
- **THEN** la tabla muestra todos los pedidos desde 2026-02-01 en adelante

#### Scenario: Filtro de fecha sin rango (solo hasta)
- **GIVEN** pedidos en diferentes fechas
- **WHEN** el usuario selecciona solo fecha_hasta=2026-01-31 (sin fecha_desde)
- **THEN** la tabla muestra todos los pedidos hasta 2026-01-31

---

### Requirement: OrderFilters — Búsqueda por Cliente o ID

El sistema SHALL permitir buscar pedidos por número de pedido o nombre/email del cliente.

#### Scenario: Buscar por número de pedido
- **GIVEN** pedido con id=42 existe en el sistema
- **WHEN** el usuario escribe "42" en el input de búsqueda
- **THEN** la tabla muestra solo el pedido con id=42

#### Scenario: Buscar por nombre de cliente
- **GIVEN** pedido hecho por "Juan Pérez" existe en el sistema
- **WHEN** el usuario escribe "Juan" en el input de búsqueda
- **THEN** la tabla muestra los pedidos hechos por clientes cuyo nombre contiene "Juan"

#### Scenario: Buscar por email de cliente
- **GIVEN** pedido hecho por cliente con email="maria@gmail.com"
- **WHEN** el usuario escribe "maria@gmail" en el input de búsqueda
- **THEN** la tabla muestra los pedidos de ese cliente

#### Scenario: Búsqueda sin resultados
- **GIVEN** no existen pedidos que coincidan con la búsqueda
- **WHEN** el usuario escribe "busqueda-inexistente-12345"
- **THEN** la tabla muestra mensaje "No hay pedidos que coincidan con la búsqueda"

---

### Requirement: OrderDetailModal — Tab Resumen

El modal de detalle SHALL mostrar un tab "Resumen" con información general del pedido.

#### Scenario: Mostrar información de resumen
- **GIVEN** pedido existe con: id=15, usuario_id=3, estado_codigo=CONFIRMADO, total=1250.00, forma_pago_codigo=MERCADOPAGO
- **WHEN** el usuario abre el modal de detalle y selecciona tab "Resumen"
- **THEN** el tab muestra: ID, Cliente, Estado, Total, Forma de Pago, Fecha de creación, Notas

---

### Requirement: OrderDetailModal — Tab Líneas

El modal de detalle SHALL mostrar un tab "Líneas" con la tabla de productos pedidos.

#### Scenario: Mostrar líneas del pedido
- **GIVEN** pedido tiene 3 líneas: Pizza (2 unidades), Coca-Cola (3 unidades), Guarnición (1 unidad)
- **WHEN** el usuario abre el modal de detalle y selecciona tab "Líneas"
- **THEN** el tab muestra una tabla con columnas: Producto, Cantidad, Precio Unitario, Subtotal
- **AND** cada fila muestra los datos del snapshot correspondientes

#### Scenario: Mostrar personalizaciones en líneas
- **GIVEN** línea de pedido tiene personalizacion=[1, 2] (sin queso, sin tomate)
- **WHEN** el usuario ve el tab "Líneas"
- **THEN** la columna "Notas" muestra "Sin queso, Sin tomate"

---

### Requirement: OrderDetailModal — Tab Historial

El modal de detalle SHALL mostrar un tab "Historial" con el timeline visual de transiciones.

#### Scenario: Mostrar historial de estados
- **GIVEN** pedido tiene historial: PENDIENTE→CONFIRMADO (10:00), CONFIRMADO→EN_PREPARACION (11:30), EN_PREPARACION→EN_CAMINO (12:00)
- **WHEN** el usuario abre el modal de detalle y selecciona tab "Historial"
- **THEN** el tab muestra el timeline con las 3 transiciones, timestamps, y actor de cada cambio

---

### Requirement: OrderDetailModal — Tab Pago

El modal de detalle SHALL mostrar un tab "Pago" con información del estado de pago.

#### Scenario: Mostrar información de pago
- **GIVEN** pedido tiene forma_pago_codigo=MERCADOPAGO, y existe registro de Pago asociado
- **WHEN** el usuario abre el modal de detalle y selecciona tab "Pago"
- **THEN** el tab muestra: Método de pago, Estado del pago, ID de transacción (si existe), Fecha de pago

#### Scenario: Mostrar que no hay información de pago
- **GIVEN** pedido fue creado pero no tiene registro de Pago (ej: pago en efectivo)
- **WHEN** el usuario abre el tab "Pago"
- **THEN** el tab muestra "Pago en efectivo - Sin registro de transacción"

---

### Requirement: StateTransitionButtons — Botones Contextuales

El sistema SHALL mostrar botones de acción para transicionar el estado del pedido, contextualizados según el rol del usuario y el estado actual del pedido.

#### Scenario: Botones para PEDIDOS en estado CONFIRMADO
- **GIVEN** pedido con estado_codigo=CONFIRMADO, usuario con rol PEDIDOS
- **WHEN** el usuario visualiza los botones de acción
- **THEN** ve botón "Iniciar Preparación" (transiciona a EN_PREPARACION)

#### Scenario: Botones para ADMIN en estado PENDIENTE
- **GIVEN** pedido con estado_codigo=PENDIENTE, usuario con rol ADMIN
- **WHEN** el usuario visualiza los botones de acción
- **THEN** ve botón "Confirmar" y botón "Cancelar" (con modal de motivo)

#### Scenario: Sin botones para estado terminal
- **GIVEN** pedido con estado_codigo=ENTREGADO o CANCELADO
- **WHEN** el usuario visualiza los botones de acción
- **THEN** ve mensaje "Sin acciones disponibles" (estados terminales no tienen transiciones)

#### Scenario: CLIENT no ve botones de transición
- **GIVEN** pedido propio con cualquier estado, usuario con rol CLIENT
- **WHEN** el usuario visualiza los botones de acción
- **THEN** no ve botones de transición (CLIENT solo puede ver, no gestionar)