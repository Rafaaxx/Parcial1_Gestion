"""Pedido, DetallePedido, HistorialEstadoPedido models — order domain with snapshot pattern and audit trail"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime, func, JSON
from sqlalchemy.dialects.postgresql import JSONB

from app.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.producto import Producto
    from app.models.estado_pedido import EstadoPedido
    from app.models.forma_pago import FormaPago
    from app.models.direccion_entrega import DireccionEntrega


class Pedido(BaseModel, table=True):
    """
    Order entity capturing a customer's cart checkout.

    Features:
    - usuario_id: owner of the order (client who placed it)
    - estado_codigo: FSM current state (FK -> estados_pedido)
    - total: total = subtotal + costo_envio (DECIMAL, immutable after creation)
    - costo_envio: flat shipping rate (DECIMAL, default 50.00, captured at creation)
    - forma_pago_codigo: payment method (FK -> formas_pago)
    - direccion_id: delivery address (FK -> direcciones_entrega, SET NULL if deleted)
    - notas: optional customer notes
    - Soft-delete support (deleted_at from BaseModel)
    - Timestamps (created_at, updated_at from BaseModel)
    - Relationships to detalles_pedido and historial_estado_pedido

    Snapshot semantics:
    - costo_envio is captured at creation time and never changes
    - DetallePedido records hold nombre_snapshot and precio_snapshot
    """
    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(
        foreign_key="usuarios.id",
        nullable=False,
        index=True,
        description="ID del usuario que realizo el pedido",
    )
    estado_codigo: str = Field(
        foreign_key="estados_pedido.codigo",
        nullable=False,
        max_length=20,
        index=True,
        description="Estado actual del FSM (FK -> estados_pedido.codigo)",
    )
    total: Decimal = Field(
        sa_column_kwargs={
            "nullable": False,
            "server_default": "0.00",
        },
        description="Total del pedido: subtotal + costo_envio (DECIMAL 10,2)",
    )
    costo_envio: Decimal = Field(
        default=Decimal("50.00"),
        sa_column_kwargs={
            "nullable": False,
            "server_default": "50.00",
        },
        description="Costo de envio flat rate capturado al crear el pedido",
    )
    forma_pago_codigo: str = Field(
        foreign_key="formas_pago.codigo",
        nullable=False,
        max_length=20,
        description="Forma de pago elegida (FK -> formas_pago.codigo)",
    )
    direccion_id: Optional[int] = Field(
        foreign_key="direcciones_entrega.id",
        nullable=True,
        description="Direccion de entrega (NULL = retiro en local)",
    )
    notas: Optional[str] = Field(
        default=None,
        description="Notas opcionales del cliente para el pedido",
    )

    # ── Relationships ────────────────────────────────────────────────────────

    usuario: Optional["Usuario"] = Relationship(back_populates="pedidos")
    estado: "EstadoPedido" = Relationship(
        back_populates="pedidos",
        sa_relationship_kwargs={
            "foreign_keys": "[Pedido.estado_codigo]",
        },
    )
    forma_pago: "FormaPago" = Relationship(
        back_populates="pedidos",
        sa_relationship_kwargs={
            "foreign_keys": "[Pedido.forma_pago_codigo]",
        },
    )
    detalles: List["DetallePedido"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[DetallePedido.pedido_id]",
        },
    )
    historial: List["HistorialEstadoPedido"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[HistorialEstadoPedido.pedido_id]",
        },
    )
    direccion: Optional["DireccionEntrega"] = Relationship(
        back_populates="pedidos",
    )


class DetallePedido(SQLModel, table=True):
    """
    Order line item with immutable snapshots.

    Captures the product name and price at the moment of order creation.
    Even if the product is renamed or price changes, this record keeps
    the historical values (RN-04: Snapshot Pattern).

    Features:
    - nombre_snapshot: product name captured at creation (immutable)
    - precio_snapshot: product price captured at creation (immutable)
    - cantidad: requested quantity
    - personalizacion: JSON array of ingredient IDs removed by customer
    - Timestamps (created_at only, no updated_at)
    """
    __tablename__ = "detalles_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(
        foreign_key="pedidos.id",
        nullable=False,
        index=True,
        description="Pedido padre",
    )
    producto_id: int = Field(
        foreign_key="productos.id",
        nullable=False,
        index=True,
        description="Producto ordenad",
    )
    nombre_snapshot: str = Field(
        max_length=200,
        nullable=False,
        description="Nombre del producto capturado al crear el pedido (snapshot inmutable)",
    )
    precio_snapshot: Decimal = Field(
        sa_column_kwargs={"nullable": False},
        description="Precio del producto capturado al crear el pedido (snapshot inmutable)",
    )
    cantidad: int = Field(
        nullable=False,
        ge=1,
        description="Cantidad solicitada (>= 1)",
    )
    personalizacion: Optional[List[int]] = Field(
        default=None,
        sa_type=JSON,
        sa_column_kwargs={"nullable": True},
        description="Array de IDs de ingredientes removidos por el cliente",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
        },
        description="Timestamp de creacion de la linea",
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    pedido: "Pedido" = Relationship(back_populates="detalles")
    producto: Optional["Producto"] = Relationship(
        back_populates="detalles_pedido",
        sa_relationship_kwargs={
            "foreign_keys": "[DetallePedido.producto_id]",
        },
    )


class HistorialEstadoPedido(SQLModel, table=True):
    """
    Audit trail for order state transitions (append-only).

    Every state transition creates a new record here. This table is
    APPEND-ONLY: no UPDATE or DELETE operations are ever performed
    on this table. Enforcement is at the repository layer (no update/delete
    methods) and at the database level (triggers recommended).

    Features:
    - estado_desde: previous state (NULL = initial transition, per RN-02)
    - estado_hacia: new state after transition
    - observacion: optional note from the user/admin
    - usuario_id: user who performed the transition (NULL for system transitions)
    - created_at: timestamp of transition (never updated)

    Business rules enforced:
    - RN-02: First record has estado_desde = NULL
    - RN-03: Append-only (no UPDATE/DELETE)
    """
    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(
        foreign_key="pedidos.id",
        nullable=False,
        index=True,
        description="Pedido al que pertenece esta transicion",
    )
    estado_desde: Optional[str] = Field(
        foreign_key="estados_pedido.codigo",
        nullable=True,
        max_length=20,
        description="Estado anterior (NULL = transicion inicial, RN-02)",
    )
    estado_hacia: str = Field(
        foreign_key="estados_pedido.codigo",
        nullable=False,
        max_length=20,
        description="Estado nuevo despues de la transicion",
    )
    observacion: Optional[str] = Field(
        default=None,
        description="Nota opcional sobre la transicion",
    )
    usuario_id: Optional[int] = Field(
        foreign_key="usuarios.id",
        nullable=True,
        description="Usuario que realizo la transicion (NULL = sistema)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
        },
        description="Timestamp de la transicion (append-only, nunca se actualiza)",
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    pedido: "Pedido" = Relationship(back_populates="historial")


# ── Add back-populates to existing models ────────────────────────────────────

# EstadoPedido back_populates
if "EstadoPedido" in dir():
    pass  # Will be set after import

if "Producto" in dir():
    pass  # Will be set after import
