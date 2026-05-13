# Task Breakdown — CHANGE-10: Máquina de Estados (FSM) ✅ COMPLETADO

## Summary
- **Total Tasks**: 18
- **Estimated Hours**: 22-26 hours
- **Priority Order**: Backend Core → Stock → Endpoints → Tests → Frontend
- **Status**: ✅ ALL COMPLETED

---

## Phase 1: Backend — FSM Core ✅

### 1.1 Define FSM transition map constant in service.py ✅
**Files**: `backend/app/modules/pedidos/fsm.py` (NEW), `service.py` (MODIFIED)  
**Status**: ✅ COMPLETE - Transition dataclass, ESTADOS_VALIDOS dict, FSM_TRANSITION_MAP

### 1.2 Create _validar_transicion() method ✅
**Files**: `backend/app/modules/pedidos/service.py`  
**Status**: ✅ COMPLETE - Valida origin, target, terminal state, roles, motivo requirement

### 1.3 Create _es_estado_terminal() helper ✅
**Files**: `backend/app/modules/pedidos/service.py`  
**Status**: ✅ COMPLETE - Wrapper around es_estado_terminal from fsm.py

---

## Phase 2: Backend — Stock Operations ✅

### 2.1 Create _decrementar_stock_en_pedido() method ✅
**Files**: `backend/app/modules/pedidos/service.py`  
**Status**: ✅ COMPLETE - Uses SELECT FOR UPDATE, decrements stock_cantidad

### 2.2 Create _restaurar_stock_en_pedido() method ✅
**Files**: `backend/app/modules/pedidos/service.py`  
**Status**: ✅ COMPLETE - Increments stock_cantidad for cancellation from CONFIRMADO/EN_PREP

---

## Phase 3: Backend — Endpoints ✅

### 3.1 Add AvanzarEstadoRequest schema ✅
**Files**: `backend/app/modules/pedidos/schemas.py`  
**Status**: ✅ COMPLETE - nuevo_estado, motivo fields with validation

### 3.2 Add PATCH /pedidos/{id}/estado endpoint ✅
**Files**: `backend/app/modules/pedidos/router.py`  
**Status**: ✅ COMPLETE - Validates transition, executes stock ops, persists via UoW

### 3.3 Add DELETE /pedidos/{id} endpoint ✅
**Files**: `backend/app/modules/pedidos/router.py`  
**Status**: ✅ COMPLETE - CLIENT cancel own PENDIENTE, ADMIN/PEDIDOS cancel PENDIENTE/CONFIRMADO

---

## Phase 4: Backend — Tests ✅

### 4.1 Test FSM map validation ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - Tests all 6 states, forward/cancel transitions, terminal detection

### 4.2 Test valid transitions ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - PENDIENTE→CONFIRMADO, CONFIRMADO→EN_PREP, EN_PREP→EN_CAMINO, EN_CAMINO→ENTREGADO

### 4.3 Test invalid transitions rejected ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - PENDIENTE→EN_CAMINO, CONFIRMADO→ENTREGADO, backward transitions

### 4.4 Test terminal state rejection ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - ENTREGADO and CANCELADO reject any transition

### 4.5 Test role-based permissions ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - CLIENT can cancel own PENDIENTE, PEDIDOS cannot cancel CONFIRMADO

### 4.6 Test stock decrement on CONFIRMADO ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - Verifies stock decrements by cantidad on PENDIENTE→CONFIRMADO

### 4.7 Test stock restore on CANCELADO ✅
**Files**: `backend/tests/integration/test_pedidos_fsm.py`  
**Status**: ✅ COMPLETE - Verifies stock restores on CONFIRMADO→CANCELADO and EN_PREP→CANCELADO

---

## Phase 5: Frontend — AdminOrders UI ✅

### 5.1 Create pedidos API and hooks ✅
**Files**: `frontend/src/features/pedidos/api.ts`, `frontend/src/features/pedidos/hooks/index.ts`  
**Status**: ✅ COMPLETE - getPedidos, transicionarEstado, cancelarPedido, useTransicionEstado, useCancelarPedido

### 5.2 Update AdminOrders page ✅
**Files**: `frontend/src/pages/AdminOrders.tsx`  
**Status**: ✅ COMPLETE - Data table with ID, Estado, Total, Fecha, Acciones columns

### 5.3 Add state transition buttons ✅
**Files**: `frontend/src/pages/AdminOrders.tsx`  
**Status**: ✅ COMPLETE - Buttons per row based on current state and user role

### 5.4 Add cancel dialog with motivo ✅
**Files**: `frontend/src/pages/AdminOrders.tsx`  
**Status**: ✅ COMPLETE - Modal with textarea for motivo (required)

### 5.5 Add toast feedback ✅
**Files**: `frontend/src/pages/AdminOrders.tsx`  
**Status**: ✅ COMPLETE - Success toast on transition, error toast on failures

---

## Dependencies Summary

| Task | Depends On | Status |
|------|------------|--------|
| 1.1 | Specs | ✅ |
| 1.2 | 1.1 | ✅ |
| 1.3 | 1.1 | ✅ |
| 2.1 | 1.2, existing repo method | ✅ |
| 2.2 | 2.1 | ✅ |
| 3.1 | Specs | ✅ |
| 3.2 | 1.2, 1.3, 2.1, 2.2, 3.1 | ✅ |
| 3.3 | 3.2, 2.2 | ✅ |
| 4.1 | 1.1 | ✅ |
| 4.2 | 1.2, 1.3 | ✅ |
| 4.3 | 1.2 | ✅ |
| 4.4 | 1.3 | ✅ |
| 4.5 | 1.2 | ✅ |
| 4.6 | 2.1 | ✅ |
| 4.7 | 2.2 | ✅ |
| 5.1 | 3.2, 3.3 | ✅ |
| 5.2 | 5.1 | ✅ |
| 5.3 | 5.2 | ✅ |
| 5.4 | 5.3 | ✅ |
| 5.5 | 5.3 | ✅ |
