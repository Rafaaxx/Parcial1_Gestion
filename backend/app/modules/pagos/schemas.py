"""Pydantic schemas for Pagos module — MercadoPago integration"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class PagoCreate(SQLModel):
    """
    Request body for creating a MercadoPago payment.

    Used by POST /api/v1/pagos/crear
    """

    pedido_id: int = Field(description="ID del pedido a pagar")
    card_token: Optional[str] = Field(
        default=None,
        description="Token de tarjeta generado por SDK frontend (PCI-compliant)",
    )


class PagoCreateResponse(SQLModel):
    """
    Response after successfully creating a payment.

    Returns init_point for redirect to MP checkout or status directly.
    """

    mp_payment_id: Optional[int] = Field(
        default=None,
        description="ID del pago en MercadoPago (null si es checkout redirect)",
    )
    status: str = Field(description="Estado inicial del pago en MP")
    init_point: Optional[str] = Field(
        default=None,
        description="URL de redirección al checkout de MP (si aplica)",
    )
    external_reference: str = Field(description="UUID del pedido")
    monto: Decimal = Field(description="Monto del pago")


class PagoResponse(SQLModel):
    """
    Response for getting payment details.

    Used by GET /api/v1/pagos/{pedido_id}
    """

    id: int
    pedido_id: int
    mp_payment_id: Optional[int]
    mp_status: str
    mp_status_detail: Optional[str]
    external_reference: str
    idempotency_key: str
    monto: Decimal
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class WebhookPayload(SQLModel):
    """
    Payload received from MercadoPago webhook (IPN).

    The real validation happens by querying MP API with this topic/resource.
    This schema is for documentation and optional initial validation.
    """

    topic: str = Field(description="Tipo de notificación (payment, plan, etc.)")
    resource: Optional[str] = Field(
        default=None,
        description="ID del recurso en MP (deprecated, usar action_id)",
    )
    action_id: Optional[str] = Field(
        default=None,
        description="ID de la acción del webhook",
    )


class WebhookResponse(SQLModel):
    """Response from webhook endpoint."""

    message: str = Field(description="Mensaje de procesamiento")
    processed: bool = Field(description="Si el webhook fue procesado correctamente")
