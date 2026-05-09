"""EstadoPedido model — FSM states catalog"""
from sqlmodel import SQLModel, Field
from typing import Optional
from app.models.mixins import TimestampMixin


class EstadoPedido(TimestampMixin, SQLModel, table=True):
    __tablename__ = "estados_pedido"
    codigo: str = Field(primary_key=True, max_length=20)
    descripcion: str = Field(max_length=100)
    orden: int = Field(default=0)
    es_terminal: bool = Field(default=False)
