# Specification: Mis Pedidos (Vista Cliente)

## ADDED Requirements

### Requirement: Cliente puede listar sus pedidos con paginación

El sistema MUST mostrar al cliente autenticado una lista paginada de sus propios pedidos ordenados por fecha descendente (más reciente primero). La respuesta del backend incluye `page`, `size` y `total` para controles de navegación.

#### Scenario: Listado con paginacióndefault
- **WHEN** el cliente accede a `/mis-pedidos` sin parámetros de query
- **THEN** el sistema muestra los primeros 10 pedidos más recientes con número, fecha, estado badge y total

#### Scenario: Navegación entre páginas
- **WHEN** el cliente hace clic en "Siguiente" o cambia a página 2
- **THEN** el sistema muestra los pedidos 11-20 con la misma estructura

#### Scenario: Listado vacío
- **WHEN** el cliente no tiene ningún pedido en el sistema
- **THEN** el sistema muestra un mensaje de "Sin pedidos" con un enlace al catálogo de productos

### Requirement: Cliente puede filtrar sus pedidos por estado

El sistema MUST permitir filtrar la lista de pedidos por código de estado mediante query param `?estado=<codigo>`. Los filtros disponibles deben coincidir con los estados del FSM (PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO).

#### Scenario: Filtrar por estado PENDIENTE
- **WHEN** el cliente selecciona filtro "Pendiente" en la UI
- **THEN** la URL cambia a `/mis-pedidos?estado=PENDIENTE` y solo se muestran pedidos en ese estado

#### Scenario: Quitar filtro
- **WHEN** el cliente hace clic en "Limpiar filtros" o "Todos"
- **THEN** la URL vuelve a `/mis-pedidos` y se muestran todos los pedidos del cliente

### Requirement: Cliente puede ver el detalle completo de un pedido

El sistema MUST mostrar la página de detalle del pedido con la siguiente información:
- Resumen: ID, fecha de creación, estado actual (con badge colorizado), total, costo de envío
- Líneas: lista de productos con nombre, cantidad, precio unitario (snapshot al momento de compra), observaciones
- Historial: timeline de transiciones de estado con fecha/hora y actor (SISTEMA o nombre del usuario)
- Pago: estado del pago en MercadoPago (approved, rejected, pending, none)

#### Scenario: Ver detalle de pedido propio
- **WHEN** el cliente hace clic en un pedido de la lista
- **THEN** el sistema navega a `/mis-pedidos/{pedidoId}` y carga el detalle con las 4 tabs

#### Scenario: Ver detalle de pedido de otro usuario
- **WHEN** el cliente intenta acceder directamente a `/mis-pedidos/{pedidoId}` de otro cliente
- **THEN** el backend retorna HTTP 403 Forbidden y la UI muestra error de acceso denegado

### Requirement: Cliente puede ver el timeline de historial de estados

El sistema MUST mostrar un timeline visual con todas las transiciones de estado del pedido, incluyendo:
- Fecha y hora de cada transición
- Estado origen (FROM) y estado destino (TO)
- Actor: nombre del usuario que realizó el cambio o "SISTEMA" si fue automático

#### Scenario: Timeline con múltiples transiciones
- **WHEN** el pedido tiene historial: PENDIENTE → CONFIRMADO → EN_PREPARACION
- **THEN** el timeline muestra 3 nodos conectados cronológicamente con las fechas y actores

#### Scenario: Transición automática sin usuario
- **WHEN** el pedido transiciona de PENDIENTE a CONFIRMADO por aprobación de pago (webhook MP)
- **THEN** el actor se muestra como "SISTEMA" y no como un usuario específico

### Requirement: Cliente puede cancelar un pedido desde estado PENDIENTE

El sistema MUST permitir la cancelación de un pedido únicamente cuando su estado_codigo sea PENDIENTE. El cliente debe proporcionar un motivo obligatorio que se almacenará en el historial.

#### Scenario: Cancelar pedido exitosamente
- **WHEN** el cliente hace clic en "Cancelar pedido" y confirma con motivo "Ya no lo necesito"
- **THEN** el sistema: (1) cambia estado a CANCELADO, (2) registra en historial con motivo, (3) muestra toast de éxito, (4) redirecciona al listado

#### Scenario: Botón cancelar oculto para estado no PENDIENTE
- **WHEN** el cliente visualiza un pedido en estado CONFIRMADO o posterior
- **THEN** el botón "Cancelar pedido" no se muestra en la UI

#### Scenario: Cancelar sin motivo
- **WHEN** el cliente intenta confirmar la cancelación sin填写 motivo
- **THEN** el sistema muestra mensaje de error "El motivo es obligatorio" y no envía la request

### Requirement: Cliente puede ver el estado del pago del pedido

El sistema MUST mostrar el estado del pago associated al pedido, consultando el endpoint `GET /api/v1/pagos/{pedido_id}`. Los estados posibles son: approved, rejected, in_process, pending, o "Sin información de pago".

#### Scenario: Pago aprobado
- **WHEN** el pago del pedido está aprobado en MercadoPago
- **THEN** la UI muestra badge verde "Pagado" o "Aprobado" en la tab de Pago

#### Scenario: Pago pendiente
- **WHEN** el pago está en proceso o pending
- **THEN** la UI muestra badge amarillo "Pendiente" o "Procesando"

#### Scenario: Sin información de pago
- **WHEN** el pedido no tiene registro de pago asociado (ej: pedido en efectivo)
- **THEN** la UI muestra "Sin información de pago" con styling neutral

### Requirement: Skeleton loaders durante carga de datos

El sistema MUST mostrar skeleton loaders mientras se realiza el fetch de datos de pedidos para mejorar la experiencia de usuario.

#### Scenario: Carga inicial del listado
- **WHEN** el usuario accede a `/mis-pedidos` y la request está en vuelo
- **THEN** la UI muestra 5 skeleton cards simulando la estructura de un pedido

#### Scenario: Carga de detalle
- **WHEN** el usuario accede a `/mis-pedidos/{id}` y la request está en vuelo
- **THEN** la UI muestra skeleton loaders en las 4 tabs hasta que los datos llegan

### Requirement: Manejo de errores con toast notifications

El sistema MUST mostrar notificaciones toast para operaciones exitosas y fallidas.

#### Scenario: Error al cargar pedidos
- **WHEN** la request a `GET /api/v1/pedidos` falla (500, network error)
- **THEN** la UI muestra toast de error "Error al cargar pedidos" con retry button

#### Scenario: Éxito al cancelar
- **WHEN** la request a `DELETE /api/v1/pedidos/{id}` retorna 200 OK
- **THEN** la UI muestra toast verde "Pedido cancelado exitosamente"

---

## FSM State Transitions (Referencia)

El historial de pedidos sigue el FSM definido en CHANGE-10:

```
PENDIENTE ──[pago aprobado]──→ CONFIRMADO ──[gestión]──→ EN_PREPARACIÓN
                    ↓                 ↓                          ↓
                 CANCELADO ←───────────────── [solo ADMIN]
                     ↓                                             ↓
                 [terminal]                                  EN_CAMINO → ENTREGADO
                                                                ↓        ↓
                                                           [solo PEDIDOS] [terminal]
```

Estados terminales: ENTREGADO, CANCELADO - sin transiciones salientes.