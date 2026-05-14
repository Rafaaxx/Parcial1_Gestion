"""Pago model — MercadoPago payment entity with idempotency support"""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class Pago(BaseModel, table=True):
    """
    Payment entity for MercadoPago integration.

    Features:
    - pedido_id: FK to order being paid (CASCADE delete)
    - mp_payment_id: MercadoPago payment ID (unique, nullable until created)
    - mp_status: MP status (pending, approved, rejected, in_process, etc.)
    - mp_status_detail: detailed status from MP
    - external_reference: UUID of the order (for MP reference)
    - idempotency_key: unique key to prevent duplicate charges
    - monto: payment amount (DECIMAL 10,2)
    - Soft-delete support (deleted_at from BaseModel)
    - Timestamps (created_at, updated_at from BaseModel)
    - Relationship to Pedido

    Business rules:
    - RN-01: idempotency_key must be unique (prevent duplicate payments)
    - RN-02: mp_payment_id is set only after successful MP API call
    - RN-03: Only one unpaid payment per order (enforced at service layer)
    """

    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(
        foreign_key="pedidos.id",
        nullable=False,
        index=True,
        description="Pedido que se esta pagando (CASCADE)",
    )
    mp_payment_id: Optional[int] = Field(
        default=None,
        unique=True,
        description="ID del pago en MercadoPago (nullable hasta que se crea)",
    )
    mp_status: str = Field(
        max_length=30,
        default="pending",
        description="Estado del pago en MP: pending, approved, rejected, in_process, cancelled, refunded",
    )
    mp_status_detail: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Detalle del estado desde MP",
    )
    external_reference: str = Field(
        max_length=100,
        nullable=False,
        description="UUID del pedido como referencia externa para MP",
    )
    idempotency_key: str = Field(
        max_length=100,
        unique=True,
        nullable=False,
        description="Clave de idempotencia para prevenir cobros duplicados",
    )
    monto: Decimal = Field(
        default=Decimal("0.00"),
        sa_column_kwargs={"nullable": False},
        description="Monto del pago (DECIMAL 10,2)",
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    pedido: "Pedido" = Relationship(
        back_populates="pagos",
        sa_relationship_kwargs={
            "foreign_keys": "[Pago.pedido_id]",
        },
    )


# Back-populates from Pedido model
# This is handled in pedido.py when it imports Pago
