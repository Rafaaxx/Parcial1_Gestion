"""EstadoPedido model — FSM states catalog"""

from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class EstadoPedido(TimestampMixin, SQLModel, table=True):
    __tablename__ = "estados_pedido"
    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=100)
    orden: int = Field(default=0)
    es_terminal: bool = Field(default=False)
    pedidos: List["Pedido"] = Relationship(
        back_populates="estado",
        sa_relationship_kwargs={
            "foreign_keys": "[Pedido.estado_codigo]",
        },
    )
