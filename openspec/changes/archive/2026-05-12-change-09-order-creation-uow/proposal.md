# Proposal: CHANGE-09 — Order Creation with Unit of Work

## 1. Overview

| Campo | Valor |
|-------|-------|
| **Change** | `change-09-order-creation-uow` |
| **Historias US** | US-035, US-036, US-037, US-038 |
| **Funcionalidad** | POST /pedidos con Unit of Work atomico, snapshots de productos, validacion de stock con SELECT FOR UPDATE |
| **Dependencias** | CHANGE-08 (carrito), CHANGE-05 (direcciones), CHANGE-01 (auth) |
| **Duracion estimada** | 16h |

---

## 2. Problema

Actualmente no existe forma de crear pedidos en el sistema. El carrito en el frontend necesita un endpoint para convertir items en un Pedido con todas las garantias de integridad:

- **Atomicidad**: Todo o nada. Si falla un item, el pedido entero no se crea.
- **Snapshots**: El precio del producto puede cambiar despues del pedido, pero el pedido debe guardar los valores al momento de creacion.
- **Validacion de stock**: Dos pedidos simultaneos para el mismo producto no pueden sobrepasar el stock disponible.
- **Trazabilidad**: Cada pedido nace con un historial de estado inicial (RN-02).
- **Validacion de negocio**: La direccion debe pertenecer al usuario, la forma de pago debe existir y estar habilitada.

---

## 3. Objetivos

1. Crear el modelo `Pedido` con campos para snapshots y referencias necesarias.
2. Crear el modelo `DetallePedido` con snapshots inmutables.
3. Crear el modelo `HistorialEstadoPedido` para audit trail append-only.
4. Crear el modulo `pedidos` con servicio y router.
5. Extender el UoW con `pedidos` repository.
6. Implementar la logica de creacion atomica con validaciones secuenciales.
7. Crear tests de integracion que requieran PostgreSQL (por SELECT FOR UPDATE).
8. NO tocar repositorio remoto (100% local).

---

## 4. User Stories

### US-035: Crear pedido desde carrito

**Criterio de aceptacion**: El sistema debe permitir a un cliente autenticado convertir su carrito en un Pedido atomico.

| Req | Descripcion | Validacion |
|-----|-------------|------------|
| REQ-OD-01 | MUST validar que direccion_id pertenece al usuario (404 si no) | Service |
| REQ-OD-02 | MUST validar que forma_pago_codigo existe y esta habilitado (422 si no) | Service |
| REQ-OD-03 | MUST validar stock suficiente con SELECT FOR UPDATE (422 si no) | Repository |
| REQ-OD-04 | MUST crear Pedido + DetallePedido + HistorialEstadoPedido en una transaccion | UoW |
| REQ-OD-05 | MUST guardar snapshots de nombre y precio en DetallePedido | Service |
| REQ-OD-06 | MUST rollback completo si cualquier paso falla | UoW |
| REQ-OD-07 | MUST calcular total = subtotal + costo_envio | Service |
| REQ-OD-08 | MUST responder 201 + PedidoRead en exito | Router |
| REQ-OD-09 | MUST requerir rol CLIENT o ADMIN | RBAC |

### US-036: Listar pedidos del cliente

**Criterio de aceptacion**: El cliente ve solo sus pedidos, ADMIN/PEDIDOS ven todos.

| Req | Descripcion |
|-----|-------------|
| REQ-OD-10 | GET /pedidos debe filtrar por usuario_id para CLIENT |
| REQ-OD-11 | GET /pedidos debe retornar todos para ADMIN/PEDIDOS |
| REQ-OD-12 | GET /pedidos debe soportar paginacion (skip, limit) |

### US-037: Ver detalle de pedido

**Criterio de aceptacion**: Detalle completo con lineas, trazabilidad y pago.

| Req | Descripcion |
|-----|-------------|
| REQ-OD-13 | GET /pedidos/{id} retorna detalle completo |
| REQ-OD-14 | Cliente solo ve sus propios pedidos (404 si no) |
| REQ-OD-15 | ADMIN/PEDIDOS ven cualquier pedido |

### US-038: Ver historial de estados

**Criterio de aceptacion**: Timeline del pedido orden cronologico.

| Req | Descripcion |
|-----|-------------|
| REQ-OD-16 | GET /pedidos/{id}/historial retorna lista ordenada por created_at ASC |
| REQ-OD-17 | Primer registro tiene estado_desde = NULL (RN-02) |
| REQ-OD-18 | Historial es append-only (nunca UPDATE/DELETE en tabla) |

---

## 5. Modelo de Datos

### 5.1 Pedido (nuevo)

| Campo | Tipo | Restriccion | Notas |
|-------|------|-------------|-------|
| id | BIGSERIAL | PK | Auto |
| usuario_id | BIGINT | FK -> usuarios, NN | Propietario del pedido |
| estado_codigo | VARCHAR(20) | FK -> estados_pedido, NN | Estado inicial: PENDIENTE |
| total | DECIMAL(10,2) | CHECK >= 0, NN | Calculado: subtotal + costo_envio |
| costo_envio | DECIMAL(10,2) | NN, default 50.00 | Valor fijo v1 |
| forma_pago_codigo | VARCHAR(20) | FK -> formas_pago, NN | Forma de pago elegida |
| direccion_id | BIGINT | FK -> direcciones_entrega, SET NULL | NULL = retiro en local |
| notas | TEXT | NULL | Notas opcionales del cliente |
| created_at | TIMESTAMPTZ | NN | TimestampMixin |
| updated_at | TIMESTAMPTZ | NN | TimestampMixin |
| deleted_at | TIMESTAMPTZ | NULL | Soft delete |

