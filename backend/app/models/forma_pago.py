"""FormaPago model — payment methods catalog"""

from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class FormaPago(TimestampMixin, SQLModel, table=True):
    __tablename__ = "formas_pago"
    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=100)
    habilitado: bool = Field(default=True)
    pedidos: List["Pedido"] = Relationship(
        back_populates="forma_pago",
        sa_relationship_kwargs={
            "foreign_keys": "[Pedido.forma_pago_codigo]",
        },
    )
