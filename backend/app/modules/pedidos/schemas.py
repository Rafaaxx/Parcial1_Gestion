"""Pydantic schemas for Pedido module — request/response validation"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlmodel import SQLModel, Field


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
    estado_codigo: str
    total: Decimal
    costo_envio: Decimal
    created_at: datetime


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


class PedidoListResponse(SQLModel):
    """Paginated order list response."""
    items: List[PedidoRead]
    total: int
    skip: int
    limit: int
