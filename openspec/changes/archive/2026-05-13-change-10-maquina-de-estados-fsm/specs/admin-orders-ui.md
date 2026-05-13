# Delta Spec — CHANGE-10: Admin Orders UI

## Capability: admin-orders-ui

### Purpose
Replace placeholder AdminOrders page with a functional order management view featuring a data table, filters, and contextual transition action buttons.

### Requirements

#### ADMIN-UI-01: Order List Table
The AdminOrders page MUST display a table of all pedidos (for ADMIN/PEDIDOS roles) with columns: ID, Cliente, Estado, Total, Fecha, Acciones. Data fetched via TanStack Query `useQuery`.

#### Scenario: Admin views all orders
- GIVEN an authenticated ADMIN user on /admin/pedidos
- WHEN the page loads
- THEN a table renders with all orders from the API
- AND each row shows ID, estado_codigo, total, created_at
- AND empty state shows "No hay pedidos" when none exist

#### ADMIN-UI-02: State Transition Buttons
The system MUST render action buttons per row based on current state and user role:
- PENDIENTE: "Cancelar" button (for CLIENT/PEDIDOS/ADMIN)
- CONFIRMADO: "En Preparación" + "Cancelar" buttons (for PEDIDOS/ADMIN)
- EN_PREP: "En Camino" + "Cancelar" buttons (ADMIN sees Cancelar, PEDIDOS sees En Camino)
- EN_CAMINO: "Entregado" button (for PEDIDOS/ADMIN)
- ENTREGADO/CANCELADO: No action buttons (terminal)

#### Scenario: Transition buttons available per role
- GIVEN a PEDIDOS user viewing a CONFIRMADO order
- WHEN the table renders
- THEN "En Preparación" and "Cancelar" buttons are visible
- AND clicking "En Preparación" calls PATCH /pedidos/{id}/estado
- AND the UI updates optimistically showing loading state

#### ADMIN-UI-03: Cancel Dialog with motivo
When clicking "Cancelar", the system MUST show a modal/dialog with a textarea for `motivo` (required) and confirm/cancel buttons.

#### Scenario: Cancel dialog validates motivo
- GIVEN the cancel dialog is open
- WHEN the user clicks confirm without filling motivo
- THEN the dialog shows validation error "El motivo es obligatorio"
- AND the API call is NOT made

#### ADMIN-UI-04: State Change Feedback
The system MUST show success toast on successful transitions and error toast on failures, then invalidate the orders query to refresh the list.

#### Scenario: Error feedback on failed transition
- GIVEN an attempted invalid transition (e.g., PENDIENTE→EN_CAMINO)
- WHEN the API returns 422
- THEN a toast shows "Transición no válida"
- AND the order state remains unchanged in the UI
