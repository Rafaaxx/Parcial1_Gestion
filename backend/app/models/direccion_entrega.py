"""DireccionEntrega model — delivery addresses for users with soft delete"""

from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import BaseModel

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.usuario import Usuario


class DireccionEntrega(BaseModel, table=True):
    """
    Delivery address for a user.

    Features:
    - Foreign key to usuarios table (ownership)
    - Optional alias (e.g. "Casa", "Trabajo")
    - Principal address flag (only one per user, enforced by partial unique index)
    - Soft-delete support (deleted_at from BaseModel)
    - Timestamps (created_at, updated_at from BaseModel)
    """

    __tablename__ = "direcciones_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(
        foreign_key="usuarios.id",
        nullable=False,
        description="ID del usuario propietario de la dirección",
    )
    alias: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Alias opcional: 'Casa', 'Trabajo', etc. (max 50 chars)",
    )
    linea1: str = Field(
        nullable=False,
        max_length=500,
        description="Dirección completa (calle, número, ciudad, etc.)",
    )
    es_principal: bool = Field(
        default=False,
        nullable=False,
        description="Indica si es la dirección predeterminada del usuario",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    usuario: Optional["Usuario"] = Relationship(
        back_populates="direcciones",
    )
    pedidos: List["Pedido"] = Relationship(back_populates="direccion")
