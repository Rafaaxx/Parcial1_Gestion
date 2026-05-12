# Design: CHANGE-09 — Order Creation with Unit of Work

## 1. Overview

Este documento describe la implementacion tecnica del cambio `change-09-order-creation-uow`. Cubre los modelos de datos, schemas Pydantic, servicios, repositories, router, UoW extendido, migrations y tests.

**Restricciones del change:**
- Prohibido tocar repo remoto (CERO push/pull/merge). 100% local.
- Tests DEBEN exigir PostgreSQL para SELECT FOR UPDATE (SQLite falla aqui).

---

## 2. Estructura de Archivos

```
backend/
├── app/
│   ├── models/
│   │   ├── pedido.py              # Pedido, DetallePedido, HistorialEstadoPedido
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── pedido_repository.py   # PedidoRepository, DetallePedidoRepository
│   │   ├── historial_repository.py  # HistorialEstadoPedidoRepository (append-only)
│   │   └── __init__.py
│   ├── modules/
│   │   └── pedidos/
│   │       ├── schemas.py         # Pydantic schemas (request/response)
│   │       ├── service.py         # PedidoService
│   │       ├── router.py          # Endpoints
│   │       └── __init__.py
│   ├── uow.py                     # Extender con pedidos repository
│   └── main.py                    # Registrar router
├── migrations/versions/
│   └── 008_add_pedidos_tables.py  # Migration Alembic
└── tests/
    ├── integration/
    │   └── test_pedidos_api.py    # Tests que requieren PostgreSQL
    └── conftest.py                # Fixture que exige PostgreSQL
```

---

## 3. Modelos de Datos

### 3.1 Pedido (`app/models/pedido.py`)

```python
class Pedido(BaseModel, TimestampMixin, SoftDeleteMixin, table=True):
    """Pedido entity with shipping cost and payment method references"""
    __tablename__ = "pedidos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False, index=True)
    estado_codigo: str = Field(
        foreign_key="estados_pedido.codigo",
        nullable=False,
        max_length=20,
        index=True
    )
    total: Decimal = Field(
        sa_column_kwargs={"nullable": False},
        description="Total del pedido: subtotal + costo_envio"
    )
    costo_envio: Decimal = Field(
        default=Decimal("50.00"),
        sa_column_kwargs={"nullable": False, "server_default": "50.00"},
        description="Costo de envio flat rate"
    )
    forma_pago_codigo: str = Field(
        foreign_key="formas_pago.codigo",
        nullable=False,
        max_length=20
    )
    direccion_id: Optional[int] = Field(
        foreign_key="direcciones_entrega.id",
        nullable=True
    )
    notas: Optional[str] = Field(default=None)
    # Timestamps from TimestampMixin + SoftDeleteMixin


class DetallePedido(SQLModel, TimestampMixin, table=True):
    """Order line item with immutable price/nombre snapshots"""
    __tablename__ = "detalles_pedido"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False, index=True)
    producto_id: int = Field(foreign_key="productos.id", nullable=False, index=True)
    nombre_snapshot: str = Field(
        max_length=200,
        nullable=False,
        description="Nombre del producto al momento de crear el pedido"
    )
    precio_snapshot: Decimal = Field(
        sa_column_kwargs={"nullable": False},
        description="Precio del producto al momento de crear el pedido"
    )
    cantidad: int = Field(nullable=False, ge=1)
    personalizacion: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Array de IDs de ingredientes removidos"
    )
    # Relationships
    pedido: "Pedido" = Relationship(back_populates="detalles")


class HistorialEstadoPedido(SQLModel, table=True):
    """
    Audit trail for order state transitions.
    APPEND-ONLY: Never UPDATE or DELETE. Managed by PedidoService.
    """
    __tablename__ = "historial_estado_pedido"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", nullable=False, index=True)
    estado_desde: Optional[str] = Field(
        foreign_key="estados_pedido.codigo",
        nullable=True,
        max_length=20,
        description="Estado anterior. NULL = transicion inicial (RN-02)"
    )
    estado_hacia: str = Field(
        foreign_key="estados_pedido.codigo",
        nullable=False,
        max_length=20
    )
    observacion: Optional[str] = Field(default=None)
    usuario_id: Optional[int] = Field(foreign_key="usuarios.id", nullable=True)
    created_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp de la transicion. Append-only: nunca se actualiza"
    )
    # Relationships
    pedido: "Pedido" = Relationship(back_populates="historial")


# Add relationships to Pedido
Pedido.detalles: List["DetallePedido"] = Relationship(
    back_populates="pedido",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"}
)
Pedido.historial: List["HistorialEstadoPedido"] = Relationship(
    back_populates="pedido",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"}
)
```