### 5.2 DetallePedido (nuevo)

| Campo | Tipo | Restriccion | Notas |
|-------|------|-------------|-------|
| id | BIGSERIAL | PK | Auto |
| pedido_id | BIGINT | FK -> pedidos, NN | Pedido padre |
| producto_id | BIGINT | FK -> productos, NN | Producto ordenado |
| nombre_snapshot | VARCHAR(200) | NN | Snapshot nombre al crear |
| precio_snapshot | DECIMAL(10,2) | NN | Snapshot precio al crear |
| cantidad | INTEGER | CHECK >= 1, NN | Cantidad solicitada |
| personalizacion | INTEGER[] | NULL | IDs de ingredientes removidos |
| created_at | TIMESTAMPTZ | NN | TimestampMixin |

### 5.3 HistorialEstadoPedido (nuevo)

| Campo | Tipo | Restriccion | Notas |
|-------|------|-------------|-------|
| id | BIGSERIAL | PK | Auto |
| pedido_id | BIGINT | FK -> pedidos, NN | Pedido padre |
| estado_desde | VARCHAR(20) | FK -> estados_pedido, NULL | NULL = transicion inicial (RN-02) |
| estado_hacia | VARCHAR(20) | FK -> estados_pedido, NN | Estado al que transiciona |
| observacion | TEXT | NULL | Nota opcional |
| usuario_id | BIGINT | FK -> usuarios, NULL | Quien realizo la transicion |
| created_at | TIMESTAMPTZ | NN | Append-only (nunca updated_at) |

---

## 6. Flujo UoW — Crear Pedido

```
PASO 1: Validar direccion
  - uow.direcciones.get_by_id(direccion_id)
  - Si no existe o deleted_at != NULL -> 404
  - Si direccion.usuario_id != jwt.userId -> 404 (no revelar existencia)

PASO 2: Validar forma de pago
  - Validar que forma_pago_codigo existe en tabla FormasPago
  - Validar que habilitado = true
  - Si no existe o deshabilitado -> 422 ValidationError

PASO 3: Validar stock (SELECT FOR UPDATE)
  - Para cada item en carrito:
    - uow.productos.get_for_update(producto_id) -- SELECT FOR UPDATE
    - Verificar disponible = true
    - Verificar stock_cantidad >= cantidad solicitada
    - Si falla cualquier item -> rollback completo, 422

PASO 4: Calcular totales
  - subtotal = SUM(precio_base * cantidad) para cada item
  - costo_envio = 50.00 (flat rate v1)
  - total = subtotal + costo_envio

PASO 5: Crear Pedido
  - pedido = Pedido(usuario_id, estado_codigo=PENDIENTE, total, costo_envio, ...)
  - uow.pedidos.create(pedido)
  - flush() para obtener pedido.id

PASO 6: Crear DetallePedido (por cada item)
  - detalle = DetallePedido(
      pedido_id=pedido.id,
      producto_id=item.producto_id,
      nombre_snapshot=item.nombre,       -- Snapshot!
      precio_snapshot=item.precio_base, -- Snapshot!
      cantidad=item.cantidad,
      personalizacion=item.personalizacion
    )
  - uow.session.add(detalle)

PASO 7: Crear HistorialEstadoPedido inicial
  - historial = HistorialEstadoPedido(
      pedido_id=pedido.id,
      estado_desde=NULL,  -- RN-02: transicion inicial
      estado_hacia=PENDIENTE,
      usuario_id=usuario_id
    )
  - uow.session.add(historial)

PASO 8: Commit atomico
  - UoW.__exit__ llama session.commit()
  - Si todo OK -> todo persiste
  - Si cualquier excepcion -> rollback, nada persiste
```

---

## 7. Reglas de Negocio

| ID | Regla | Verificacion |
|----|-------|--------------|
| RN-01 | Un estado con es_terminal = true no admite transiciones salientes | CHANGE-10 |
| RN-02 | El primer registro de HistorialEstadoPedido siempre tiene estado_desde = NULL | Service al crear pedido |
| RN-03 | La tabla HistorialEstadoPedido es append-only. Ninguna capa puede emitir UPDATE ni DELETE | BaseRepository no expone update/delete para historial |
| RN-04 | El total, nombre y precio en DetallePedido son un snapshot inmutable al crear el pedido | Service captura valores antes de insertar |
| RN-05 | El costo de envio es fijo en $50.00 para v1 | Service hardcodea el valor |

---

## 8. Dependencias

| Modulo | Relación |
|--------|----------|
| auth-jwt-rbac | get_current_user + require_role(["CLIENT", "ADMIN"]) |
| direcciones | Validacion de ownership del usuario |
| uow-pattern | UnitOfWork con context manager |
| productos | Stock con SELECT FOR UPDATE |

---

## 9. Criterios de Exito

- [ ] POST /pedidos crea pedido atomico o no crea nada (rollback completo)
- [ ] Snapshots de nombre y precio guardados en DetallePedido
- [ ] SELECT FOR UPDATE bloquea filas de productos durante validacion
- [ ] HistorialEstadoPedido creado con estado_desde = NULL
- [ ] Tests de integracion requieren PostgreSQL (marcado en pytest.mark.postgres)
- [ ] 0 operaciones remotas (sin push/pull/merge a repositorio)

---

**Generado**: 2026-05-12 | **Change**: change-09-order-creation-uow | **Metodologia**: SDD
