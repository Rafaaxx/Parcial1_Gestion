"""Pydantic schemas for Pedido module — request/response validation"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlmodel import Field, SQLModel


class ItemPedidoRequest(SQLModel):
    """Line item for creating an order."""

    producto_id: int = Field(description="Product ID to order")
    cantidad: int = Field(ge=1, description="Quantity to order (>= 1)")
    personalizacion: Optional[List[int]] = Field(
        default=None,
        description="List of ingredient IDs to remove from this item",
    )


class CrearPedidoRequest(SQLModel):
    """Request body for POST /api/v1/pedidos."""

    items: List[ItemPedidoRequest] = Field(
        min_length=1,
        description="At least one item required",
    )
    forma_pago_codigo: str = Field(
        max_length=20,
        description="Payment method code (e.g. MERCADOPAGO, EFECTIVO, TRANSFERENCIA)",
    )
    direccion_id: Optional[int] = Field(
        default=None,
        description="Delivery address ID (NULL = pickup at location)",
    )
    notas: Optional[str] = Field(
        default=None,
        description="Optional customer notes for the order",
    )


class DetallePedidoRead(SQLModel):
    """Order line item response with immutable snapshots."""

    id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    cantidad: int
    personalizacion: Optional[List[int]]
    created_at: datetime


class ClienteInfo(SQLModel):
    """Customer info for order list endpoints."""

    id: int
    nombre: Optional[str]
    email: str


class HistorialEstadoPedidoRead(SQLModel):
    """State transition history record."""

    id: int
    estado_desde: Optional[str]
    estado_hacia: str
    observacion: Optional[str]
    usuario_id: Optional[int]
    created_at: datetime


class PedidoRead(SQLModel):
    """Compact order response for list endpoints."""

    id: int
    usuario_id: int
    estado_codigo: str
    total: Decimal
    costo_envio: Decimal
    created_at: datetime
    cliente: Optional[ClienteInfo] = None


class PedidoDetail(SQLModel):
    """Full order response with line items, history, and address."""

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
    cliente: Optional[ClienteInfo] = None


class PedidoListResponse(SQLModel):
    """Paginated order list response."""

    items: List[PedidoRead]
    total: int
    skip: int
    limit: int


class AvanzarEstadoRequest(SQLModel):
    """
    Request body for transitioning order state.

    Required for PATCH /pedidos/{id}/estado
    """

    nuevo_estado: str = Field(
        max_length=20,
        description="Target state code (e.g., CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO)",
    )
    motivo: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Explanation for the transition (required for CANCELADO)",
    )


class TransicionResponse(SQLModel):
    """Response for state transition."""

    id: int
    estado_codigo: str
    mensaje: str = "Estado actualizado correctamente"