---

## 4. Schemas Pydantic v2

### 4.1 Request Schemas (`app/modules/pedidos/schemas.py`)

```python
class ItemPedidoRequest(SQLModel):
    """Line item for creating an order"""
    producto_id: int
    cantidad: int = Field(ge=1)
    personalizacion: Optional[List[int]] = None


class CrearPedidoRequest(SQLModel):
    """Request body for POST /pedidos"""
    items: List[ItemPedidoRequest] = Field(min_length=1)
    forma_pago_codigo: str = Field(max_length=20)
    direccion_id: Optional[int] = None
    notas: Optional[str] = None


class ListarPedidosParams(SQLModel):
    """Query params for GET /pedidos"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
```

### 4.2 Response Schemas

```python
class DetallePedidoRead(SQLModel):
    """Order line item response with snapshots"""
    id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    cantidad: int
    personalizacion: Optional[List[int]]
    created_at: datetime


class HistorialEstadoPedidoRead(SQLModel):
    """State transition history record"""
    id: int
    estado_desde: Optional[str]
    estado_hacia: str
    observacion: Optional[str]
    usuario_id: Optional[int]
    created_at: datetime


class PedidoRead(SQLModel):
    """Compact order response for listings"""
    id: int
    estado_codigo: str
    total: Decimal
    costo_envio: Decimal
    created_at: datetime


class PedidoDetail(SQLModel):
    """Full order response with items and history"""
    id: int
    usuario_id: int
    estado_codigo: str
    total: Decimal
    costo_envio: Decimal
    forma_pago_codigo: str
    direccion_id: Optional[int]
    notas: Optional[str]
    detalles: List[DetallePedidoRead]
    historial: List[HistorialEstadoPedidoRead]
    created_at: datetime
    updated_at: datetime


class PedidoListResponse(SQLModel):
    """Paginated order list"""
    items: List[PedidoRead]
    total: int
    skip: int
    limit: int
```

---

## 5. Repositories

### 5.1 PedidoRepository (`app/repositories/pedido_repository.py`)

```python
class PedidoRepository(BaseRepository[Pedido]):
    """Repository for Pedido with custom queries"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Pedido)
    
    async def get_for_user(
        self, usuario_id: int, skip: int, limit: int
    ) -> tuple[List[Pedido], int]:
        """Get orders for a specific user (CLIENT role)"""
        filters = {"usuario_id": usuario_id}
        return await self.list_all(skip=skip, limit=limit, filters=filters)
    
    async def get_all_paginated(
        self, skip: int, limit: int
    ) -> tuple[List[Pedido], int]:
        """Get all orders (ADMIN/PEDIDOS roles)"""
        return await self.list_all(skip=skip, limit=limit)
    
    async def get_detail(self, pedido_id: int) -> Optional[Pedido]:
        """Get order with details and history eagerly loaded"""
        query = (
            select(Pedido)
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.historial)
            )
            .where(Pedido.id == pedido_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    """Repository for order line items"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, DetallePedido)
    
    async def list_by_pedido(self, pedido_id: int) -> List[DetallePedido]:
        """Get all line items for an order"""
        query = select(DetallePedido).where(DetallePedido.pedido_id == pedido_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
```

### 5.2 ProductoRepository — SELECT FOR UPDATE

Extender `ProductoRepository` con metodo `get_for_update`:

```python
async def get_for_update(self, producto_id: int) -> Optional[Producto]:
    """
    Get product with row-level lock for stock validation.
    CRITICAL: Requires PostgreSQL. SQLite does not support SELECT FOR UPDATE.
    
    Uses: SELECT ... FROM productos WHERE id = $1 FOR UPDATE
    """
    query = (
        select(Producto)
        .where(Producto.id == producto_id)
        .with_for_update()
    )
    result = await self.session.execute(query)
    return result.scalar_one_or_none()
```

### 5.3 HistorialRepository — Append-Only

```python
class HistorialEstadoPedidoRepository(BaseRepository[HistorialEstadoPedido]):
    """
    Repository for order state history.
    APPEND-ONLY: Exposes only find and create. NO update/delete.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, HistorialEstadoPedido)
    
    async def list_by_pedido(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """Get history ordered by created_at ASC"""
        query = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    # NOTE: update() and delete() are intentionally NOT implemented
    # This enforces append-only semantics at the repository layer
```

---

## 6. Unit of Work Extendido

### 6.1 Extension (`app/uow.py`)

```python
from app.repositories.pedido_repository import PedidoRepository, DetallePedidoRepository
from app.repositories.historial_repository import HistorialEstadoPedidoRepository

class UnitOfWork:
    def __init__(self, session: AsyncSession):
        # ... existing code ...
        self._pedidos: Optional[PedidoRepository] = None
        self._detalles_pedido: Optional[DetallePedidoRepository] = None
        self._historial_pedido: Optional[HistorialEstadoPedidoRepository] = None
    
    @property
    def pedidos(self) -> PedidoRepository:
        if self._pedidos is None:
            self._pedidos = PedidoRepository(self.session)
        return self._pedidos
    
    @property
    def detalles_pedido(self) -> DetallePedidoRepository:
        if self._detalles_pedido is None:
            self._detalles_pedido = DetallePedidoRepository(self.session)
        return self._detalles_pedido
    
    @property
    def historial_pedido(self) -> HistorialEstadoPedidoRepository:
        if self._historial_pedido is None:
            self._historial_pedido = HistorialEstadoPedidoRepository(self.session)
        return self._historial_pedido
```

---

## 7. Servicio (`app/modules/pedidos/service.py`)

### 7.1 PedidoService — Logica de Negocio

```python
class StockInsufficientError(HTTPException):
    """Raised when product stock is insufficient for the order"""
    def __init__(self, producto_id: int, solicitado: int, disponible: int):
        detail = (
            f"Stock insuficiente para producto ID {producto_id}: "
            f"solicitado {solicitado}, disponible {disponible}"
        )
        super().__init__(status_code=422, detail=detail)


class PaymentMethodNotFoundError(HTTPException):
    """Raised when payment method code is invalid or disabled"""
    def __init__(self, codigo: str):
        detail = f"Forma de pago '{codigo}' no existe o esta deshabilitada"
        super().__init__(status_code=422, detail=detail)


class PedidoService:
    """
    Service layer for order operations.
    Stateless. Receives UoW via dependency injection.
    Does NOT call session.commit() — UoW handles it.
    """
    
    COSTO_ENVIO_DEFAULT = Decimal("50.00")
    ESTADO_INICIAL = "PENDIENTE"
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def crear_pedido(
        self,
        usuario_id: int,
        body: CrearPedidoRequest,
    ) -> Pedido:
        """
        Create order with atomic UoW transaction.
        
        Flow:
        1. Validate address ownership
        2. Validate payment method
        3. Validate stock (SELECT FOR UPDATE)
        4. Calculate totals
        5. Create Pedido + DetallePedido + HistorialEstadoPedido
        6. Commit or rollback handled by UoW context manager
        
        Raises:
            HTTPException 404: Address not found or not owned by user
            HTTPException 422: Payment method invalid, stock insufficient
        """
        # PAS 1: Validar direccion
        if body.direccion_id is not None:
            direccion = await self.uow.direcciones.find(body.direccion_id)
            if direccion is None or direccion.deleted_at is not None:
                raise HTTPException(status_code=404, detail="Direccion no encontrada")
            if direccion.usuario_id != usuario_id:
                raise HTTPException(status_code=404, detail="Direccion no encontrada")
        
        # PASO 2: Validar forma de pago
        forma_pago = await self._get_forma_pago(body.forma_pago_codigo)
        if forma_pago is None or not forma_pago.habilitado:
            raise PaymentMethodNotFoundError(body.forma_pago_codigo)
        
        # PASO 3: Validar stock con SELECT FOR UPDATE
        items_validados = []
        for item in body.items:
            producto = await self.uow.productos.get_for_update(item.producto_id)
            if producto is None or producto.deleted_at is not None:
                raise HTTPException(
                    status_code=422,
                    detail=f"Producto ID {item.producto_id} no encontrado"
                )
            if not producto.disponible:
                raise HTTPException(
                    status_code=422,
                    detail=f"Producto '{producto.nombre}' no esta disponible"
                )
            if producto.stock_cantidad < item.cantidad:
                raise StockInsufficientError(
                    producto_id=item.producto_id,
                    solicitado=item.cantidad,
                    disponible=producto.stock_cantidad
                )
            items_validados.append((item, producto))
        
        # PASO 4: Calcular totales
        subtotal = sum(
            item.cantidad * producto.precio_base
            for item, producto in items_validados
        )
        total = subtotal + self.COSTO_ENVIO_DEFAULT
        
        # PASO 5: Crear Pedido
        pedido = Pedido(
            usuario_id=usuario_id,
            estado_codigo=self.ESTADO_INICIAL,
            total=total,
            costo_envio=self.COSTO_ENVIO_DEFAULT,
            forma_pago_codigo=body.forma_pago_codigo,
            direccion_id=body.direccion_id,
            notas=body.notas,
        )
        pedido = await self.uow.pedidos.create(pedido)
        
        # PASO 6: Crear DetallePedido (con snapshots)
        for item, producto in items_validados:
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                nombre_snapshot=producto.nombre,       # Snapshot!
                precio_snapshot=producto.precio_base, # Snapshot!
                cantidad=item.cantidad,
                personalizacion=item.personalizacion,
            )
            self.uow.session.add(detalle)
        
        # PASO 7: Crear HistorialEstadoPedido inicial
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=None,  # RN-02: transicion inicial
            estado_hacia=self.ESTADO_INICIAL,
            usuario_id=usuario_id,
        )
        self.uow.session.add(historial)
        
        return pedido
    
    async def listar_pedidos(
        self,
        usuario_id: int,
        roles: List[str],
        skip: int,
        limit: int,
    ) -> tuple[List[Pedido], int]:
        """List orders filtered by user for CLIENT, all for ADMIN/PEDIDOS"""
        if "CLIENT" in roles:
            return await self.uow.pedidos.get_for_user(usuario_id, skip, limit)
        return await self.uow.pedidos.get_all_paginated(skip, limit)
    
    async def obtener_detalle(
        self,
        pedido_id: int,
        usuario_id: int,
        roles: List[str],
    ) -> Optional[Pedido]:
        """Get order detail if user owns it (CLIENT) or is ADMIN/PEDIDOS"""
        pedido = await self.uow.pedidos.get_detail(pedido_id)
        if pedido is None or pedido.deleted_at is not None:
            return None
        if "CLIENT" in roles and pedido.usuario_id != usuario_id:
            return None
        return pedido
    
    async def obtener_historial(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """Get state transition history ordered by created_at ASC"""
        return await self.uow.historial_pedido.list_by_pedido(pedido_id)
    
    async def _get_forma_pago(self, codigo: str) -> Optional[FormaPago]:
        """Get payment method by code"""
        return await self.uow.session.get(FormaPago, codigo)
```

---

## 8. Router (`app/modules/pedidos/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.dependencies import get_current_user, require_role
from app.uow import UnitOfWork
from app.modules.pedidos.schemas import (
    CrearPedidoRequest,
    ListarPedidosParams,
    PedidoRead,
    PedidoDetail,
    PedidoListResponse,
    HistorialEstadoPedidoRead,
)
from app.modules.pedidos.service import PedidoService

router = APIRouter(prefix="/pedidos", tags=["pedidos"])
Roles = List[str]


async def get_uow() -> AsyncSession:
    session = await anext(get_session())
    return UnitOfWork(session)


@router.post("", response_model=PedidoRead, status_code=201)
async def crear_pedido(
    body: CrearPedidoRequest,
    current_user: dict = Depends(require_role(["CLIENT", "ADMIN"])),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Create order from cart items.
    
    Atomic UoW transaction: all-or-nothing.
    Validates address, payment method, and stock before committing.
    """
    service = PedidoService(uow)
    pedido = await service.crear_pedido(
        usuario_id=current_user["id"],
        body=body,
    )
    return PedidoRead.model_validate(pedido)


@router.get("", response_model=PedidoListResponse)
async def listar_pedidos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    List orders.
    - CLIENT: only their own orders
    - ADMIN/PEDIDOS: all orders
    """
    service = PedidoService(uow)
    if "CLIENT" in current_user["roles"]:
        pedidos, total = await service.listar_pedidos(
            usuario_id=current_user["id"],
            roles=current_user["roles"],
            skip=skip,
            limit=limit,
        )
    else:
        pedidos, total = await service.listar_pedidos(
            usuario_id=current_user["id"],
            roles=current_user["roles"],
            skip=skip,
            limit=limit,
        )
    return PedidoListResponse(
        items=[PedidoRead.model_validate(p) for p in pedidos],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{pedido_id}", response_model=PedidoDetail)
async def obtener_pedido(
    pedido_id: int,
    current_user: dict = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Get order detail with line items and state history.
    CLIENT can only see their own orders.
    """
    service = PedidoService(uow)
    pedido = await service.obtener_detalle(
        pedido_id=pedido_id,
        usuario_id=current_user["id"],
        roles=current_user["roles"],
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return PedidoDetail.model_validate(pedido)


@router.get("/{pedido_id}/historial", response_model=List[HistorialEstadoPedidoRead])
async def obtener_historial(
    pedido_id: int,
    current_user: dict = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """Get state transition history for an order"""
    service = PedidoService(uow)
    # Validate access
    pedido = await service.obtener_detalle(
        pedido_id=pedido_id,
        usuario_id=current_user["id"],
        roles=current_user["roles"],
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    historial = await service.obtener_historial(pedido_id)
    return [HistorialEstadoPedidoRead.model_validate(h) for h in historial]
```

---

## 9. Migration Alembic

### `migrations/versions/008_add_pedidos_tables.py`

```python
"""Add pedidos, detalles_pedido, historial_estado_pedido tables

Revision ID: 008_add_pedidos_tables
Revises: 007_add_direcciones_table
Create Date: 2026-05-12
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '008_add_pedidos_tables'
down_revision: Union[str, None] = '007_add_direcciones_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabla pedidos
    op.create_table(
        'pedidos',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('estado_codigo', sa.String(20), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('costo_envio', sa.Numeric(10, 2), nullable=False, server_default='50.00'),
        sa.Column('forma_pago_codigo', sa.String(20), nullable=False),
        sa.Column('direccion_id', sa.BigInteger(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_pedidos_usuario_id', 'pedidos', ['usuario_id'])
    op.create_index('ix_pedidos_estado_codigo', 'pedidos', ['estado_codigo'])
    op.create_foreign_key(
        'fk_pedidos_usuario_id', 'pedidos', 'usuarios', ['usuario_id'], ['id']
    )
    op.create_foreign_key(
        'fk_pedidos_estado_codigo', 'pedidos', 'estados_pedido', ['estado_codigo'], ['codigo']
    )
    op.create_foreign_key(
        'fk_pedidos_forma_pago_codigo', 'pedidos', 'formas_pago', ['forma_pago_codigo'], ['codigo']
    )
    op.create_foreign_key(
        'fk_pedidos_direccion_id', 'pedidos', 'direcciones_entrega', ['direccion_id'], ['id']
    )
    
    # Tabla detalles_pedido
    op.create_table(
        'detalles_pedido',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('pedido_id', sa.BigInteger(), nullable=False),
        sa.Column('producto_id', sa.BigInteger(), nullable=False),
        sa.Column('nombre_snapshot', sa.String(200), nullable=False),
        sa.Column('precio_snapshot', sa.Numeric(10, 2), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('personalizacion', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_detalles_pedido_pedido_id', 'detalles_pedido', ['pedido_id'])
    op.create_index('ix_detalles_pedido_producto_id', 'detalles_pedido', ['producto_id'])
    op.create_foreign_key(
        'fk_detalles_pedido_pedido_id', 'detalles_pedido', 'pedidos', ['pedido_id'], ['id']
    )
    op.create_foreign_key(
        'fk_detalles_pedido_producto_id', 'detalles_pedido', 'productos', ['producto_id'], ['id']
    )
    
    # Tabla historial_estado_pedido (append-only audit trail)
    op.create_table(
        'historial_estado_pedido',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('pedido_id', sa.BigInteger(), nullable=False),
        sa.Column('estado_desde', sa.String(20), nullable=True),
        sa.Column('estado_hacia', sa.String(20), nullable=False),
        sa.Column('observacion', sa.Text(), nullable=True),
        sa.Column('usuario_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_historial_pedido_id', 'historial_estado_pedido', ['pedido_id'])
    op.create_foreign_key(
        'fk_historial_pedido_pedido_id', 'historial_estado_pedido', 'pedidos', ['pedido_id'], ['id']
    )
    op.create_foreign_key(
        'fk_historial_estado_desde', 'historial_estado_pedido', 'estados_pedido', ['estado_desde'], ['codigo']
    )
    op.create_foreign_key(
        'fk_historial_estado_hacia', 'historial_estado_pedido', 'estados_pedido', ['estado_hacia'], ['codigo']
    )


def downgrade() -> None:
    op.drop_table('historial_estado_pedido')
    op.drop_table('detalles_pedido')
    op.drop_table('pedidos')
```

---

## 10. Tests de Integracion

**IMPORTANTE**: Los tests de pedidos DEBEN usar PostgreSQL porque requieren `SELECT FOR UPDATE`, que no esta soportado por SQLite.

### 10.1 Conftest — Fixtures

```python
import pytest

# Mark all tests in this module to require PostgreSQL
pytestmark = pytest.mark.postgres


@pytest.fixture
async def pg_session(postgres_db):
    """PostgreSQL session for SELECT FOR UPDATE tests"""
    async with postgres_db.session() as session:
        yield session
```

### 10.2 Test: Crear Pedido Exitoso

```python
@pytest.mark.postgres
class TestCrearPedido:
    
    async def test_crear_pedido_exitoso(
        self, client, pg_session, auth_headers, producto_fixture
    ):
        """Test: order created atomically with snapshots"""
        # Given: authenticated user, product with stock
        producto = producto_fixture
        body = {
            "items": [
                {
                    "producto_id": producto.id,
                    "cantidad": 2,
                    "personalizacion": None
                }
            ],
            "forma_pago_codigo": "MERCADOPAGO",
            "direccion_id": None,
        }
        
        # When: POST /pedidos
        response = client.post(
            "/api/v1/pedidos",
            json=body,
            headers=auth_headers,
        )
        
        # Then: 201 + PedidoRead
        assert response.status_code == 201
        data = response.json()
        assert data["estado_codigo"] == "PENDIENTE"
        assert data["total"] > 0
        assert data["costo_envio"] == 50.00
        
        # And: Pedido exists in DB
        pedido = await pg_session.get(Pedido, data["id"])
        assert pedido is not None
        assert pedido.usuario_id == auth_headers["user_id"]
        
        # And: DetallePedido has snapshots
        detalles = await DetallePedidoRepository(pg_session).list_by_pedido(pedido.id)
        assert len(detalles) == 1
        assert detalles[0].nombre_snapshot == producto.nombre
        assert detalles[0].precio_snapshot == producto.precio_base
        
        # And: HistorialEstadoPedido with estado_desde=NULL
        historial = await HistorialEstadoPedidoRepository(pg_session).list_by_pedido(pedido.id)
        assert len(historial) == 1
        assert historial[0].estado_desde is None
        assert historial[0].estado_hacia == "PENDIENTE"
    
    async def test_stock_insuficiente_rollback(
        self, client, pg_session, auth_headers, producto_fixture
    ):
        """Test: order NOT created when stock insufficient"""
        producto = producto_fixture
        body = {
            "items": [
                {
                    "producto_id": producto.id,
                    "cantidad": producto.stock_cantidad + 100,  # Exceeds stock
                }
            ],
            "forma_pago_codigo": "MERCADOPAGO",
        }
        
        # When: POST /pedidos
        response = client.post(
            "/api/v1/pedidos",
            json=body,
            headers=auth_headers,
        )
        
        # Then: 422 with stock error
        assert response.status_code == 422
        assert "Stock insuficiente" in response.json()["detail"]
        
        # And: NO pedido created in DB
        pedidos_count = await pg_session.execute(
            select(func.count()).select_from(Pedido)
            .where(Pedido.usuario_id == auth_headers["user_id"])
        )
        assert pedidos_count.scalar() == 0
    
    async def test_forma_pago_invalida_422(
        self, client, pg_session, auth_headers, producto_fixture
    ):
        """Test: 422 when payment method invalid or disabled"""
        body = {
            "items": [{"producto_id": producto_fixture.id, "cantidad": 1}],
            "forma_pago_codigo": "INVALIDO",
        }
        
        response = client.post(
            "/api/v1/pedidos",
            json=body,
            headers=auth_headers,
        )
        
        assert response.status_code == 422
        assert "Forma de pago" in response.json()["detail"]
    
    async def test_direccion_no_pertenece_al_usuario_404(
        self, client, pg_session, auth_headers, producto_fixture, otra_direccion_fixture
    ):
        """Test: 404 when address belongs to another user"""
        body = {
            "items": [{"producto_id": producto_fixture.id, "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
            "direccion_id": otra_direccion_fixture.id,  # Belongs to different user
        }
        
        response = client.post(
            "/api/v1/pedidos",
            json=body,
            headers=auth_headers,
        )
        
        assert response.status_code == 404
```

---

## 11. Registro en main.py

```python
# app/main.py
from app.modules.pedidos.router import router as pedidos_router

app.include_router(pedidos_router, prefix="/api/v1")
```

---

## 12. Checklist de Implementacion

- [ ] Crear migration `008_add_pedidos_tables.py`
- [ ] Crear modelos `Pedido`, `DetallePedido`, `HistorialEstadoPedido`
- [ ] Extender `ProductoRepository` con `get_for_update()`
- [ ] Crear `PedidoRepository` y `DetallePedidoRepository`
- [ ] Crear `HistorialEstadoPedidoRepository` (solo create + find)
- [ ] Extender `UnitOfWork` con properties `pedidos`, `detalles_pedido`, `historial_pedido`
- [ ] Crear schemas en `app/modules/pedidos/schemas.py`
- [ ] Crear `PedidoService` en `app/modules/pedidos/service.py`
- [ ] Crear router en `app/modules/pedidos/router.py`
- [ ] Registrar router en `main.py`
- [ ] Crear tests de integracion con `pytest.mark.postgres`
- [ ] Ejecutar `alembic upgrade head`
- [ ] Verificar con queries SQL directas en `food_store_db`

---

**Generado**: 2026-05-12 | **Change**: change-09-order-creation-uow | **Metodologia**: SDD
